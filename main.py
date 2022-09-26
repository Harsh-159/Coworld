import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import folium_static
import json
import copy
import csv



def url_to_dict(url):
    URL = "https://www.worldometers.info/coronavirus/"
    URL=url
    r = requests.get(URL)
    
    soup = BeautifulSoup(r.content, 'html5lib') 
    number = soup.find_all("a", {"class": "mt_a"})

    table = soup.find('table', attrs={'id':'main_table_countries_today'})
    table_body = table.find('tbody')

    rows = table_body.find_all('tr')
    country_values={}
    all_continents=["Oceania","Asia","Europe","North America","South America","Africa","Australia","Antarctica","World",'Australia/Oceania']
    countries=''
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        
        dummy=[]
        for ele in cols:
            ele=str(ele)
            if ele[:4]=="Cura":
                break
            if ele!='':
                if all(chr.isalpha() or chr.isspace() for chr in ele) or ele=="Australia/Oceania":
                    if ele in dummy or ele in all_continents:
                        break
                dummy.append(ele)
            else:
                dummy.append('0')
        if len(dummy)>2:
            d2=dummy[1]
            dummy=dummy[2:]
            dummy=dummy[:13]
            dummy = list(map(lambda x: x.replace('N/A', '0'), dummy))
            dummy=list(map(lambda x:int(x.replace(',','')),dummy))
            if all(chr.isalpha() or chr.isspace() for chr in d2):
                country_values[d2]=dummy
    return country_values

def dict_to_csv(dict):
    country_values=dict

    with open('values.csv', 'w',newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Number","Country", 'Total_Cases', 'New_Cases', 'Total_Deths','New_Death','Total_Recovered','New_Recovered','Active_Cases','Serious_Critical','Total_Cases_per_million','Total_death_per_million','Total_Tests','Tests_per_million','Population'])
        i=1
        for x in country_values:
            arr=[i,x]
            arr.extend(country_values[x])
            writer.writerow(arr)
            i+=1
    file.close()

def geojson_with_values(dict):
    country_values=dict
    all_fields=['Total_Cases', 'New_Cases', 'Total_Deths','New_Death','Total_Recovered','New_Recovered','Active_Cases','Serious_Critical','Total_Cases_per_million','Total_death_per_million','Total_Tests','Tests_per_million','Population']
    with open('countries.geojson', 'r') as f:
        data = json.load(f)

    for feat in data['features']:
        if feat['properties']['ADMIN'] in country_values:
            if len(country_values[feat['properties']['ADMIN']])==13:
                for i in range(13):
                    feat['properties'].update({all_fields[i]:country_values[feat['properties']['ADMIN']][i]})

    with open('new.geojson', 'w') as f:
        json.dump(data, f)


def set_streamlib():
    st.set_page_config(layout ="wide")
    json1=f'new.geojson'

    m = folium.Map(location=[23.47,77.94], tiles='CartoDB positron', name="Light Map",
                zoom_start=1, attr="My Data attribution")

    world_covid = f"values.csv"
    world_covid_data = pd.read_csv(world_covid,encoding='latin1')

    choice = ['Total_Cases', 'New_Cases', 'Total_Deths', 'New_Death', 'Total_Recovered', 'New_Recovered', 'Active_Cases', 'Serious_Critical', 'Total_Cases_per_million', 'Total_death_per_million', 'Total_Tests', 'Tests_per_million', 'Population']
    choice_selected = st.selectbox("Select choice", choice)

    folium.Choropleth(
        geo_data=json1,
        name="choropleth",
        data=world_covid_data,
        columns=["Country",choice_selected],
        key_on="feature.properties.ADMIN",
        fill_color="YlOrRd",
        fill_opacity=0.7,
        line_opacity=.1,
        legend_name=choice_selected
    ).add_to(m)

    folium.features.GeoJson('new.geojson',name="Country",popup=folium.features.GeoJsonPopup(fields=[choice_selected])).add_to(m)

    folium_static(m, width=1000, height=650)



site_url="https://www.worldometers.info/coronavirus/"
country_values=url_to_dict(site_url)
dict_to_csv(country_values)
geojson_with_values(country_values)
set_streamlib()
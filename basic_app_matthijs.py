import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

pd.options.display.max_rows = 999
pd.set_option('display.width', 1000)       
pd.set_option('display.max_columns', None)  

def get_population_data(country_name):
    url = f"https://api.api-ninjas.com/v1/population?country={country_name}"
    headers = {"X-Api-Key": "WXpLhqoFwtWNQK/4yBAnLQ==Dr4y3QC5e0OOcSpn"} 
    response = requests.get(url, headers=headers)

    hist_df = pd.DataFrame()
    if response.status_code == 200:
        data = response.json()  
        
        hist_df = pd.DataFrame(data.get('historical_population', []))
        if not hist_df.empty:
            hist_df = hist_df.set_index('year')
            hist_df.rename(columns={'population': 'historical_population'}, inplace=True)
    
        forecast_df = pd.DataFrame(data.get('population_forecast', []))
        if not forecast_df.empty:
            forecast_df = forecast_df.set_index('year')
            forecast_df.rename(columns={'population': 'population_forecast'}, inplace=True)
  
        top_level_fields = {k: v for k, v in data.items() if k not in ['historical_population', 'population_forecast']}
        for key, value in top_level_fields.items():
            hist_df[key] = value
        
        for col in hist_df.columns:
            if '.' in col: 
                base_col = col.split('.')[0]
                hist_df[base_col] = hist_df[base_col].combine_first(hist_df[col])
                hist_df = hist_df.drop(columns=[col])
        
        key_cols = ['historical_population', 'median_age', 'fertility_rate', 'rank']
        hist_df = hist_df.dropna(subset=key_cols, how='all')
        hist_df = hist_df.sort_index()
        
        print(hist_df[['historical_population', 'median_age', 'fertility_rate', 'country_name']])
    else:
        print(f"Error: {response.status_code}, {response.text}")

    #api voor GDP
    url1 = f"https://api.api-ninjas.com/v1/gdp?country={country_name}"
    headers1 = {"X-Api-Key": "WXpLhqoFwtWNQK/4yBAnLQ==Dr4y3QC5e0OOcSpn"} 
    response1 = requests.get(url1, headers=headers1)

    if response1.status_code == 200:
        data1 = response1.json() 
        hist_df1 = pd.DataFrame(data1)
        print(hist_df1)
    else:
        print(f"Error: {response1.status_code}, {response1.text}")

    return hist_df


# ✅ gebruik:
country_name = 'USA'
hist_df = get_population_data(country_name)

#Plots enzovoort maken
fig = px.line(
            hist_df,
            x=hist_df.index,
            y='historical_population',
            title=f'Historical Population of {country_name}',
            labels={'x': 'Year', 'historical_population': 'Population'}
        )
fig.update_traces(mode='lines+markers')

fig.show()

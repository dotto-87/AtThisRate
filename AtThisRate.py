import numpy as np
import pandas as pd
import datetime as dt

covid_df = pd.read_csv("https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv")

jour = dt.date.today()
jour_1s = jour - dt.timedelta(weeks=1)
jour_3s = jour - dt.timedelta(weeks=3)


def GetLatest(loc, date, lookup):
    df = covid_df[covid_df['location'] == loc]
    df = df[['date',lookup]]
    value = list()
    value1 = ""
    value2 = np.nan
    while date > dt.date(2021,1,1) and np.isnan(value2):
        value = df[df['date'] == date.strftime("%Y-%m-%d")].values.tolist()
        try:
            value1 = value[0][0]
        except:
            value1 = ""
        try:
            value2 = value[0][1]
        except:
            value2 = np.nan
        date = date - dt.timedelta(days=1)
    value = [value1, value2] 
    return value

result = pd.DataFrame(columns=['Country','Current %','Reach 50%','Reach 60%','Reach 70%','Reach 80%'])

i = 1
nodepays = (len(covid_df['location'].unique()))

for pays in covid_df['location'].unique():
 try:
    vaxxed = GetLatest(pays,jour,'people_fully_vaccinated')
    jour_ref = dt.datetime.strptime(vaxxed[0],"%Y-%m-%d")
    vaxxed_today = vaxxed[1]
    vaxxed_period = GetLatest(pays,jour_1s,'people_fully_vaccinated')[1] - \
        GetLatest(pays,jour_3s,'people_fully_vaccinated')[1]
    period_start = dt.datetime.strptime(GetLatest(pays,jour_3s,'people_fully_vaccinated')[0], '%Y-%m-%d')
    period_end = dt.datetime.strptime(GetLatest(pays,jour_1s,'people_fully_vaccinated')[0], '%Y-%m-%d')
    period_days = period_end - period_start
    vaxxed_per_day = vaxxed_period / period_days.days

    population = GetLatest(pays,jour,'population')[1]

    vaxxed_rate = vaxxed_today / population

    jour50 = np.nan
    jour60 = np.nan
    jour70 = np.nan
    jour80 = np.nan

    if vaxxed_rate < 0.8:
        jour80 = jour_ref + dt.timedelta(days=(((population * 0.8)-vaxxed_today)/vaxxed_per_day))
        jour80 = jour80.date()
        if vaxxed_rate < 0.7:
            jour70 = jour_ref + dt.timedelta(days=(((population * 0.7)-vaxxed_today)/vaxxed_per_day))
            jour70 = jour70.date()
            if vaxxed_rate < 0.6:
                jour60 = jour_ref + dt.timedelta(days=(((population * 0.6)-vaxxed_today)/vaxxed_per_day))
                jour60 = jour60.date()
                if vaxxed_rate < 0.5:
                    jour50 = jour_ref + dt.timedelta(days=(((population * 0.5)-vaxxed_today)/vaxxed_per_day))
                    jour50 = jour50.date()
    
     

    result_row = pd.DataFrame([{
        'Country': pays,
        'Current %': vaxxed_rate,
        'Reach 50%': jour50,
        'Reach 60%': jour60,
        'Reach 70%': jour70,
        'Reach 80%': jour80
        }])
        


 except:
    result_row = pd.DataFrame([{
        'Country': pays + ' (no data)',
        'Current %': np.nan,
        'Reach 50%': np.nan,
        'Reach 60%': np.nan,
        'Reach 70%': np.nan,
        'Reach 80%': np.nan
        }])    
 

 result = pd.concat([result,result_row])
 print(f"{int(i / nodepays*100)}%", end='\r')
 i = i + 1


result.set_index('Country').to_csv('AtThisRate.csv',date_format='%Y-%m-%d')
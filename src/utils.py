import pandas as pd

def calc_popularity(data):
    df = data.copy()
    counts = df['pageTitle'].value_counts()
    df['pageVisits'] = df['pageTitle'].apply(lambda x: counts[x])
    return df

def calc_freshness(data):
    df = data.copy()
    data.sort_values(by=['pageTitle', 'time'], inplace=True)
    first_time = data.groupby('pageTitle').first()['time']
    df['freshness'] = df['pageTitle'].apply(lambda x: first_time[x])
    df['diff'] = df['time'] - df['freshness']
    df['freshness'] = df['diff'].apply(lambda x: x.seconds/3600) # in hours
    del df['diff']
    df.reset_index(inplace=True, drop=True)
    return df

def take_first_click(data):
    df = data.copy()
    df.sort_values(by=['visitor', 'pageTitle', 'time'], inplace=True)
    df.reset_index(drop=True, inplace=True)
    df = df.groupby(['visitor', 'pageTitle']).first().reset_index()
    return df

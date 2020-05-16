import pandas as pd

def calc_popularity(data):
    df = data.copy()
    counts = df['pageTitle'].value_counts()
    df['pageVisits'] = df['pageTitle'].apply(lambda x: counts[x])
    return df
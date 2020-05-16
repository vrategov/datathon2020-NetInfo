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

def cos_sim(mat):
    cosine = cosine_similarity(mat)
    np.fill_diagonal(cosine, 0 )
    similarity_users =pd.DataFrame(cosine,index=mat.index)
    similarity_users.columns=mat.index
    return similarity_users

def find_n_neighbours(similarity,n):
    order = np.argsort(similarity.values, axis=1)[:, :n]
    similarity = similarity.apply(lambda x: pd.Series(x.sort_values(ascending=False).iloc[:n].index, 
          index=['top{}'.format(i) for i in range(1, n+1)]), axis=1)
    return similarity

def User_item_score(user, df, mat, neighbours,similarity):
    articles_read_by_user = mat.columns[mat.iloc[user,:]>0].tolist()
    a = neighbours[neighbours.index==user].values.squeeze().tolist()
    neighbours_articles = df[df.visitor_label.isin(a)]['page_label'].unique()
    aritcles_for_consideration = list(set(neighbours_articles)-set(articles_read_by_user))
    score = []
    for item in aritcles_for_consideration:
        c = mat.loc[:,item]
        d = c[c.index.isin(a)]
        f = d[d.notnull()]
        #avg_user = df.loc[df['userId'] == user,'rating'].values[0]
        index = f.index.values.squeeze().tolist()
        corr = similarity.loc[user,index]
        fin = pd.concat([f, corr], axis=1)
        fin.columns = ['adj_score','correlation']
        fin['score']=fin.apply(lambda x:x['adj_score'] * x['correlation'],axis=1)
        nume = fin['score'].sum()
        deno = fin['correlation'].sum()
        final_score = (nume/deno)
        score.append(final_score)
    data = pd.DataFrame({'articles':aritcles_for_consideration,'score':score})
    data = data.sort_values(by='score',ascending=False)
    data = data.reset_index(drop=True)
    return int(data.iloc[0,0])

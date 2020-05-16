import pandas as pd

def calc_popularity(data):
    df = data.copy()
    counts = df['pageTitle'].value_counts()
    df['pageVisits'] = df['pageTitle'].apply(lambda x: counts[x])
    return df

def take_first_click(data):
    df = data.copy()
    df.sort_values(by=['visitor', 'pageTitle', 'time'], inplace=True)
    df.reset_index(drop=True, inplace=True)
    df = df.groupby(['visitor', 'pageTitle']).first().reset_index()
    return df

def cos_sim(mat):
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    import pandas as pd
    cosine = cosine_similarity(mat)
    np.fill_diagonal(cosine, 0 )
    similarity_users =pd.DataFrame(cosine,index=mat.index)
    similarity_users.columns=mat.index
    return similarity_users

def find_n_neighbours(similarity,n):
    import numpy as np
    import pandas as pd
    order = np.argsort(similarity.values, axis=1)[:, :n]
    similarity = similarity.apply(lambda x: pd.Series(x.sort_values(ascending=False).iloc[:n].index, 
          index=['top{}'.format(i) for i in range(1, n+1)]), axis=1)
    return similarity

def User_item_score(user, df, mat, neighbours,similarity):
    import pandas as pd
    articles_read_by_user = mat.columns[mat.iloc[user,:]>0].tolist()
    a = neighbours[neighbours.index==user].values.squeeze().tolist()
    neighbours_articles = df[df.visitor_label.isin(a)]['page_label'].unique()
    aritcles_for_consideration = list(set(neighbours_articles)-set(articles_read_by_user))
    score = []
    for item in aritcles_for_consideration:
        c = mat.loc[:,item]
        d = c[c.index.isin(a)]
        f = d[d.notnull()]
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
    return data

def calc_freshness(data):
    import datetime
    df = data.copy()
    df['freshness'] = df['pub_time'].apply(lambda x: (datetime.datetime(2020, 5, 13, 0, 0) - x).total_seconds()/3600) # in hours
    return df

def calc_freshness_sample(data):
    import datetime
    df = data.copy()
    df['freshness'] = df['pub_time'].apply(lambda x: (datetime.datetime(2020, 4, 30, 0, 0) - x).total_seconds()/3600) # in hours
    return df

def get_subtopic(url):
    url = url.replace('http://', '', 1)
    url = url.replace('https://', '', 1)
    url = url.replace('www.vesti.bg', '', 1)
    url = url.split('/')
    url = [string for string in url if string != ""]
    joined_url = ''.join(url)
    if 'razvlechenia' in joined_url:
        topic = 'razvlechenia'
    elif 'testove' in joined_url:
        topic = 'testove'
    elif 'koronavirus' in joined_url or 'covid' in joined_url:
        topic = 'tema-koronavirus'
    elif not joined_url or len(url) == 1 or '?' in joined_url:
        topic = 'no_topic'
    elif len(url) == 2 or url[0] == url[1]:
        topic = url[0] + '_others'
    else:
        topic = url[1]
    
    topic = topic.replace('tema-', '', 1)
    topic = re.sub('[^a-zA-Z]+', ' ', topic)
    topic = ' '.join(topic.split(' '))
    return topic

def calc_freshness_w_read(data):
    df = data.copy()
    df['diff'] = df['time'] - df['pub_time']
    df['freshness_w_read'] = df['diff'].apply(lambda x: x.total_seconds()/3600) # in hours
    del df['diff']
    return df

def calc_publication_time(data):
    df = data.copy()
    data.sort_values(by=['pageTitle', 'time'], inplace=True)
    first_time = data.groupby('pageTitle').first()['time']
    df['pub_time'] = df['pageTitle'].apply(lambda x: first_time[x])
    df.reset_index(inplace=True, drop=True)
    return df

def test_recommendation_colab(recommend_article, test_df, encoder_user, user):
    import numpy as np
    import datetime
    test_user=encoder_user.inverse_transform(np.array(user).reshape(-1))[0]
    actual_articles = test_df[(test_df.visitor==test_user) & (test_df.time > datetime.datetime(2020,4,30)) & (test_df.time < datetime.datetime(2020,5,1))]['pagePath']
    return recommend_article in actual_articles

def get_subtopics_array(df):
    result = []
    keys = {}
    for url in df.pagePath:
        # old_url = url
        if 'http://' in url or 'https://' in url:
            url = url.replace('http://', '', 1)
            url = url.replace('https://', '', 1)
            if 'http:' in url:
                idx = url.find('http:')
                url = url[0:idx]
            if 'https:' in url:
                idx = url.find('https:')
                url = url[0:idx]
        dup_str = url.find('www.vesti.bg', 2)
        if dup_str != -1:
            url = url[0:dup_str]
        params_idx = url.find('?')
        if params_idx != -1:
            url = url[0:params_idx]
        url = url.split('/')
        if len(url) <= 2:
            topic = 'no_topic'
            idx = keys.get(topic)
            if idx is None:
                idx = len(result)
                keys[topic] = idx
                row = {'topic': topic, 'count': 0}
                result.append(row)
            else:
                row = result[idx]
            row['count'] = row['count'] + 1
        elif len(url) == 3:
            topic = url[2]
            subtopic = f'{topic}_other'
            key = topic + subtopic
            idx = keys.get(key)
            if idx is None:
                idx = len(result)
                keys[key] = idx
                row = { 'topic': topic, 'subtopic_1': subtopic, 'count': 0 }
                result.append(row)
            else:
                row = result[idx]
            row['count'] = row['count'] + 1
        else:
            topic = url[2]
            subtopics = url[2:-1]
            key = topic + ''.join(subtopics)
            idx = keys.get(key)
            if idx is None:
                idx = len(result)
                keys[key] = idx
                row = { 'topic': topic, 'count': 0 }
                for i, subtopic in enumerate(subtopics):
                    row[f'subtopic_{i+1}'] = subtopic
                result.append(row)
            else:
                row = result[idx]
            row['count'] = row['count'] + 1
    return result


def get_subtopics(df):
    import pandas as pd
    r = get_subtopics_array(df)
    return pd.DataFrame(r)

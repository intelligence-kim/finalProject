import Graph
import pandas as pd
import json 
from ast import literal_eval


mbti_list = ['ISTJ','ISFJ','INFJ','INTJ',
                        'ISTP','ISFP','INFP','INTP',
                        'ESTP','ESFP','ENFP','ENTP',
                        'ESTJ','ESFJ','ENFJ','ENTJ']
mbti_data = pd.read_csv('./mbti_final_data.csv',index_col=0,header=0)


for mbti in mbti_list:
    data = pd.DataFrame({'contents':literal_eval(mbti_data.loc[f'{mbti}']['contents'])})
    data.index = range(len(data))
    test = Graph.MakeGraph(mbti_data=data)
    df = test.keyword_df()
    df.to_csv(f'./network/mbti/{mbti}.csv')


category = ['Watcha_Contents','Naver_Title','Naver_Contents','Tistory_Title','Tistory_Contents']
movie_data = pd.read_csv('./movie_total.csv',index_col=0)

movie_list = []

not_found = []
for n in range(0,15):
    movie_list = []
    df=pd.DataFrame()
    for i in range(n*100,n*100+100):
        for c in category:
            try:
                l = literal_eval(movie_data[c][i])
                if len(l) == 0: continue
                movie_list.extend(l)
                temp=pd.DataFrame({'contents':literal_eval(movie_data[c][i]),'nfid':movie_data['nfid'][i]})
                df = pd.concat([df,temp],axis=0)
            except:
                not_found.append([i,c])
                continue
    df.index = range(len(df))
    test = Graph.MakeGraph(mbti_data=df)
    df = test.keyword_df()
    df.to_csv(f'./network/movie/df{n}.csv')

with open('./not_found.json','w') as f:
    json.dump(not_found,
              f,ensure_ascii=False)
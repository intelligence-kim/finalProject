from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view, permission_classes

from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import conversation,UserMessage, questions, recommendation, movie
import json, random

import pandas as pd
import csv

import pickle
from gensim.models.keyedvectors import Word2VecKeyedVectors
import networkx as nx

# Create your views here.

# home.html
def home(request):
    return render(request, 'frontend/home.html')

def talk_view(request):
    return render(request, 'frontend/talk.html')

def survey_view(request):
    # questions TABLE 사용
    return render(request, 'frontend/survey.html')

def suggest_view(request):
    # chatbot_response(request)
    # messages = UserMessage.objects.all() # 모든 메시지 가져오기
    return render(request, 'frontend/suggest.html')


# 채팅 화면

def create_conversation(request):
    # 클라이언트에서 전달한 conversation_id를 가져옴
    conversation_id = request.POST.get('conversation_id')

    #새로운 conversation 생성 시(로그 끝남)
    if not conversation_id:
        #새로운 conversation 생성 및 conversation_id 전달
        new_conversation = conversation.objects.create()
        conversation_id = new_conversation.id

    # 해당 conversation에 해당하는 usermessages를 가져오기
    messages = UserMessage.objects.filter(conv_id__id=conversation_id)
    return render(request, 'frontend/suggest.html', {'messages': messages, 'conversation_id': conversation_id})



# REST API

def mbti_rest_api(request):
    if request.method == 'POST':
        # mbti 받아옴
        try:
            json_data = json.loads(request.body)
            mbti = json_data.get('mbti')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data.'}, status=400)

        # converstation 모델에 데이터 저장
        conv = conversation.objects.create(mbti = mbti)
        id = conv.id

        return JsonResponse({'conv_id': id })
    else:
        return JsonResponse({'error': 'Invalid request method'})

@csrf_exempt
def message_rest_api(request):
    if request.method == 'POST':
        # 클라이언트에서 전달한 conversation_id, message 가져옴
        try:
            json_data = json.loads(request.body)
            user_message = json_data.get('message')
            conversation_id = json_data.get('conversation_id')
            question = json_data.get('question_text')
            question_num = json_data.get('question_num')
            drop_index = json_data.get('drop_index')
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data.'}, status=400)

        # 챗봇 응답 처리 부분
        reply = get_assistant_empathy(question, question_num, user_message, drop_index)

        response_data = {
            'message': user_message,
            'conversation_id': conversation_id,
            'reply': reply['Answer'],
        }
        print(reply['keyword'])
        # 사용자의 메시지를 모델에 저장
        conv_obj = conversation.objects.get(id=conversation_id)
        UserMessage.objects.create(message=user_message, conv_id=conv_obj, keyword=reply['keyword'])

        return JsonResponse(response_data)
    else:
        return JsonResponse({'error': 'Invalid request method'})
    

# 전역 변수로 설정하기 위해 기본 설정
# question_rest_api 실행 될 때마다 업데이트됨
question = ''

def question_rest_api(request):
    if request.method == 'POST':
        # chat-gpt API 처리 함수
        result = get_random_question()
        # print(result['question_text'])
        # result = {'question_text', 'question_num', 'cat_survey_index'}
        return JsonResponse(result)
    else:
        return JsonResponse({'error': 'Invalid request method'})


# 재승 님: chat-gpt API 처리 함수
import openai
import random
with open('./secrets.json') as f:
    secrets = json.loads(f.read())

openai.api_key  = secrets['api_key']


 #사용자마다 대화 시작하면 불러와야함
survey_df = pd.read_csv('./csv/survey.csv',index_col=0)
survey_df['mbti 특성'] = [_.split(',') for _ in survey_df['mbti 특성']]
survey_df['mbti topic'] = [_.split(',')  for _ in survey_df['mbti topic']]
keyword_list=[] #추천단에 보낼 키워드리스트
print('hello view')

#설문 뽑기
def get_random_question():
    global survey_df
    category = survey_df['mbti topic'].value_counts().index # 설문 카테고리
    survey_num = len(category) # 설문 카테고리 개수(중복제외)
    select_num = random.randint(0, survey_num - 1) # 설문 카테고리 개수가 21이라면 0-20까지 뽑음
    cat_survey_index = [_ for _ in range(len(survey_df['mbti topic'])) if survey_df['mbti topic'][_] == category[select_num]]
    question_num = random.choice(cat_survey_index) # 뽑을 질문의 index
    question_text = survey_df['질문'][question_num]
    result = {'question_text': question_text, 'question_num': question_num, 'cat_survey_index': cat_survey_index}
    return result
# question_text = 질문 text
# num = 질문 인덱스
user_input = '아니요' #유저에게 받은 대답넣을 자리
# drop_index = 데이터프레임에서 제거할 index 리스트

# result = get_random_question()
def get_assistant_empathy(question_text, question_num, user_input, drop_index):
    #무지성공감봇
    global survey_df
    empathy=[]
    print(question_text, question_num, user_input, drop_index)
    messages = [{"role": "system", "content": "지금부터 너는 공감하는 역할을 맡아줘, 존댓말로 대답해줘"}]
    input_message = '질문 : ' + question_text + ',' + '사용자 : ' + user_input
    user_content = "user : " + input_message + "," + "질문에 대한 사용자의 대답에 존댓말로 짧게 한마디로 공감해줘"
    messages.append({'role' : 'user', 'content' : f"{user_content}"})
    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    assistant_empathy = completion.choices[0].message["content"].strip()
    # try:
    # except:
    #     print(completion.choices[0].message['content'])
    try:# :이 붙어있으면 한번 자름
        empathy = assistant_empathy.split(':')[1]
        try:#.으로 자를 수 있으면
            empathy = assistant_empathy.split(':')[1].split('.')[0]
        except:
            pass
    except:
        try: empathy = assistant_empathy.split('.')[0]
        except: empathy = assistant_empathy
    #감성분석봇
    messages = [{"role": "system", "content": "지금부터 너는 감성분석 전문가 역할을 맡아줘, 짧게 한 단어로 감성분석해줘"}]
    question_message = '질문 : {} , '.format(question_text) # 질문
    user_content = "user : ["+ f'{question_message}' + '답변자 : ' + f'{user_input}' + f"], 라는 대화에서 답변자는 {survey_df['mbti 특성'][question_num][0]+survey_df['mbti 특성'][question_num][1]} 사람인지 {survey_df['mbti 특성'][question_num][2]+survey_df['mbti 특성'][question_num][3]} 사람인지 감성분석 해서 '{survey_df['mbti 특성'][question_num][0]+survey_df['mbti 특성'][question_num][1]}'사람이면 '{survey_df['mbti 특성'][question_num][0]}', '{survey_df['mbti 특성'][question_num][2]+survey_df['mbti 특성'][question_num][3]}'사람이면 '{survey_df['mbti 특성'][question_num][2]}'이라고 대답해줘"
    messages.append({'role' : 'user', 'content' : f"{user_content}"})
    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages = messages)
    assistant_content = completion.choices[0].message["content"].strip()
    messages.append({'role': "assistant", "content": f"{assistant_content}"})
    #print(assistant_content)#챗봇의 대답
    if survey_df['mbti 특성'][question_num][0] in assistant_content:
        keyword = survey_df['mbti topic'][question_num][0]
    elif survey_df['mbti 특성'][question_num][2] in assistant_content:
        keyword = survey_df['mbti topic'][question_num][1]
    else:
        keyword = None
    print('전',len(survey_df))
    survey_df = survey_df.drop(drop_index).reset_index(drop=True)
    print('후',len(survey_df))
    print({'keyword' : keyword,'Answer' : empathy})
    return {'keyword' : keyword,'Answer' : empathy}
# my_dict = get_assistant_empathy(result['question_text'], result['question_num'], user_input, result['cat_survey_index'])
# keyword_list.append(my_dict['keyword'])



# 추천 결과 돌려주는 통신
def recommend_rest_api(request):
    if request.method == 'POST':
        # request 받으면 
        try:
            json_data = json.loads(request.body)
            mbti = json_data['mbti']
            conversation_id = json_data['id']
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data.'}, status=400)

        #### conv_id별로 추천 DB에서 뽑아오는 방식
        # 1. user message로 추출된 keyword DB에 같이 저장(message_rest_api에서 처리)
        # 2. conversation id로 keyword get
        keyword_list = UserMessage.objects.filter(conv_id=conversation_id).values('keyword')
        # 3. 얻은 keyword로 추천 (recommend_movies) => nfid return
        nfids = recommend_movies(mbti, keyword_list)
        # print(movie.objects.filter(nfid=nfids).all())
        movies = []
        for nfid in nfids:

            #recommendation.objects.create(nfid=nfid)

            # 4. nfid로 movies 조회 => recommendation DB에 저장
            mo = movie.objects.get(nfid=nfid)
            movie_data = {
                'nfid': mo.nfid,
                'title': mo.title,
                'synopsis': mo.synopsis,
                'review_key1': mo.review_key1,
                'review_key2': mo.review_key2,
                'review_key3': mo.review_key3,
                'movie_poster': mo.movie_poster,
            }
            movies.append(movie_data)

        result = {}  # 합쳐진 결과를 저장할 딕셔너리
        for item in movies:
            for key, value in item.items():
                if key in result:
                    result[key].append(value)
                else:
                    result[key] = [value]

        # result = json.dumps(result)
        # print('결과다~',result)
        # print('type', type(result)) # str...

        return JsonResponse(result)
    else:
        return JsonResponse({'error': 'Invalid request method'})

# ./csv/survey.csv
# def make_info():
#     title=pd.read_csv('./csv/EndData/total_review_end.csv',index_col=0)['title']
#     nfid=pd.read_csv('./csv/EndData/total_review_end.csv',index_col=0)['nfid']
#     return pd.concat([nfid,title],axis=1)

info_df = pd.read_csv('./csv/info_df.csv')

def recommender_system(mbti,info_df,keyword=None):
    if keyword==None:
        movie_list = recommend(f'{mbti}',info_df['title'])
        top_40 = list(top_n(movie_list,True,30).keys())
        sample_list = random.sample(top_40,5)
    else:
        movie_list = []
        for k in keyword:
            if k==None: continue
            movie_list.extend(recommend_keyword(f'{mbti}',info_df['title'],k))
        sample_list = random.sample(sum([],movie_list),5)
    return list(info_df[info_df['title'].isin(sample_list)]['nfid'])

def recommend(mbti,title):
    # g = pickle.load(open(f'./csv/network/final_graph/{mbti}.pickle', 'rb'))
    # model = Word2VecKeyedVectors.load(f'./csv/network/model/{mbti}.model')
    # g = pickle.load(open(f'./csv/network/graph/ori_{mbti}_Network_2.pickle', 'rb'))
    # model = Word2VecKeyedVectors.load(f'./csv/network/model/{mbti}.model')
    # gm = Graph.MakeGraph(mbti_data=1)
    g = pickle.load(open(f'./csv/network/final_graph/{mbti}.pickle', 'rb'))
    model = Word2VecKeyedVectors.load(f'./csv/network/model/{mbti}.model')
    dic = {}
    for n,ti in enumerate(list(title)):
        # if n==10: break
        w=0
        weight = []
        for tar in [f'{mbti.lower()}']:
            c=1
            d = nx.shortest_path(g,source=tar,target=ti,weight='distance')
            for i in range(0,len(d)-1):
                w1 = model.similarity(str(d[i]),str(d[i+1]))
                w2 = model.similarity(f'{tar}',str(d[i+1]))
                w3 = model.distance(str(d[i]),str(d[i+1]))
                if 'p' in tar:
                    w += (w1+w2)*w3
                else:
                    w += (w1)*w3
                c+=1
            weight.append(round(w/c,3))
        dic[ti]=max(weight)
    return dic

def recommend_movies(mbti, keyword_list):
    global info_df
    # 지성님 추천 화면
    keyword = keyword_list
    nfid = recommender_system(mbti,info_df,keyword=None)
    #nfid 5개 반환 => nfid로 movie 조회
    return nfid

def recommend_keyword(mbti,title,keyword):
    # gm = Graph.MakeGraph(mbti_data=1)
    g = pickle.load(open(f'./csv/network/final_graph/{mbti}.pickle', 'rb'))
    model = Word2VecKeyedVectors.load(f'./csv/network/model/{mbti}.model')
    mbti = mbti.lower()
    dic={}
    movie_list = []
    for n,ti in (enumerate(title)):
        w=0
        c=1
        weight = []
        d = nx.shortest_path(g,f'{mbti}',f'{keyword}',weight='distance')
        d.extend(nx.shortest_path(g,f'{keyword}',f'{ti}',weight='distance')[1:])
        for i in range(0,len(d)-1):
            w1 = model.similarity(str(d[i]),str(d[i+1]))
            w2 = model.similarity(f'{mbti}',str(d[i+1]))
            w3 = model.distance(str(d[i]),str(d[i+1]))
            w += (w1+w2)*w3
            c*=3
        weight.append(round(w/c,3))
        dic[ti]=max(weight)
    movie_list.extend(list(top_n(dic,True,15).keys()))
    return movie_list

def top_n(count_dict, reverse, n=3):
    return dict(sorted(count_dict.items(), reverse=reverse, key=lambda x: x[1])[:n])


# def survey_question(num):
#     question_list = []
#     category = list(set(survey_df['mbti topic']))
#     for i in range(num):
#         survey_num = len(category) # 설문 총 개수(중복제외)
#         select_num = random.randint(0,survey_num-1) # 설문 총 개수가 5라면 0-4까지 뽑음
#         # category[select_num]은 카테고리 값
#         question_list.append(
#         survey_df[survey_df['mbti topic']==category[select_num]].\
#         iloc[random.randint(0,len(survey_df[survey_df['mbti topic']==category[select_num]]))-1]['질문'])
#         category.remove(category[select_num])
#     return {'question_list':question_list}


# 설문 질문 DB에서 불러와서 랜덤으로 하나 return
# def survey_question():
#     nums = random.sample(range(1, 156), 3) # question 행 개수 중 3개 랜덤으로 뽑음
#     question_list = []
#     for i in nums:
#         queryset = questions.objects.values().filter(id = i)
#         text = queryset[0]['question']
#         question_list.append(text)
#     # print(question_list)
#     return question_list

# @csrf_exempt
# def question_rest_api(request):
#     if request.method == 'POST':
#         # 클라이언트에서 전달한 conversation_id, message 가져옴
#         try:
#             json_data = json.loads(request.body)
#             user_message = json_data.get('message')
#             conversation_id = json_data.get('conversation_id')
#         except json.JSONDecodeError:
#             return JsonResponse({'error': 'Invalid JSON data.'}, status=400)

#         # 챗봇 응답 처리 부분
#         # 핑퐁핑퐁 하는 거라서 survey에 사용
#         response_data = {
#             'message': user_message,
#             'conversation_id': conversation_id,
#             'reply': random.sample(survey_question(), 1),
#             # 'reply': random.sample(["현재 기능 구현 중 입니다.", "신속하게 제작하겠습니다.", "이용해주셔서 감사합니다."], 1),
#         }
#         # print(response_data.reply)

#         # 사용자의 메시지를 모델에 저장
#         conv_obj = conversation.objects.get(id=conversation_id)
#         UserMessage.objects.create(message=user_message, conv_id=conv_obj)

#         return JsonResponse(response_data)
#     else:
#         return JsonResponse({'error': 'Invalid request method'})
    

# rest api
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def hello_rest_api(request):
    data = {'message': 'Hello, REST API!'}
    return Response(data)
    # -> urls.py 열고 import function


'''# chatbot
def keyboard(request):

    return JsonResponse({
        'type':'buttons',
        'buttons':['안녕', '날씨']
    })

def message'''
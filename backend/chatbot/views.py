from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view, permission_classes

from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import conversation,UserMessage, questions
import json, random

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
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data.'}, status=400)

        # 챗봇 응답 처리 부분
        # 핑퐁핑퐁 하는 거라서 survey에 사용
        response_data = {
            'message': user_message,
            'conversation_id': conversation_id,
            'reply': random.sample(survey_question(), 1),
            # 'reply': random.sample(["현재 기능 구현 중 입니다.", "신속하게 제작하겠습니다.", "이용해주셔서 감사합니다."], 1),
        }
        # print(response_data.reply)

        # 사용자의 메시지를 모델에 저장
        conv_obj = conversation.objects.get(id=conversation_id)
        UserMessage.objects.create(message=user_message, conv_id=conv_obj)

        return JsonResponse(response_data)
    else:
        return JsonResponse({'error': 'Invalid request method'})
    
# 설문 질문 DB에서 불러와서 랜덤으로 하나 return
def survey_question():
    nums = random.sample(range(1, 156), 3) # question 행 개수 중 3개 랜덤으로 뽑음
    question_list = []
    for i in nums:
        queryset = questions.objects.values().filter(id = i)
        text = queryset[0]['question']
        question_list.append(text)
    # print(question_list)
    return question_list
    

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
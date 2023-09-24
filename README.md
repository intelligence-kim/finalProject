# 성향분석을 통한 넷플릭스 작품 추천
## [상세 내용](https://github.com/intelligence-kim/finalProject/blob/main/document/230811_%EC%A7%80%EC%9E%88%EC%A7%80_PPT_%EC%B5%9C%EC%A2%85.pdf)

## 프로젝트 소개
넷플릭스 자체적 추천은 유저들에게 상당한 피로도를 유발한다.또한 기존 추천의 문제점인 cold start 문제 해결을 위하여 개인성향에 기반한 넷플릭스 작품 추천 시스템을 구현한다.<br>
각 작품들의 리뷰를 토픽 모델링을 진행하고 네트워크 분석 기법 중 이분 그래프를 활용하여 유저들의 성향과 작품들을 연결하여 추천한다.<br>
챗봇은 chatGPT API를 활용하여 대화형 모델을 구성한다<br>

## 프로젝트 기술 소개
 - 네트워크 분석 라이브러리 : NetworkX, Node2Vec
 - 폐기된 모델 : KoBERT, fastText, PCA
 - 차원 축소 : TSNE cuda
 - 크롤링 : BeautifulSoup4, selenium
 - 토픽 모델링 : LDA, LSA, BERTopic
 - 토크나이저 : Mecab

## 개발 기간
 - 23.07 - 23.08.10

## 구성원
 - 김지성(팀장) : 추천 시스템, 모델링, EDA/전처리, 데이터 수집
 - 노재승 : EDA/전처리, 데이터 수집, chatGPT API를 활용한 챗봇 개발
 - 강예림 : 프론트, BERTopic, 데이터 수집
 - 이주현 : 프론트, 백, DB, UI, 데이터 수집
 - 윤영주 : 데이터 수집, 리서치 및 문서 작업

## 사용 언어
 - python

## 프로젝트 결과
### 데이터 수집
 1. MBTI
    - 네이버 블로그(73mb)
    - 티스토리(46mb)
    - 나무위키 덤프(437kb)
 2. Netflix
    - Rapid API 한국 넷플릭스 작품 정보
    - 넷플릭스 공식 사이트 작품 정보(1.9mb)
    - 네이버 블로그(363mb)
    - 티스토리(70mb)
    - 왓챠피디아(166mb)
    - IMDB 평점/리뷰개수/리뷰

### 챗봇(chatGPT3.5 turbo)
1. RULE_1 감성분석 모델
   - 모델에게 공감로봇의 역할 부여하여 사용자의 대답에 대한 공감 멘트 추출하여 대화형 챗봇으로 활용
2. RULE_2 키워드 추출 모델
   - 질문에 대한 사용자의 답변에서 사전에 준비한 질문지에서 지정한 영화관련 토픽 중 어떤 토픽에 가까운지 분석

### 네트워크 분석을 통한 추천 시스템
### ***대전제 : 노드 간 path 중 가장 잘 설명되는 path를 찾는다.***

<img width="534" alt="n" src="https://github.com/intelligence-kim/finalProject/assets/128572870/e6055401-c133-48f0-ab32-74a0728dd8d9"><br>
 - 작품 토픽 네트워크<br>
 
<img width="439" alt="n2" src="https://github.com/intelligence-kim/finalProject/assets/128572870/d8715a57-9377-4e71-ad94-a46e3b15c18e"><br>
 - 성향 토픽 네트워크<br>

- 그래프를 구성
![1](https://github.com/intelligence-kim/finalProject/assets/128572870/7424f422-ed98-484c-81ff-3d1257aeaddd)

- MBTI -> MOVIE까지 도달할 때, 노드 벡터 유사도가 가장 높은 길을 찾는다.
![2](https://github.com/intelligence-kim/finalProject/assets/128572870/f1339447-ec9f-45a8-a03f-9e390e85e91a)

- 키워드가 존재할 때, 키워드를 거치는 PATH를 찾고, PATH의 길이의 가중치를 높여서 해당 작품에 도달한다.
![3](https://github.com/intelligence-kim/finalProject/assets/128572870/6110b850-36db-4620-af55-2aa83056c3ca)




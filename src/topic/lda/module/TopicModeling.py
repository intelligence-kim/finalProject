import pandas as pd
from tqdm import tqdm
import re
import pickle
import csv
import pandas as pd
from pandas import DataFrame 
import numpy as np

from sklearn.feature_extraction.text import CountVectorizer
from konlpy.tag import Kkma
from konlpy.tag import Okt
from collections import Counter
from konlpy.tag import Mecab

from gensim.models.ldamodel import LdaModel
from gensim.models.callbacks import CoherenceMetric
from gensim import corpora
from gensim.models.callbacks import PerplexityMetric
from gensim.models.coherencemodel import CoherenceModel
from IPython.display import clear_output
import logging
from ast import literal_eval
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


class TopicModeling:
    def __init__(self,type=None,movie_data=None,stopwords_path='./koreanStopwords2.txt'):
        self.stopwords=[]
        file = open(f"{stopwords_path}", "r")
        while True:
            line = file.readline()
            if not line:
                break
            self.stopwords.append(line.strip())
        file.close()
        self.kkma = Kkma()
        self.mecab=Mecab()
        # if type != 'mbti':
        #     self.movie = movie_data

    def clean_text(self,text):
        text=re.sub(r"[^A-Za-z0-9가-힣.]|[xa0]"," ",text)
        text =' '.join(text.split())
        text = text.lstrip()
        return text.lower()
    
    def sentence_split(self, text):
        sentence = sum([],(text.split('.')))
        sentence = list(filter(None, sentence))
        return [s.strip() for s in sentence]
    
    def get_nouns(self,tokenizer, sentence):
        tagged = tokenizer.pos(sentence)
        nouns = [s for s, t in tagged if t in ['NNG', 'NNP', 'VA', 'XR'] and len(s) >1]
        return nouns
    
    def get_nouns(self,tokenizer, sentence):
        tagged = tokenizer.pos(sentence)
        nouns = [s for s, t in tagged if t in ['NNG', 'NNP', 'VA', 'XR'] and len(s) >1]
        nouns = [x for x in nouns if x not in self.stopwords]
        return nouns
    # 0.3 괜찮음
    def keyword_ext(self,mbti=None,movie_title=None,topic=5,passes=10,iterations=10,no_above=0.3):
        keyword = []


        mbti_ = self.sentence_split(mbti)
        for key in mbti_:
            keyword.append(self.get_nouns(self.mecab,key))
        dictionary = corpora.Dictionary(keyword)
        dictionary.filter_extremes(no_below=2, no_above=no_above)
        corpus = [dictionary.doc2bow(text) for text in keyword]
        num_topics = topic
        chunksize = 1000
        passes = passes
        iterations = iterations
        eval_every = 0
        try:
            temp = dictionary[0]
        except:
            return ''

            
            
        id2word = dictionary.id2token

        model = LdaModel(
            corpus=corpus,
            id2word=id2word,
            chunksize=chunksize,
            alpha='auto',
            eta='auto',
            iterations=iterations,
            num_topics=num_topics,
            passes=passes,
            eval_every=eval_every
        )
        return  model.top_topics(corpus)
    
    def clean_topic(self,topics):
        topic_dict={}
        for i in range(len(topics)):
            if topics[i][1]>-10.0 and topics[i][1]<-1.5:
                continue
            for key,value in dict(topics[i][0]).items():
                try:
                    topic_dict[value] += key
                except KeyError:
                    topic_dict[value] = key
        return topic_dict

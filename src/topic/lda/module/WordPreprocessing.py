import pandas as pd
from ast import literal_eval
from konlpy.tag import Kkma
from konlpy.tag import Okt
from konlpy.tag import Mecab

class sentence:
    def __init__(self,stopword_path='./koreanStopwords.txt') -> None:
        self.stopword_path = stopword_path
        self.stopwords = self.read_stopwords(self.stopword_path)
        self.mecab = Mecab()
        pass
    def read_stopwords(self,path):
        stopwords=[]
        file = open(f"{path}", "r")
        while True:
            line = file.readline()
            if not line:
                break
            stopwords.append(line.strip())
        file.close()
        return stopwords
    
    def top_n(self,count_dict, reverse, n=3):
        return dict(sorted(count_dict.items(), reverse=reverse, key=lambda x: x[1])[:n])
    
    def split_text(self,text):
        sentence = sum([],(text.split('.')))
        sentence = list(filter(None, sentence))
        return [s.strip() for s in sentence]

    def make_sentence(self,data):
        text = literal_eval(data)
        sentence_list=[]
        for i in text:
            sentence_list.extend(self.split_text(i))
        return sentence_list
    
    def ext_text(self,sentence):
        tagged = self.mecab.pos(sentence)
        nouns = [s for s, t in tagged if t in ['NNG', 'NNP', 'VA', 'XR'] and len(s) >1]
        nouns = [x for x in nouns if x not in self.stopwords]
        return nouns

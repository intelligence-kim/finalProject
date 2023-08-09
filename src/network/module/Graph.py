import nltk 

import matplotlib.pyplot as plt

import numpy as np
import pandas as pd

import networkx as nx
from networkx.algorithms.bipartite.projection import overlap_weighted_projected_graph

from nltk.corpus import reuters
from IPython.display import clear_output
import TopicModeling


from tqdm.notebook import tqdm

import pickle
from node2vec import Node2Vec
from tsnecuda import TSNE
from gensim.models.keyedvectors import Word2VecKeyedVectors
import community.community_louvain as cl
import os
import re

plt.rcParams['font.family'] = 'NanumGothic'
plt.rcParams['axes.unicode_minus'] = False

class MakeGraph:
    def __init__(self,stopwords_path='./koreanStopwords.txt',mbti_data=None) -> None:
        self.topic = TopicModeling.TopicModeling(stopwords_path=stopwords_path)
        self.mbti_data = mbti_data

    def clean_text(self,text):
        text=re.sub(r"[^A-Za-z0-9가-힣.]|[xa0]"," ",text)
        text =' '.join(text.split())
        text = text.lstrip()
        return text.lower()
    def keyword_lambda(self,text):
        try:
            keyword=[(v,k) for k,v in self.topic.keyword_ext(text,topic=1)[0][0]]
            # clear_output()
            os.system('clear')
            return keyword
        except:
            return np.nan
     
    def keyword_df(self,feature_data=None):
        self.mbti_data['contents']=self.mbti_data['contents'].apply(lambda x:self.clean_text(x))
        self.mbti_data["keywords"] = self.mbti_data["contents"].apply(self.keyword_lambda)
        self.mbti_data.dropna(inplace=True)
        return self.mbti_data
    
    def edge(self,data):
        edges = pd.DataFrame([
            {"source": _id, "target": keyword, "weight": score, "type": _type}
            for _id, row in data.iterrows()
            for _type in ["keywords"] 
            for (keyword, score) in row[_type]
        ])
        return edges
    
    def G(self,edges):
        G = nx.Graph()
        G.add_nodes_from(edges["source"].unique(), bipartite=0)
        G.add_nodes_from(edges["target"].unique(), bipartite=1)
        G.add_edges_from([
                (row["source"], row["target"])
                for _, row in edges.iterrows()
            ])
        return G

    def entity_graph(self,G,d=5):
        document_nodes = {n for n, d in G.nodes(data=True) if d["bipartite"] == 0}
        entity_nodes = {n for n, d in G.nodes(data=True) if d["bipartite"] == 1}
        # nodes_with_low_degree = {n for n, d in nx.degree(G, nbunch=entity_nodes) if d<5}
        nodes_with_low_degree = {n for n, d in nx.degree(G, nbunch=entity_nodes) if d<d}
        subGraph = G.subgraph(set(G.nodes) - nodes_with_low_degree)
        entityGraph = overlap_weighted_projected_graph(
            subGraph, 
            {n for n, d in subGraph.nodes(data=True) if d["bipartite"] == 1}
            )
        
        degrees = pd.Series({k: v for k, v in nx.degree(entityGraph)})
        degrees=degrees[degrees.values!=0]

        return entityGraph, degrees
    
    def plot_Distribution(self, serie: pd.Series, nbins: int, minValue=None, maxValue=None):
        _minValue=int(np.floor(np.log10(minValue if minValue is not None else serie.min())))
        _maxValue=int(np.ceil(np.log10(maxValue if maxValue is not None else serie.max())))
        bins = [0] + list(np.logspace(_minValue, _maxValue, nbins)) + [np.inf]
        serie.hist(bins=bins)
        plt.xscale("log")


    def graph_Summary(self, graph, bins=10):
        print(nx.info(graph))
        plt.figure(figsize=(20, 8))
        plt.subplot(1,2,1)
        degrees = pd.Series({k: v for k, v in nx.degree(graph)})
        plt.yscale("log")
        self.plotDistribution(degrees, bins)
        # plt.rcParams['font.family'] = 'NanumGothic'
        try:
            plt.subplot(1,2,2)
            allEdgesWeights = pd.Series({(d[0], d[1]): d[2]["weight"] for d in graph.edges(data=True)})
            self.plotDistribution(allEdgesWeights, bins)
            plt.yscale("log")
        except:
            pass

    def infoG(self,Graph):
        print('Number of nodes', len(Graph.nodes))
        print('Number of edges', len(Graph.edges))
        print('Average degree', sum(dict(Graph.degree).values()) / len(Graph.nodes))

    def filter_entity_graph(self,entityGraph,weight=0.1):
        filteredEntityGraph = entityGraph.edge_subgraph(
            [edge for edge in entityGraph.edges if entityGraph.edges[edge]["weight"]>weight]
        )
        return filteredEntityGraph
    
    def global_Kpis(self,g):
        globalKpis = [{
                "shortest_path": nx.average_shortest_path_length(_graph),
                "clustering_coefficient": nx.average_clustering(_graph),
                "global_efficiency": nx.global_efficiency(_graph)
            } for components in nx.connected_components(g) 
                for _graph in [nx.subgraph(g, components)]]
        pd.concat([
            pd.DataFrame(globalKpis), 
            pd.Series([len(c) for c in nx.connected_components(g)])
        ], axis=1)

        return globalKpis
    
    def connected_components(self,g):
        return pd.Series([len(c) for c in nx.connected_components(g)]).sum()
        
    def draw_Network(self,g):
        default_edge_color = 'gray'
        default_node_color = '#407cc9'
        enhanced_node_color = '#f5b042'
        enhanced_edge_color = '#cc2f04'
        spring_pos = nx.spring_layout(g)

        plt.axis("off")
        nx.draw_networkx(g, pos=spring_pos, node_color=default_node_color, 
                 edge_color=default_edge_color, with_labels=False, node_size=15)

    def make_community(self,g):
        communities = pd.Series(cl.best_partition(g))
        return communities
    
    def draw_community(self,g,nodes):
        smallGrap = nx.subgraph(g, nbunch=nodes)
        plt.figure(figsize=(20,20))

        pos = nx.spring_layout(smallGrap) 

        nx.draw(smallGrap, with_labels=True, node_color='skyblue', font_family='NanumGothic',node_size=1500, edge_cmap=plt.cm.Blues, pos = pos)

    def save_graph(self,g,name='test'):
        save_g = nx.Graph(g)
        pickle.dump(save_g, open(f'{name}.pickle', 'wb'))
    
    def load_graph(self,name='test'):
        g = pickle.load(open(f'{name}.pickle', 'rb'))
        return g

    def model(self,g,d=5,w=10):
        node2vec = Node2Vec(g, dimensions=d) 
        model = node2vec.fit(window=w) 
        embeddings = model.wv 
        return embeddings
    
    def tsne(self,embeddings):
        tsne=TSNE(n_components=2)
        embedding2d=tsne.fit_transform(embeddings.vectors)
        return embedding2d
    def draw_tsne(self,embedding2d):
        plt.plot(embedding2d[:, 0], embedding2d[:, 1], 'o')

    def save_model(self,model,name='model'):
        model.save(f'{name}.model')
        
    def load_model(self,name='model'):
        model=Word2VecKeyedVectors.load(f'./{name}.model')
        return model

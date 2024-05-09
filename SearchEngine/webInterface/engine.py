from django.shortcuts import render
from .models import Pages, Indexer, Keywords

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np
from nltk.stem import PorterStemmer
import os
import pickle

### TODO:
# 1. Better title weighting setting

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class SearchEngine(metaclass=Singleton):
    def __init__(self, pages, indexer, keywords):
        # table objects
        self.pages = pages
        self.indexer = indexer
        self.keywords = keywords

        # The file to save/load the TF-IDF matrix
        vectorizer_file = 'vectorizer.pickle'

        # for tf-idf calculation
        if os.path.exists(vectorizer_file):
            print("Loading vectorizer...")
            self.vectorizer = pickle.load(open(vectorizer_file, 'rb'))
            print("Vectorizer loaded.")
        else:
            self.vectorizer = TfidfVectorizer(ngram_range=(1, 3))
        
        self.tfidf_matrix = self.calculate_tfidf()
        print(f"TF-IDF Matrix: {self.tfidf_matrix.dtype} {self.tfidf_matrix.shape}")

        if not os.path.exists(vectorizer_file):
            pickle.dump(self.vectorizer, open(vectorizer_file, 'wb'))

        # for query preprocessing
        self.stemmer = PorterStemmer()
        self.stopwords = self.load_stopwords()

    def load_stopwords(self):
        stopwords = set()
        with open("stopwords.txt", "r") as file:
            for line in file:
                stopwords.add(line.strip())
        return stopwords

    def __get_docs(self):
        docs = []
        for page in self.pages:
            # extract keywords from the indexer
            content_keywords = [(index.keyword_id.keyword, index.frequency) for index in self.indexer if index.page_id == page and not index.is_title]
            
            # add title keywords with higher weight by checking index.is_title
            title_keywords = [(index.keyword_id.keyword, index.frequency * 5) for index in self.indexer if index.page_id == page and index.is_title]
            
            keyword_list = content_keywords + title_keywords
            keyword_list = sorted(keyword_list, key=lambda x: x[1], reverse=True)
            keywords = " ".join([keyword for keyword, _ in keyword_list])

            docs.append(keywords)
        return docs
    
    def calculate_tfidf(self):
        tfidf_file = 'tfidf_matrix.npy'

        # tfidf_matrix = np.zeros((len(self.pages), len(self.indexer)))

        if os.path.exists(tfidf_file):
            print("Loading TF-IDF matrix...")
            self.tfidf_matrix = np.load(tfidf_file, allow_pickle=True)
            print("TF-IDF matrix loaded.")
        else:
            self.tfidf_matrix = self._calculate_tfidf()  # Assume this method calculates the TF-IDF matrix
            np.save(tfidf_file, self.tfidf_matrix.toarray())
            print(f"TF-IDF Matrix: {self.tfidf_matrix.toarray().dtype} {self.tfidf_matrix.toarray().shape}")

        return self.tfidf_matrix

    def _calculate_tfidf(self):
        # Select keywords from the indexer for each page
        docs = self.__get_docs()

        tfidf_matrix = self.vectorizer.fit_transform(docs)
        # print(f"TF-IDF Matrix: {tfidf_matrix}")
        return tfidf_matrix

    def calculate_cosine_similarity(self, query):
        query_vector = self.vectorizer.transform([query])
        print(f"Query Vector: {query_vector.shape} {query_vector.dtype}")
        print("Calculating cosine similarity...")
        cosine_similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        print(f"Cosine Similarities calculated.")
        return cosine_similarities

    def rank_documents(self, query):
        cosine_similarities = self.calculate_cosine_similarity(query)
        print("Ranking documents...")
        indices = np.argsort(cosine_similarities)[::-1]
        ranked_pages = [(self.pages[int(i)], cosine_similarities[i]) for i in indices]
        print("Documents ranked.")
        return ranked_pages[:50] # max 50 results
    
    def query_preprocessing(self, query):
        query = query.lower()
        
        # Stemming
        query = self.stemmer.stem(query)
        print(f"Stemmed query: {query}")
        query = query.split(" ")
        
        # stopwords removal
        query = [word for word in query if word not in self.stopwords]
        
        #convert back to string
        query = " ".join(query)
        
        return query

    def search(self, query):
        query = self.query_preprocessing(query)

        ranked_pages = self.rank_documents(query)
        outputs = []

        for page, score in ranked_pages:
            if score == 0:
                break

            # extract child links from the child_link_list
            child_link_list = page.child_link_list.split("\n") if page.child_link_list else []

            # extract parent links
            parent_link_list = self.pages.filter(child_link_list__contains=page.url).values_list('url', flat=True)

            # extract keywords
            keyword_list = [(index.keyword_id.keyword, index.frequency) for index in self.indexer if index.page_id == page]
            keyword_list = sorted(keyword_list, key=lambda x: x[1], reverse=True)[:5]

            # print(f"last_modification_date: {page.last_modification_date}")
            output = {
                'page_title': page.title,
                'url': page.url,
                'last_modification_date': page.last_modification_date.strftime('%Y-%m-%d %H:%M:%S') if page.last_modification_date else None,
                'page_size': page.page_size,
                'keywords': keyword_list,
                'parent_links': parent_link_list,
                'child_links': child_link_list,
                'score': score
            }
            outputs.append(output)

        return outputs

def get_search_results(query):
    # Assuming you have a list of Page objects and Indexer objects
    pages = Pages.objects.all()
    indexer = Indexer.objects.all()
    keywords = Keywords.objects.all()

    # Create an instance of SearchEngine
    search_engine = SearchEngine(pages, indexer, keywords)

    results = search_engine.search(query)

    return results if results else "Not Found"

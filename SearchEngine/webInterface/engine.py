from django.shortcuts import render
from .models import Pages, Indexer, Keywords

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np
from nltk.stem import PorterStemmer

### TODO:
# 1. Better title weighting setting
# 2. Last modification date display bug

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class SearchEngine(metaclass=Singleton):
    def __init__(self, pages, indexer):
        # table objects
        self.pages = pages
        self.indexer = indexer

        # for tf-idf calculation
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 3))
        self.tfidf_matrix = self.calculate_tfidf()

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
            keyword_list = [(index.keyword_id.keyword, index.frequency) for index in self.indexer if index.page_id == page]
            keyword_list = sorted(keyword_list, key=lambda x: x[1], reverse=True)
            keywords = " ".join([keyword for keyword, _ in keyword_list])

            # Add title keywords with higher weight
            title_keywords = page.title.split()
            for keyword in title_keywords:
                keywords += " " + keyword * 3  # repeat title keywords 3 times

            docs.append(keywords)
        return docs

    def calculate_tfidf(self):
        # Select keywords from the indexer for each page
        docs = self.__get_docs()

        tfidf_matrix = self.vectorizer.fit_transform(docs)
        # print(f"TF-IDF Matrix: {tfidf_matrix}")
        return tfidf_matrix

    def calculate_cosine_similarity(self, query):
        query_vector = self.vectorizer.transform([query])
        # print(f"Query Vector: {query_vector}")
        cosine_similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        return cosine_similarities

    def rank_documents(self, query):
        cosine_similarities = self.calculate_cosine_similarity(query)
        indices = np.argsort(cosine_similarities)[::-1]
        ranked_pages = [(self.pages[int(i)], cosine_similarities[i]) for i in indices]
        return ranked_pages[:50] # max 50 results
    
    def query_preprocessing(self, query):
        # TODO: is case insensitive?
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

    # Create an instance of SearchEngine
    search_engine = SearchEngine(pages, indexer)

    results = search_engine.search(query)

    return results if results else "Not Found"
from django.shortcuts import render
from .models import Pages, Indexer, Keywords

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np
from nltk.stem import PorterStemmer

### TODO:
# 1. Implement stemming
# 2. Implement stop words removal

class SearchEngine:
    def __init__(self, pages, indexer):
        self.pages = pages
        self.indexer = indexer
        self.stopwords = self.load_stopwords()
        self.vectorizer = TfidfVectorizer()
        self.stemmer = PorterStemmer()

    def load_stopwords(self):
        stopwords = set()
        with open("stopwords.txt", "r") as file:
            for line in file:
                stopwords.add(line.strip())
        return stopwords

    def calculate_tfidf(self):
        docs = [page.title for page in self.pages]
        tfidf_matrix = self.vectorizer.fit_transform(docs)
        return tfidf_matrix

    def calculate_cosine_similarity(self, query):
        tfidf_matrix = self.calculate_tfidf()
        query_vector = self.vectorizer.transform([query])
        cosine_similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()
        return cosine_similarities

    def rank_documents(self, query):
        cosine_similarities = self.calculate_cosine_similarity(query)
        indices = np.argsort(cosine_similarities)[::-1]
        ranked_pages = [(self.pages[int(i)], cosine_similarities[i]) for i in indices]
        return ranked_pages[:50]
    
    def query_preprocessing(self, query):
        # TODO: is case insensitive?
        query = query.lower()
        
        # Stemming
        query = self.stemmer.stem(query)
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
            # extract child links from the child_link_list
            child_link_list = page.child_link_list.split(" ") if page.child_link_list else []

            # extract parent links
            parent_link_list = self.pages.filter(child_link_list__contains=page.url)

            output = {
                'page_title': page.title,
                'url': page.url,
                'last_modification_date': page.last_modification_date,
                'page_size': page.page_size,
                'keywords': [(index.keyword_id.keyword, index.frequency) for index in self.indexer if index.page_id == page],
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
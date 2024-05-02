from django.shortcuts import render

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np
from .models import Pages, Indexer, Keywords

class SearchEngine:
    def __init__(self, pages, indexer):
        self.pages = pages
        self.indexer = indexer
        self.vectorizer = TfidfVectorizer()

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
        ranked_pages = [(self.pages[i], cosine_similarities[i]) for i in indices]
        return ranked_pages[:50]

    def search(self, query):
        ranked_pages = self.rank_documents(query)
        outputs = []
        for page, score in ranked_pages:
            child_link_list = page.child_link_list.split(" ") if page.child_link_list else []

            output = {
                'page_title': page.title,
                'url': page.url,
                'last_modification_date': page.last_modification_date,
                'page_size': page.page_size,
                'keywords': [index.keyword_id.keyword for index in self.indexer if index.page_id == page],
                'parent_links': "None",
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
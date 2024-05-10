from django.test import TestCase
from .models import Pages, TopKeywords, Indexer, Keywords
from .engine import SearchEngine

# Create your tests here.
from webInterface.spider import Spider

class SearchEngineTestCase(TestCase):
    def setUp(self):        
        # Create an instance of SearchEngine
        pages = Pages.objects.all()
        indexer = Indexer.objects.all()
        keywords = Keywords.objects.all()
        
        self.engine = SearchEngine(pages, indexer, keywords)

    def test_query_preprocessing(self):
        # Test that query preprocessing works correctly
        query = "This is a test query"
        processed_query = self.engine.query_preprocessing(query)
        self.assertEqual(processed_query, "test queri")

    def test_search(self):
        # Test that search returns the correct results
        results = self.engine.search('Chain of Command')
        self.assertEqual(len(results), 16)
        self.assertEqual(results[0]['url'], 'https://www.cse.ust.hk/~kwtleung/COMP4321/Movie/89.html')

    def test_search_efficiency(self):
        # Test that search is efficient
        import time
        start_time = time.time()
        self.engine.search('test')
        end_time = time.time()
        self.assertLess(end_time - start_time, 1)  # The search should take less than 1 second

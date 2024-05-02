from bs4 import BeautifulSoup
import requests as rq
from urllib.parse import urljoin, urlparse
import sqlite3
from nltk.stem import PorterStemmer
import re
from datetime import datetime

from .parent_child_link import *

class Spider():
    def __init__(self, starting_url) -> None:
        self.starting_url = starting_url
        self.link = parent_child_link()
        self.stopwords = self.load_stopwords()  # Load stopwords
        self.stemmer = PorterStemmer()  # Create stemmer

    def load_stopwords(self):
        stopwords = set()
        with open("stopwords.txt", "r") as file:
            for line in file:
                stopwords.add(line.strip())
        return stopwords

    def stem_word(self, word):
        return self.stemmer.stem(word)

    def extract_keywords(self, text):
        # Extract keywords from the text and apply stemming and stopword removal
        keywords = re.findall(r'\b\w+\b', text.lower())
        keywords = [self.stem_word(keyword) for keyword in keywords if keyword not in self.stopwords]
        return keywords

    def extract_content(self, soup):
        # extract content from the soup object
        content = ""
        paragraphs = soup.find_all("body")
        for paragraph in paragraphs:
            if paragraph.get_text() == "br":
                continue
            content += paragraph.get_text() + " "
        return content
    
    def form_child_link_list(self, links):
        output = "\n"
        for link in links:
            output += link
            output += "\n"
        return output

    def insert_page(self, page, apps):
        Pages = apps.get_model('webInterface', 'Pages')

        # Insert the page into the Pages table
        page_instance = Pages.objects.create(
            title=page['title'],
            url=page['url'],
            last_modification_date=datetime.strptime(page['modification_date'], '%a, %d %b %Y %H:%M:%S %Z') if page['modification_date'] != -1 else None,
            page_size=page['page_size'],
            child_link_list=self.form_child_link_list(page['child_links'])
        )

        Keywords = apps.get_model('webInterface', 'Keywords')

        # Extract keywords from the page content and insert them into the keywords table
        keywords = self.extract_keywords(page['content'])
        keyword_dict = {}
        for keyword in keywords:
            keyword_instance, created = Keywords.objects.get_or_create(keyword=keyword)
            keyword_id = keyword_instance.id
            if keyword_id in keyword_dict.keys():
                keyword_dict[keyword_id] += 1
            else:
                keyword_dict[keyword_id] = 1

        Indexer = apps.get_model('webInterface', 'Indexer')

        # Insert associations between page and keywords into the indexer table
        for keyword_id, freq in keyword_dict.items():
            Indexer.objects.create(
                page_id=page_instance,
                keyword_id=Keywords.objects.get(id=keyword_id),
                frequency=freq,
                is_title=False
            )

        # Extract keywords from the title and insert them into the keywords table
        title_keywords = self.extract_keywords(page['title'])
        title_keyword_dict = {}
        for keyword in title_keywords:
            keyword_instance, created = Keywords.objects.get_or_create(keyword=keyword)
            keyword_id = keyword_instance.id
            if keyword_id in title_keyword_dict.keys():
                title_keyword_dict[keyword_id] += 1
            else:
                title_keyword_dict[keyword_id] = 1
        
        # Insert associations between page and keywords into the indexer table
        for keyword_id, freq in title_keyword_dict.items():
            Indexer.objects.create(
                page_id=page_instance,
                keyword_id=Keywords.objects.get(id=keyword_id),
                frequency=freq,
                is_title=True
            )

    def run(self, num_pages, apps):
        queue = [self.starting_url]  # Queue to store URLs to be processed
        visited = []  # Set to keep track of visited URLs
        num_processed = 0  # Counter for the number of processed pages

        while queue and num_processed < num_pages:
            url = queue.pop(0)  # Get the next URL from the queue
            if url not in visited:
                visited.append(url)
                try:
                    response = rq.get(url)  # Fetch the page
                    if response.status_code == 200:
                        page_content = response.text  # Extract the HTML content

                        # get header of url
                        header = rq.head(url).headers

                        # Parse the HTML using BeautifulSoup
                        soup = BeautifulSoup(page_content, 'lxml')

                        ### Extract the necessary information from the page
                        # title
                        title = soup.title.string if soup.title else ""
                        
                        # last modification date
                        last_modification_date = header.get('Last-Modified', -1)
                        
                        # size of page
                        page_size = header.get('content-length', -1)

                        # page content
                        content = self.extract_content(soup)  # Replace with your own function to extract content

                        # Extract all hyperlinks from the page
                        child_links = []
                        links = soup.find_all('a')
                        for link in links:
                            child_url = link.get('href')
                            child_url = urljoin(url, child_url)  # Resolve the child URL

                            # change the links content to complete link
                            child_links.append(child_url)

                            # Process the child URL (perform checks, add to queue, etc.)
                            if child_url not in visited and child_url not in queue:                                
                                # limit the number
                                if len(queue) < num_pages:
                                    queue.append(child_url)
                                    self.link.add_link(visited.index(url), url, child_url)

                        # Increment the counter for processed pages
                        num_processed += 1

                        # print(f"Current Page: {title} num_process: {num_processed} \nCurrent Queue: {queue} \n Current Visited: {visited}\n")
                        # Create a document dictionary
                        page = {
                            'title': title,
                            'url': url,
                            'modification_date': last_modification_date,
                            'page_size': page_size,
                            'child_links': child_links,
                            'content': content
                        }

                        # Insert the document into the index
                        self.insert_page(page, apps)
                    else:
                        print(f"Failed to fetch page: {url}")
                except rq.exceptions.RequestException as e:
                    print(f"Error fetching page: {url}")
            else:
                print(f"URL already visited: {url}")

        # self.conn.close()  # Close the database connection
        # print(f"Length of queue: {len(queue)}")

def load_initial_data(apps, schema_editor):
    # fetch the urls
    test_url_1 = "https://www.cse.ust.hk/~kwtleung/COMP4321/testpage.htm"
    num_of_pages = 30

    spider = Spider(test_url_1)
    spider.run(num_of_pages, apps)

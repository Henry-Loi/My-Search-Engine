from bs4 import BeautifulSoup
import requests as rq
from urllib.parse import urljoin, urlparse
import sqlite3
from nltk.stem import PorterStemmer
import re

from spider import parent_child_link

class Spider():
    def __init__(self, starting_url) -> None:
        self.starting_url = starting_url
        self.link = parent_child_link()
        self.conn = sqlite3.connect('search_engine.db')  # Connect to the SQLite database
        self.cursor = self.conn.cursor()
        self.create_tables()  # Create necessary tables for indexing
        self.stopwords = self.load_stopwords()  # Load stopwords
        self.stemmer = PorterStemmer()  # Create stemmer

    def create_tables(self):
        # Create tables for documents and terms if they don't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Pages (
                id INTEGER PRIMARY KEY,
                title TEXT,
                url TEXT,
                last_modification_date TEXT,
                page_size INTEGER,
                child_link_list TEXT
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Keywords (
                id INTEGER PRIMARY KEY,
                keyword TEXT UNIQUE
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Indexer (
                page_id INTEGER,
                keyword_id INTEGER,
                frequency INTEGER,
                FOREIGN KEY (page_id) REFERENCES Pages(id),
                FOREIGN KEY (keyword_id) REFERENCES Keywords(id)
            )
        ''')

        # not necessary
        # self.cursor.execute('''
        #     CREATE TABLE IF NOT EXISTS ChildLinks (
        #         page_id INTEGER,
        #         keyword_id INTEGER,
        #         FOREIGN KEY (page_id) REFERENCES Pages(id),
        #         FOREIGN KEY (keyword_id) REFERENCES Keywords(id)
        #     )
        # ''')

    def load_stopwords(self):
        stopwords = set()
        with open("stopwords.txt", "r") as file:
            for line in file:
                stopwords.add(line.strip())
        return stopwords

    def stem_word(self, word):
        return self.stemmer.stem(word)

    def extract_terms(self, text):
        # Extract terms from the text and apply stemming and stopword removal
        terms = re.findall(r'\b\w+\b', text.lower())
        terms = [self.stem_word(term) for term in terms if term not in self.stopwords]
        return terms

    def insert_document(self, document):
        # Insert the document into the documents table
        self.cursor.execute('INSERT INTO documents (title, url, content) VALUES (?, ?, ?)',
                            (document['title'], document['url'], document['content']))
        document_id = self.cursor.lastrowid

        # Extract terms from the document content and insert them into the terms table
        terms = self.extract_terms(document['content'])
        term_ids = []
        for term in terms:
            self.cursor.execute('INSERT OR IGNORE INTO terms (term) VALUES (?)', (term,))
            self.cursor.execute('SELECT id FROM terms WHERE term = ?', (term,))
            term_id = self.cursor.fetchone()[0]
            term_ids.append(term_id)

        # Insert associations between document and terms into the indexer table
        for term_id in term_ids:
            self.cursor.execute('INSERT INTO indexer (document_id, term_id) VALUES (?, ?)',
                                (document_id, term_id))

        # Commit the changes to the database
        self.conn.commit()

    def extract_content(self, soup):
        # extract content from the soup object
        content = ""
        paragraphs = soup.find_all("body")
        for paragraph in paragraphs:
            if paragraph.get_text() == "br":
                continue
            content += paragraph.get_text() + " "
        return content

    def run(self, num_pages):
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

                        # Extract the necessary information from the page
                        # title
                        title = soup.title.string if soup.title else ""

                        # last modification date
                        last_modification_date = header.get('Last-Modified', -1)
                        
                        # size of page
                        page_size = header.get('content-length', -1)

                        # 
                        content = self.extract_content(soup)  # Replace with your own function to extract content

                        # Create a document dictionary
                        document = {
                            'title': title,
                            'url': url,
                            'content': content
                        }

                        # Insert the document into the index
                        self.insert_document(document)

                        # Extract all hyperlinks from the page
                        links = soup.find_all('a')

                        for link in links:
                            child_url = link.get('href')
                            child_url = urljoin(url, child_url)  # Resolve the child URL

                            # Process the child URL (perform checks, add to queue, etc.)
                            if child_url not in visited:
                                # limit the number
                                if len(queue) < num_pages:
                                    queue.append(child_url)
                                    self.link.add_link(visited.index(url), url, child_url)

                            # Increment the counter for processed pages
                            num_processed += 1
                    else:
                        print(f"Failed to fetch page: {url}")
                except rq.exceptions.RequestException as e:
                    print(f"Error fetching page: {url}")
            else:
                print(f"URL already visited: {url}")

        self.conn.close()  # Close the database connection
        print(f"Length of queue: {len(queue)}")

if __name__ == "__main__":
    # fetch the urls
    test_url_1 = "https://www.cse.ust.hk/~kwtleung/COMP4321/testpage.htm"
    num_of_pages = 30

    spider = Spider(test_url_1)
    spider.run(num_of_pages)

    print(spider.link)
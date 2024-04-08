from bs4 import BeautifulSoup

import requests as rq
from urllib.parse import urljoin, urlparse

class parent_child_link():
    def __init__(self) -> None:
        self.data = {}
        self.size = 1
    
    def print_page(self, page_id_url, level=0):
        page_id, page_url = page_id_url
        print('  ' * level + f"Page ID: {page_id}, URL: {page_url}")
        if page_id_url in self.data:
            for child_page_id_url in self.data[page_id_url]:
                self.print_page(child_page_id_url, level + 1)

    def __str__(self) -> str:
        print(f"Parent-Child Link: \nSize: {self.size}")
        # Find the root pages
        root_pages = set(self.data.keys()) - {child for children in self.data.values() for child in children}
        for root_page in root_pages:
            self.print_page(root_page)
        return ""

    def add_link(self, parent_id, parent_url, child_url):
        if (parent_id, parent_url) in self.data:
            self.data[(parent_id, parent_url)].append((self.size, child_url))
            self.size += 1
        else:
            self.data[(parent_id, parent_url)] = [(self.size, child_url)]
            self.size += 1

    def get_children(self, parent_page_id, parent_url):
        if (parent_page_id, parent_url) in self.data:
            return self.data[(parent_page_id, parent_url)]
        else:
            return []

    def get_parents(self, child_page_id, child_url):
        parents = []
        for (parent_id, parent_url), children in self.data.items():
            if (child_page_id, child_url) in children:
                parents.append((parent_id, parent_url))
        return parents
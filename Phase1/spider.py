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


# class Spider():
#     def __init__(self, starting_url) -> None:
#         self.starting_url = starting_url
#         self.link = parent_child_link()

#     def run(self, num_pages):
#         queue = [self.starting_url]  # Queue to store URLs to be processed
#         visited = []  # Set to keep track of visited URLs
#         num_processed = 0  # Counter for the number of processed pages

#         while queue and num_processed < num_pages:
#             url = queue.pop(0)  # Get the next URL from the queue
#             if url not in visited:
#                 visited.append(url)
#                 try:
#                     response = rq.get(url)  # Fetch the page
#                     if response.status_code == 200:
#                         page_content = response.text  # Extract the HTML content

#                         # print(page_content)

#                         # Parse the HTML using BeautifulSoup
#                         soup = BeautifulSoup(page_content, 'lxml')
                        
#                         # Extract all hyperlinks from the page
#                         links = soup.find_all('a')

#                         # Remove the file extension from the URL
#                         dot_index = url.rfind('/')
#                         if dot_index != -1:
#                             base_url = url[:dot_index]

#                         for link in links:
#                             child_url = link.get('href')
                            
#                             child_url = base_url+ "/" +child_url

#                             # Process the child URL (perform checks, add to queue, etc.)
#                             if child_url not in visited:
#                                 # limit the number
#                                 if len(queue) < num_pages:
#                                     queue.append(child_url)
#                                     # add child url without check
#                                     self.link.add_link(visited.index(url), url, child_url)
#                                     # print(f"pid: {visited.index(url)} parent: {url} add: {child_url}")
                                
#                             # Increment the counter for processed pages
#                             num_processed += 1
#                     else:
#                         print(f"Failed to fetch page: {url}")
#                 except rq.exceptions.RequestException as e:
#                     print(f"Error fetching page: {url}")
#             else:
#                 print(f"URL already visited: {url}")
        
#         print(len(queue))


# if __name__ == "__main__":
#     # fetch the url
#     test_url = "https://www.cse.ust.hk/~kwtleung/COMP4321/testpage.htm"
#     num_of_pages = 30

#     spider = Spider(test_url)
#     spider.run(num_of_pages)

#     print(spider.link)

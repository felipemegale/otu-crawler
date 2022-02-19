''' IMPORTS '''
# import HTML parser
from bs4 import BeautifulSoup

# import HTTP library
import requests

# import URL utility library
from urllib.parse import urlsplit, quote

# import another URL utility library
import tldextract

# import sleep to prevent IP lockout
#     or intentional delays
from time import sleep

# import datetime to improve logging
from datetime import datetime

# python native queue/stack data structure
from collections import deque

# native python json module, allows to serialize/deserialize json
import json
'''END IMPORTS'''

'''GLOBAL VARIABLES'''
university_domains = ['uoit', 'ontariotechu'] # list of accepted domains
bad_file_extensions = ["mp4","mkv","pdf","docx","doc","mp3","wav","webp", "jpg", "png"]
INITIAL_URL = "https://ontariotechu.ca"
graph = {} # this is a dictionary. each key is a URL and each value is a set of URLs that are referenced by the key
queue = deque() # this will be the queue of unvisited URLs
'''END GLOBALS VARIABLES'''

''' BEGIN FUNCTIONS '''
# helper function to get formatted current datetime
def get_now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# lambda function to filter off URLs with bad file extensions
def detect_bad_file_extensions(url):
    splitted_url = urlsplit(url)
    path = splitted_url.path

    for ext in bad_file_extensions:
        if ext in path:
            return False
    return True

# lambda function to return URL withouth index.php in it
# since the version without it redirects to the same page
# this function also strips trailing /
def rstrip_url(url):
    splitted_url = urlsplit(url)
    scheme = splitted_url.scheme
    netloc = splitted_url.netloc
    path = splitted_url.path\
        .rstrip('/')\
        .replace('index.php', '')\
        .replace('index.html', '')\
        .replace('//','/')\
        .rstrip('/')
    new_url = f'{scheme}://{netloc}{path}'.rstrip('/')
    return new_url

# lambda function to convert uoit domain to ontariotechu
def uoit_to_ontariotechu(url):
    splitted_url = urlsplit(url)
    scheme = splitted_url.scheme
    netloc = splitted_url.netloc.replace('uoit','ontariotechu')
    path = splitted_url.path
    new_url = f'{scheme}://{netloc}{path}'.rstrip('/')
    return new_url

# step by step:
# 1) sleep for 1 second to avoid ip blocking or slow down
# 2) perform HTTP request to given URL
# 3) parse HTML response to Python object
# 4) get all anchor tags
# 5) get all hrefs from all anchors
# 6) filter off hrefs that are not in the UOIT or OTU domains
# 7) filter off URLs that point to files
# 8) remove trailing / , and index.php, and index.html, and //
# 9) change all uoit domains to ontariotechu
# 10) return children of current node
def generate_children(url):
    sleep(2)
    print(get_now(), "GET HTTP request", url)
    r = requests.get(url)
    html_content = r.content
    soup = BeautifulSoup(html_content, "html.parser")
    all_anchors = soup.find_all("a")
    all_hrefs = []
    for anchor in all_anchors:
        try:
            all_hrefs.append(anchor['href'])
        except:
            pass
    university_hrefs = list(filter(lambda d: tldextract.extract(d).domain in university_domains, all_hrefs))
    university_hrefs = list(filter(detect_bad_file_extensions, university_hrefs))
    university_hrefs = list(map(rstrip_url, university_hrefs))
    university_hrefs = list(map(uoit_to_ontariotechu, university_hrefs))
    print(get_now(), 'Returning children...')
    return list(set(university_hrefs))

# bfs driver function
# add by populating queue with first node
# while queue is not empty,
#     pop element from queue,
#     if element hasnt been seen before
#     generate its children
#     add children to queue to be visited
#     add children to adjacency list
#     when queue is empty, all nodes have been visited
#     write adjacency list to file
#     quit BFS
def bfs(url):
    print(get_now(), "Started BFS...")
    queue.append(url)

    while len(queue) != 0:
        u = queue.pop()
        print(get_now(), f'Analyzing {u}...')
        graph_keys = list(graph.keys())

        if u not in graph_keys:
            print(get_now(), 'Generating children...')
            children = generate_children(u)
            print(get_now(), 'Generated', len(children), 'children!')

            for child in children:
                queue.append(child)
            graph[u]=children
    print(get_now(), 'Writing adjacency list to file...')
    with open('bfs_adj_list.json', 'w') as f:
        f.write(json.dumps(graph))
    print(get_now(), 'Wrote adjacency list to file!')

''' END FUNCTIONS '''


''' BEGIN MAIN '''
if __name__ == '__main__':
    print(get_now(), "Starting BFS...")
    bfs(INITIAL_URL)
    print(get_now(), "Program finished!")
''' END MAIN '''
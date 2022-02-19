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

# python native queue/stack data structure
from collections import deque
'''END IMPORTS'''

'''GLOBAL VARIABLES'''
university_domains = ['uoit', 'ontariotechu'] # list of accepted domains
bad_file_extensions = ["mp4","mkv","pdf","docx","doc","mp3","wav","webp", "jpg", "png"]
INITIAL_URL = "https://ontariotechu.ca"
graph = {} # this is a dictionary. each key is a URL and each value is a set of URLs that are referenced by the key
queue = deque() # this will be the queue of unvisited URLs
'''END GLOBALS VARIABLES'''

''' BEGIN FUNCTIONS '''
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
    sleep(1.0)
    r = requests.get(url)
    html_content = r.content
    soup = BeautifulSoup(html_content, "html.parser")
    all_anchors = soup.find_all("a")
    all_hrefs = [anchor['href'] for anchor in all_anchors]
    university_hrefs = list(filter(lambda d: tldextract.extract(d).domain in university_domains, all_hrefs))
    university_hrefs = list(filter(detect_bad_file_extensions, university_hrefs))
    university_hrefs = list(map(rstrip_url, university_hrefs))
    university_hrefs = list(map(uoit_to_ontariotechu, university_hrefs))
    return university_hrefs

def bfs(url):
    queue.append(url)

    while len(queue) != 0:
        u = queue.pop()

        if (u not in graph.keys()):
            children = generate_children(u)
            for child in children:
                queue.append(child)
''' END FUNCTIONS '''


''' BEGIN MAIN '''
if __name__ == '__main__':
    bfs(INITIAL_URL)
''' END MAIN '''
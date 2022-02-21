''' IMPORTS '''
# import HTML parser
from bs4 import BeautifulSoup

# import HTTP library
import requests

# import URL utility library
from urllib.parse import urlsplit

# import another URL utility library
import tldextract

# import sleep to prevent IP lockout
#     or intentional delays
from time import sleep

# import datetime to improve logging
from datetime import datetime

# python native queue data structure
from collections import deque

# native python json module, allows to serialize/deserialize json
import json
'''END IMPORTS'''

'''GLOBAL VARIABLES'''
# list of accepted domains
university_domains = ['uoit', 'ontariotechu']

# list of excluded extensions
bad_file_extensions = ["mp4","mkv","pdf","docx","doc","mp3","wav","webp", "jpg", "png"]

# BFS will use this URL as starting node
INITIAL_URL = "https://ontariotechu.ca"

# this is a dictionary. each key is a URL and each value is a set of URLs that are referenced by the key
graph = {}

# this will be the queue of unvisited URLs
queue = deque()
'''END GLOBALS VARIABLES'''

''' BEGIN FUNCTIONS '''
# helper function to get formatted current datetime
def get_now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# lambda function to disregard all those hrefs that are not http or https pages, e.g. mailto
def filter_non_http(url):
    splitted_url = urlsplit(url)
    scheme = splitted_url.scheme
    if scheme not in ['http', 'https']:
        return False
    return True

# lambda function to filter off URLs with bad file extensions
def detect_bad_file_extensions(url):
    splitted_url = urlsplit(url)
    path = splitted_url.path

    for ext in bad_file_extensions:
        if ext in path:
            return False
    return True

# lambda function to remove www. from URLs, trailing slashes, index pages and double slashes.
def rstrip_url(url):
    splitted_url = urlsplit(url)
    netloc = splitted_url.netloc.replace("www.", "")
    path = splitted_url.path\
        .rstrip('/')\
        .replace('index.php', '')\
        .replace('index.html', '')\
        .replace('//','/')\
        .rstrip('/')
    new_url = f'https://{netloc}{path}'.rstrip('/')
    return new_url

# lambda function to convert uoit domain to ontariotechu
def uoit_to_ontariotechu(url):
    splitted_url = urlsplit(url)
    netloc = splitted_url.netloc.replace('uoit','ontariotechu')
    path = splitted_url.path
    new_url = f'https://{netloc}{path}'.rstrip('/')
    return new_url

# key function for BFS. This expands the current node (URL)
def generate_children(url):
    try:
        # 1) sleep for 1 second to avoid ip blocking or throttling
        sleep(1)
        
        # 2) perform HTTP request to given URL
        print(get_now(), "GET HTTP request", url)
        r = requests.get(url)
        html_content = r.content

        # 3) parse HTML response to Python object
        soup = BeautifulSoup(html_content, "html.parser")

        # 4) get all anchor tags
        all_anchors = soup.find_all("a")
        
        # 5) get all hrefs from all anchors
        all_hrefs = []
        for anchor in all_anchors:
            try:
                all_hrefs.append(anchor['href'])
            except:
                pass

        # 6) filter off URLs that are not in the UOIT or OTU domains
        university_hrefs = list(filter(lambda d: tldextract.extract(d).domain in university_domains, all_hrefs))

        # 7) filter off all URLs that are not http or https (e.g. mailto)
        university_hrefs = list(filter(filter_non_http, university_hrefs))

        # 8) filter off URLs that point to files
        university_hrefs = list(filter(detect_bad_file_extensions, university_hrefs))

        # 9) remove www., index.php or index.html, trailing slashes and double slashes
        university_hrefs = list(map(rstrip_url, university_hrefs))

        # 10) convert uoit domains to ontariotechu since uoit redirects to ontariotechu
        university_hrefs = list(map(uoit_to_ontariotechu, university_hrefs))

        # 11) return all found children
        print(get_now(), 'Returning children...')
        return list(set(university_hrefs))
    except:
        # return empty children list if HTTP request fails for any reason
        return []

# bfs driver function
def bfs(url):
    print(get_now(), "Started BFS...")

    # 1) start by populating the queue with the initial node
    queue.append(url)
    skipped_count = 0

    # 2) while the queue isnt empty
    while len(queue) != 0:

        # 3) dequeue the first item in line
        u = queue.popleft()

        # 4) get current nodes of the graph
        graph_keys = list(graph.keys())

        print(get_now(), "Current number of nodes", len(graph_keys))

        # 5) if the dequeued item is not a node in the graph
        if u not in graph_keys:
            print(get_now(), "Skipped", skipped_count, "before expanding next node!")
            skipped_count = 0
            print(get_now(), f'Generating children of {u}...')

            # 6) expand all nodes from current node
            children = generate_children(u)
            print(get_now(), 'Generated', len(children), 'children!')

            # 7) queue new URLs if they have not been queued yet
            for child in children:
                if child not in queue   :
                    queue.append(child)
            
            # 8) add current node's adjacency list to graph
            graph[u]=children

        # 9) if web page has been visited before, skip
        else:
            skipped_count += 1
            print(get_now(), f'Skipped {u} !')
        
        print(get_now(), "Queue length", len(queue))

    # 10) after traversing all web pages, dump graph to a json file for posterior processing and analysis
    print(get_now(), 'Writing adjacency list to file...')
    with open('bfs_adj_list.json', 'w') as f:
        f.write(json.dumps(graph))
    print(get_now(), 'Wrote adjacency list to file!')

''' END FUNCTIONS '''


# Python's main function
''' BEGIN MAIN '''
if __name__ == '__main__':
    program_begin = datetime.now()
    print(program_begin, "Starting BFS...")
    # start BFS from initial URL
    bfs(INITIAL_URL)
    program_end = datetime.now()
    print(program_end, "Program finished!")
    delta = program_end - program_begin
    print("Program started", program_begin)
    print("Program finished", program_end)
    print("Program took", delta, "to complete!")
''' END MAIN '''
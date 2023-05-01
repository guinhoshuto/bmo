import requests
from rich import print
from bs4 import BeautifulSoup

unwanted_tags = ['script', 'style', 'meta']
content_tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']

def getContent(url):
    response = requests.get(url)
    main_content = ''
    soup = BeautifulSoup(response.content, 'html.parser') 
    for tag in unwanted_tags:
        for el in soup.select(tag):
           el.extract() 
    for tag in soup.select(','.join(content_tags)):
        main_content += tag.get_text()        
    print(main_content)
    return main_content
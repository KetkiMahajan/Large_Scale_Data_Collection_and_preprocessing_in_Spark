from bs4 import BeautifulSoup
import urllib
from urllib.request import Request, urlopen
import re
from newsplease import NewsPlease
import pandas as pd
import numpy as np

def getLinks(url):

    USER_AGENT = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'
    request = Request(url)
    request.add_header('User-Agent', USER_AGENT)
    response = urlopen(request)
    content = response.read()
    response.close()

    soup = BeautifulSoup(content, "html.parser")
    links = []
    for link in soup.findAll('a', attrs={'href': re.compile("^/")}):
            links.append(url + link.get('href'))

    return links

def getData(url):
    article = NewsPlease.from_url(url)

    return article

if __name__ == "__main__":
    data = pd.read_csv('newssheet.csv')
    links = data.Links
    links = links.replace(np.nan, '', regex=True)

    for link in links:
        if link:
            print(link)
            try:  # need to open with try
                list = getLinks(link)
            except urllib.error.HTTPError as e:
                if e.getcode() == 404:  # check the return code
                    continue
                raise  # if other than 404, raise the error

            for item in list:
                print(item)
                article = getData(item)
                print("Url: "+ str(article.url))
                print("Headline: "+ str(article.title))
                print("authors: "+ str(article.authors))
                print("Lead Paragraph: "+ str(article.description))
                print("Text: "+ str(article.text))
                print("Data Published: "+ str(article.date_publish))
                print("")
            print("")


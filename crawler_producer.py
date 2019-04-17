from bs4 import BeautifulSoup
import urllib
from urllib.request import Request, urlopen
import re
from newsplease import NewsPlease
import pandas as pd
import numpy as np

from kafka import KafkaProducer

def publish_message(producer_instance, topic_name, value):
    try:
        key_bytes = bytes('foo', encoding='utf-8')
        value_bytes = bytes(value, encoding='utf-8')
        producer_instance.send(topic_name, key=key_bytes, value=value_bytes)
        producer_instance.flush()
        print('Message published successfully.')
    except Exception as ex:
        print('Exception in publishing message')
        print(str(ex))


def connect_kafka_producer():
    _producer = None
    try:
        _producer = KafkaProducer(bootstrap_servers=['localhost:9092'], api_version=(0, 10), linger_ms=10)

    except Exception as ex:
        print('Exception while connecting Kafka')
        print(str(ex))
    finally:
        return _producer


def getLinks(url):

    USER_AGENT = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'
    request = Request(url)
    request.add_header('User-Agent', USER_AGENT)
    response = urlopen(request)
    content = response.read()
    response.close()

    soup = BeautifulSoup(content, "html.parser")
    links = {}
    minLen = 50 # Setting the threshold for the minimum length of url
    social = ["facebook.com", "twitter.com", "instagram.com", "plus.google.com", "linkedin.com", "youtube.com", "pinterest.com", "behance.net", "blog", "pdf"] # Excluding urls containing these
    flag = 1
    for link in soup.findAll('a', attrs={'href': re.compile("^((https?://)|/)")}):
        if len(link.get('href')) > minLen:
            if "http" in link.get('href') or "www" in link.get('href'):
                finalURL = link.get('href')
            else:
                finalURL = url + link.get('href')
            for l in social:
                if l in finalURL:
                    flag = 0
            if links.get(finalURL) and flag == 1:
                links[finalURL] = links.get(finalURL) + 1
            elif flag == 1:
                links[finalURL] = 1
            flag = 1

    return links

def getData(url):
    article = NewsPlease.from_url(url)

    return article

if __name__ == "__main__":
    data = pd.read_csv('newssheet.csv')
    links = data.Links
    links = links.replace(np.nan, '', regex=True)
    if len(links) > 0:
        prod = connect_kafka_producer()

    for link in links:
        if link:
            # print(link)
            try:  # need to open with try
                list = getLinks(link)
            except urllib.error.HTTPError as e:
                if e.getcode() == 404:  # check the return code
                    continue
                raise  # if other than 404, raise the error

            for item in list:
                if (list[item] == 1): # checking the number of occurrence of the link in the website
                    # print(item)
                    try:  # need to open with try
                        article = getData(item)
                    except urllib.error.HTTPError as e:
                        if e.getcode() == 404:  # check the return code
                            continue
                        raise  # if other than 404, raise the error
                    print("Url: "+ str(article.url))
                    print("Headline: "+ str(article.title))
                    print("authors: "+ str(article.authors))
                    print("Lead Paragraph: "+ str(article.description))
                    print("Text: "+ str(article.text))
                    print("Data Published: "+ str(article.date_publish))
                    print("")
                    publish_message(prod, 'News', str(article.url+"||"+article.title))
            print("")

    if prod is not None:
        prod.close()

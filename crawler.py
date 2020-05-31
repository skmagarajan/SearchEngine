from bs4 import BeautifulSoup

from urllib.request import urlopen
from urllib.parse import urlparse
import os
from os import path

from html.parser import HTMLParser

from urllib.error import HTTPError, URLError
from ssl import SSLError, CertificateError

import sys
import socket

import preprocess
import pickle
import urllib.parse

htmlpath = '/Users/saran/OneDrive/Desktop/UiC/htmlPages/'
urlpath = '/Users/saran/OneDrive/Desktop/UiC/'

links = list()
url_count = 0


def check_URL(url):
  if type(url) != type(""):  #Check if url is string or not
      print("Please give string url")
      return False
  try:
      if "?" not in url:      #For InvalidURL: URL can't contain control characters
        return True
  except ValueError:        #If url is string but invalid
      print("Bad URL")

def crawl(url):
    global links
    global url_count
    try:
        b = check_URL(url)
    except ValueError:
        print("EEE")
    print(url)
    if b:
        try:
            _url = urlopen(url,timeout=10)
            content = _url.read()
            remove_links = ["pdf","png","jpg","tar","zip","ppt","bib","docx","doc","avi","mp4","jpeg","gif","gz","rar","tgc","exe","js","css"]
            global PageCnt
            if not os.path.exists("htmlPages"):
                os.makedirs("htmlPages")
            soup = BeautifulSoup(content,"html.parser",from_encoding="iso-8859-1")
            for a in soup.find_all('a', href=True):     #Getting a tag in content
                links_extracted = str(a['href'])
                if(links_extracted.startswith('https')) and " " not in links_extracted:        #if links start from http
                    allow = True
                    for z in remove_links:
                        if z in links_extracted:
                            allow = False
                    if links_extracted not in links and allow is True:
                        pr = urlparse(links_extracted)
                        if "uic" in str(pr.netloc):
                            links.append(links_extracted)
                if(links_extracted.startswith('/') and "cs.uic.edu" in url) and " " not in links_extracted:        #if link contains path (/)
                    links_extracted = "https://cs.uic.edu"+str(links_extracted)
                    allow = True
                    for z in remove_links:
                        if z in links_extracted:
                            allow = False
                    if links_extracted not in links and allow is True:
                        pr = urlparse(links_extracted)
                        if "uic" in str(pr.netloc):     #Checking whether it belongs to UIC domain
                            links.append(links_extracted)
            with open(urlpath +'URLs.txt', 'a') as x:
                x.write(url + "\n");
            with open(htmlpath + str(url_count+1), 'wb') as f:
                f.write(content);
            print(url_count+1)
            url_count += 1
            return links
        except(HTTPError, TimeoutError, URLError, SSLError, CertificateError, UnicodeDecodeError, socket.timeout,socket.error):
            print("Error - get_links")
            return links
    else:
        return links

def main():
    global links
    url = "https://www.cs.uic.edu/"
    i = 0
    global url_count
    global urlpath

    if os.path.exists(urlpath+'URLs.txt'):
        os.remove(urlpath+'URLs.txt')

    while url_count < 3000:
        if i == 0:
            links = crawl(url)
            i += 1
        else:
            links = crawl(links[i])
            i += 1

if __name__ == "__main__":
    main()

A Web Search Engine
----
### Required Python Modules

> from bs4 import BeautifulSoup

>from urllib.request import urlopen

>from urllib.parse import urlparse

>import os

>from os import path

>from html.parser import HTMLParser

>from urllib.error import HTTPError, URLError

>from ssl import SSLError, CertificateError

>import sys

>import socket

>import preprocess

>import pickle

>from nltk.corpus import stopwords

>import nltk.tokenize

>import string

>import re

>import numpy

>import pandas

>import math

>import collections

>import nltk

>import pickle

>from tkinter import *

>from tkinter.ttk import Frame, Button, Label, Style, Entry

>import webbrowser

----
### Required Files
    Files used for Web Search Engine
    1. crawler.py
    2. main.py
    3. UserInterface.py


*crawler.py* 

This file perform crawling and storing html pages in htmlpages folder and URLs in URLs txt.

*main.py*

This file perform both document and query preprocessing, indexing and pagerank scores. These data structures are stored as pickle file in the folder

*UserInterface.py*

This file will create tkinter application for user to enter query and display top 10 ranks and even can move next suggested links


### Instructions to run the program
* Please dont run crawler.py and main.py it will run for long time to compute

* Please check you have 

  * doc_len.p

  * document_text.p

  * index.p

  * pr_scores.p

  * weight.p
  
* If not, then run Crawler and main python files and change path for html path and URL path in both file

* For search engine application, run *UserInterface.py* it takes some time to load and application will be displayed

  * Enter query in input field and click search button.

  * Press next button for more links.

  * Press prev button to get back links.



 



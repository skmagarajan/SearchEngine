import os
from nltk.corpus import stopwords
from bs4 import BeautifulSoup
import nltk.tokenize
import string
import re
import numpy
import pandas
import math
import collections
import nltk
import pickle

c = 10
pr_scores = dict() #Contains PageRank Scores for 3000 document
stpwords = stopwords.words('english')
retrieved_URL = dict()
document_text = dict()
index = dict()
q_ind = dict()
weight = dict()
q_weight = dict()
q_len = 0
cos_sim = dict()
doc_len = dict()



htmlpath = '/Users/saran/OneDrive/Desktop/UiC/htmlPages/'
urlpath = '/Users/saran/OneDrive/Desktop/UiC/'

def apply_p_rank(weights, default=1.0):
    rsp = 0.15
    weights = pandas.DataFrame(weights)
    nodes = set()       #Extracting Nodes
    for Key in weights:
        nodes.add(Key)
    for Key in weights.T:
        nodes.add(Key)
    matrix = weights.copy()     #Making weights as square

    def insert_missing_col(matrix):
        for key in nodes:
            if not key in matrix:
                matrix[key] = pandas.Series(default, index = matrix.index)
        return matrix

    matrix = insert_missing_col(matrix)
    matrix = insert_missing_col(matrix.T).T

    weights = matrix.fillna(default)

    weights = weights.T     #In this making weights postive
    for key in weights:
        if weights[key].sum() == 0.0:
            weights[key] = pandas.Series(numpy.ones(len(weights[key])), index=weights.index)
    weights = weights.T

    if len(nodes) != 0:
        startProb = 1.0 / float(len(nodes))
    curr = pandas.Series({node : startProb for node in nodes})
    prob = weights.div(weights.sum(axis=1), axis=0)
    alpha =( (1.0 + 1.0)/ ((float(len(nodes)) * rsp) + 1.0))
    prob = prob.copy().multiply(1.0 - rsp) + alpha

    for iteration in range(1000):
        t = curr.copy()
        curr = curr.dot(prob)
        delta = curr - t
        if ( math.sqrt(delta.dot(delta))) < 0.00001:
            break

    return curr

def clean_doc(content): #Function to remove script and style tag & Removing punctuation
    for script in content(["script","style"]):
        script.extract()
    content = content.get_text()
    content = content.strip()
    content = content.lower()
    content = re.sub('\d',"%d",content)
    for x in string.punctuation:
        if x in content:
            content = content.replace(x," ")
    content = content.replace("\n"," ")
    content = content.replace("\t"," ")
    return content

def pre_process_document(content,file):
    content = clean_doc(content)
    document_text[file] = content

def process_doc(content,Needed_Tags):   #filtering Needed_Tags words in the content
    global stpwords
    filterWords = []
    content = clean_doc(content)
    words = nltk.tokenize.word_tokenize(content)
    posTags = [pair[1] for pair in nltk.pos_tag(words)]
    for index,word in enumerate(words):
        tag = posTags[index]
        if tag in Needed_Tags and word not in stpwords:
            filterWords.append(word)
    return filterWords

def pr_vocab(doc):  #Applying PageRank
    windowSize = 2
    Needed_Tags = ['NN','NNS','NNP','NNPS','JJ']
    words = process_doc(doc,Needed_Tags) #Tokenizing and getting Needed_Tags words
    edge = collections.defaultdict(lambda: collections.Counter())
    for index,word in enumerate(words):
        for otherIndex in range(index - windowSize, index + windowSize + 1):
            if otherIndex >= 0  and otherIndex < len(words) and otherIndex != index:
                otherWord = words[otherIndex]
                edge[word][otherWord] += 1.0
    wordProb = apply_p_rank(edge,default=1.0)
    return wordProb.to_dict()

def process_q(q):   #Removing punctuation in query
    q = q.replace("\n","")
    q = q.strip()
    q = q.lower()
    q = re.sub('\d', '%d', q)
    for x in string.punctuation:
        if x in q:
            q = q.replace(x, " ")
    return q

def q_index(query):
    global q_ind
    global stpwords
    words = query.split(" ")
    for word in words:
        if word not in stpwords:
            if word not in q_ind.keys():
                q_ind[word] = 1
            elif word in q_ind:
                q_ind[word] = 1
            else:
                q_ind[word] += 1

def build_index(content, file):
    global index
    global document_text
    global stpwords
    for doc_id, text in document_text.items():
        words = text.split(" ")
        for word in words:
            if word not in stpwords:
                if word not in index.keys():
                    index[word] = {}
                    index[word][doc_id] = 1
                elif word in index and doc_id not in index[word].keys():
                    index[word][doc_id] = 1
                else:
                    index[word][doc_id] += 1

def cal_weights():
    global document_text
    global index
    global weight
    global doc_len

    for word in index.keys():
        for doc_id in index[word].keys():
            if word not in weight.keys():
                weight[word] = {}
            tf = (index[word][doc_id])
            idf = math.log((len(document_text) / len(index[word])) ,2)
            weight[word][doc_id] = tf * idf
            if doc_id not in doc_len.keys():
                doc_len[doc_id] = (tf**2) * (idf**2)
            else:
                doc_len[doc_id] += (tf**2) * (idf**2)

def cal_q_weights():
    global q_ind
    global q_weight
    global q_len
    global index

    for word in q_ind.keys():
        tf = (q_ind[word])
        if word in index.keys() and ((len(document_text) / len(index[word])) != 1):
            idf = math.log((len(document_text) / len(index[word])) , 2)
        else:
            idf = 0
        if idf != 0:
            q_len += (tf**2) * (idf**2)
        q_weight[word] = tf * idf

def cosine_sim():
    global weight
    global q_weight
    global index
    global q_ind
    global cos_sim
    global q_len
    global doc_len

    for word in q_ind.keys():
        if word in index.keys():
            for doc_id in index[word].keys():
                if doc_id not in cos_sim.keys():
                    if math.sqrt(doc_len[doc_id]) * math.sqrt(q_len) != 0:
                        cos_sim[doc_id] = weight[word][doc_id] * q_weight[word] / (math.sqrt(doc_len[doc_id]) * math.sqrt(q_len))
                    else:
                        cos_sim[doc_id] = 0
                else:
                    if math.sqrt(doc_len[doc_id]) * math.sqrt(q_len) != 0:
                        cos_sim[doc_id] += weight[word][doc_id] * q_weight[word] / (math.sqrt(doc_len[doc_id]) * math.sqrt(q_len))
                    else:
                        cos_sim[doc_id] = 0
    return cos_sim

def get_pr_query(pr_scores, query):
    q_words = query.split()
    total_scores = dict()
    for i in q_words:
        for doc in pr_scores.keys():
            total_scores[doc] = 0
            if i in pr_scores[doc].keys():
                total_scores[doc] += pr_scores[doc][i]
    print(total_scores)
    return total_scores

def combine_res(cos_sim, pr_res):
    combinedScores = dict()
    for k in cos_sim.keys():
        if k in pr_res.keys():
            if(cos_sim[k] + pr_res[k]) != 0:
                combinedScores[k] = 2*(cos_sim[k] * pr_res[k]) / (cos_sim[k] + pr_res[k])
    return combinedScores

def get_URL(key):
    with open(urlpath + 'URLs.txt') as f:
        for i, line in enumerate(f):
            if i == int(key)-1:
                return line.replace("\n","")

def search():
    global c
    global pr_scores
    for file in os.listdir(htmlpath):
        print("Html Page: "+file)
        f = open(htmlpath + file, 'rb')
        content = BeautifulSoup(f,'html.parser')
        pr_scores[file] = pr_vocab(content)
        pre_process_document(content, file)
        build_index(content,file)
    pickle.dump( index, open( "index.p", "wb" ) )
    pickle.dump( pr_scores, open( "pr_scores.p", "wb" ) )
    pickle.dump( document_text, open( "document_text.p", "wb" ) )

def results():
    global c
    global pr_scores
    global retrieved_URL
    cos_sim = dict()
    retrieved_URL_copy = dict()
    pr_res = dict()
    query = input("query : ")
    query = process_q(query)
    q_index(query)
    cal_weights()
    pickle.dump( weight, open( "weight.p", "wb" ) )
    pickle.dump( doc_len, open( "doc_len.p", "wb" ) )
    cal_q_weights()
    print(q_ind)
    print(q_len)
    cos_sim = cosine_sim()
    cos_sim = dict(collections.Counter(cos_sim).most_common(c))
    pr_res = get_pr_query(pr_scores, query)
    pr_res = dict(collections.Counter(pr_res).most_common(c))
    final_res = combine_res(cos_sim,pr_res)
    final_res = dict(collections.Counter(final_res).most_common(c))

    for key,value in final_res.items():
        file_name = key.split('.')
        retrieved_URL[file_name[0]] = get_URL(file_name[0])
        retrieved_URL_copy[file_name[0]] = get_URL(file_name[0])

    print(retrieved_URL)

def main():
    search()
    results()

if __name__ == "__main__":
    main()

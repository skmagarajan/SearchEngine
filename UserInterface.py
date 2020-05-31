from tkinter import *
from tkinter.ttk import Frame, Button, Label, Style, Entry
import webbrowser

import pickle
import re
import string
from nltk.corpus import stopwords
import collections
import math

index = pickle.load( open( "index.p", "rb" ) )
weight = pickle.load( open( "weight.p", "rb" ) )
doc_len = pickle.load( open( "doc_len.p", "rb" ) )
pr_scores = pickle.load( open( "pr_scores.p", "rb" ) )
document_text = pickle.load( open( "document_text.p", "rb" ) )

urlpath = '/Users/saran/OneDrive/Desktop/UiC/'

c = 3000
#pr_scores = dict() #Contains PageRank Scores for 3000 document
stpwords = stopwords.words('english')
retrieved_URL = dict()
#document_text = dict()
#index = dict()
q_ind = dict()
#weight = dict()
q_weight = dict()
q_len = 0
cos_sim = dict()
#doc_len = dict()
retrieved_URL = dict()

def ClearQElements():
    global q_ind
    global q_weight
    global q_len
    global cos_sim
    q_ind.clear()
    q_weight.clear()
    q_len = 0
    cos_sim.clear()
    retrieved_URL.clear()


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
                    cos_sim[doc_id] = weight[word][doc_id] * q_weight[word] / (math.sqrt(doc_len[doc_id]) * math.sqrt(q_len))
                else:
                    cos_sim[doc_id] += weight[word][doc_id] * q_weight[word] / (math.sqrt(doc_len[doc_id]) * math.sqrt(q_len))
    return cos_sim

def get_pr_query(pr_scores, query):
    q_words = query.split()
    total_scores = dict()
    for i in q_words:
        for doc in pr_scores.keys():
            total_scores[doc] = 0
            if i in pr_scores[doc].keys():
                total_scores[doc] += pr_scores[doc][i]
    return total_scores

def combine_res(cos_sim, pr_res):
    combinedScores = dict()
    for k in cos_sim.keys():
        if k in pr_res.keys():
            combinedScores[k] = 2*(cos_sim[k] * pr_res[k]) / (cos_sim[k] + pr_res[k])
    return combinedScores

def get_URL(key):
    with open(urlpath + 'URLs.txt') as f:
        for i, line in enumerate(f):
            if i == int(key)-1:
                return line.replace("\n","")

def Query(query):
    print("Loading")
    retrieved_URL = dict()
    query = process_q(query)
    q_index(query)
    cal_q_weights()
    cos_sim = cosine_sim()
    cos_sim = dict(collections.Counter(cos_sim).most_common(c))
    pr_res = get_pr_query(pr_scores, query)
    pr_res = dict(collections.Counter(pr_res).most_common(c))
    final_res = combine_res(cos_sim,pr_res)
    final_res = dict(collections.Counter(final_res).most_common(1000))
    for key,value in final_res.items():
        file_name = key.split('.')
        retrieved_URL[file_name[0]] = get_URL(file_name[0])
    print("Retrieved")
    return retrieved_URL

class Example(Frame):

    def __init__(self):
        super().__init__()
        area = ""
        e1 = ""
        hyperlink = ""
        self.initUI()


    def callback(self,url):
        webbrowser.open_new(url)

    def q(self,string):
        self.res = Query(self.e1.get())

    def search(self):
        ClearQElements()
        self.area.delete("1.0",self.END)
        self.page = 0
        print("onclick"+self.e1.get())
        res = Query(self.e1.get())
        #res = dict(collections.Counter(res).most_common(10))
        self.res_list = list(res.values())
        if self.page == 0:
            ind = 0

        if len(self.res_list) >= ind:
            ind = (self.page + 10) - 1
        else:
            ind = (len(self.res_list)) - 1
        count = 1
        while ind >= 0 and count <= 10:
            self.area.insert("1.0",self.res_list[ind], ('link', str(0)))
            self.area.insert("1.0","\n\n", ('link', str(0)))
            self.area.tag_config('link', foreground="blue")
            self.area.tag_bind('link', '<Button-1>', lambda e: self.callback(self.res_list[ind]))
            ind -= 1
            count += 1

    def next(self):
        self.area.delete("1.0",self.END)
        self.page = self.page + 10
        ind = 0
        if len(self.res_list) >= ind:
            ind = (self.page + 10) - 1
        else:
            ind = len(self.res_list) - 1
        count = 1
        while ind >= 0 and count <= 10:
            self.area.insert("1.0",self.res_list[ind], ('link', str(0)))
            self.area.insert("1.0","\n\n", ('link', str(0)))
            self.area.tag_config('link', foreground="blue")
            self.area.tag_bind('link', '<Button-1>', lambda e: self.callback(self.res_list[ind]))
            ind -= 1
            count += 1

    def prev(self):
        self.area.delete("1.0",self.END)
        self.page = self.page - 10
        ind = 0
        if len(self.res_list) >= ind:
            ind = (self.page + 10) - 1
        else:
            ind = len(self.res_list) - 1
        count = 1
        while ind >= 0 and count <= 10:
            self.area.insert("1.0",self.res_list[ind], ('link', str(0)))
            self.area.insert("1.0","\n\n", ('link', str(0)))
            self.area.tag_config('link', foreground="blue")
            self.area.tag_bind('link', '<Button-1>', lambda e: self.callback(self.res_list[ind]))
            ind -= 1
            count += 1

    def exit(self):
        self.quit()


    def initUI(self):
        self.page = 0
        self.res_list = list()
        self.master.title("Web Search Engine")
        self.pack(fill=BOTH, expand=True)
        self.END = END
        self.style = Style()
        self.style.theme_use("default")

        self.columnconfigure(1, weight=1)
        self.columnconfigure(3, pad=7)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(5, pad=7)

        lbl = Label(self, text="URL")
        lbl.grid(sticky=W, pady=4, padx=5)

        self.area = Text(self, cursor="hand2")
        #self.hyperlink = tkHyperlinkManager.HyperlinkManager(self.area)
        self.area.grid(row=1, column=0, columnspan=2, rowspan=5,
                  padx=8, sticky=E + W + S + N)

        Label(self, text="Enter Query below").grid(row = 1 ,column=4)
        self.e1 = Entry(self,width=40)
        self.e1.grid(row=2, column=4)



        abtn = Button(self, text="NEXT",command=self.next)
        abtn.grid(row=3, column=5, padx=4)

        cbtn = Button(self, text="PREV", command=self.prev)
        cbtn.grid(row=3, column=3, padx=4, pady=4)

        hbtn = Button(self, text="SEARCH", command=self.search)
        hbtn.grid(row=3, column=4, padx=5)

        obtn = Button(self, text="Exit", command=self.exit)
        obtn.grid(row=4, column=5)




def main():
    root = Tk()
    root.geometry("850x550")
    #root.geometry("750x450+300+500")
    app = Example()
    root.mainloop()


if __name__ == '__main__':
    main()

# > from Tkinter import *
# > master = Tk()
# >
# > LINKS=("http://www.python.org", "http://www.heaven.com")
# >
# > def showLink(event):
# >     idx= int(event.widget.tag_names(CURRENT)[1])
# >     print LINKS[idx]
# >
# > txt=Text(master)
# > txt.pack(expand=True, fill="both")
# > txt.insert(END, "Press ")
# > txt.insert(END, "here ", ('link', str(0)))
# > txt.insert(END, "for Python. Press ")
# > txt.insert(END, "here ", ('link', str(1)))
# > txt.insert(END, "for Heaven.")
# > txt.tag_config('link', foreground="blue")
# > txt.tag_bind('link', '<Button-1>', showLink)
# >
# > master.mainloop()

# from tkinter import *
# from PIL import Image,ImageTk

# window = Tk()
#
# window.title("UIC Web Search Engine")
# #Fit on screen
# width, height = window.winfo_screenwidth(), window.winfo_screenheight()
# window.geometry('%dx%d+0+0' % (width,height))
# #Adding image
# label = Label(window)
# img = Image.open(r"uic.png").resize((100, 100), Image.ANTIALIAS)
# label.img = ImageTk.PhotoImage(img)
# label['image'] = label.img
# label.pack()
#
# frame1 = Frame(window, width=100, height=100, background="bisque")
#
# frame1.pack(fill=None, expand=FALSE)
#
# frame = Frame(window)
# frame.pack()
#
# greenbutton = Button(frame, text="PREV", fg="brown",padx=10, pady=10)
# greenbutton.pack( side = LEFT )
#
# bluebutton = Button(frame, text="NEXT", fg="blue",ipadx=10, ipady=10)
# bluebutton.pack( side = LEFT )
#
# window.mainloop()

import matplotlib.pyplot as plt
import scipy
from wordcloud import WordCloud

import plotly.plotly as py
from plotly.graph_objs import *

import numpy as np

import nltk, hashlib, math, datetime
from nltk.stem.porter import *
from collections import Counter


import pymongo
client = pymongo.MongoClient()
db = client.morpheus

ME = 'Harry Rickards'
FOCUS_USERS = ['Jasmeet Arora', 'Emilio Pace', 'Robby Vasen', 'Camilo Espinosa']

WEEKDAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

import redis
import cPickle as pickle
class Cache:
    def __init__(self, host='localhost', port=6379, db=0):
        self.r = redis.StrictRedis(host=host, port=port, db=db)

    def get(self, key):
        raw = self.r.get(key)
        if raw == None: return None
        return pickle.loads(raw)

    def set(self, key, obj):
        return self.r.set(key, pickle.dumps(obj))

import sys, unicodedata
from nltk.corpus import stopwords
# full text corpus
class Corpus:
    # punctuation to remove
    PUNCTUATION_TBL = dict.fromkeys(i for i in xrange(sys.maxunicode) if unicodedata.category(unichr(i)).startswith('P'))

    def __init__(self, text, cache):
        self.text = text
        # for caching
        self.hash = hashlib.md5(self.text.encode('utf-8')).hexdigest()
        self.cache = cache

    # create from list of threads
    @classmethod
    def from_threads(cls, threads, cache):
        text = " ".join(message['text'] for thread in threads for message in thread['messages'])
        return cls(text, cache)

    # create with all threads containing a specific user, optionally including group
    # chats
    # @classmethod(cls, user):

    # tokenize into words, removing non-alpha chars
    def tokenize(self):
        # cache with self.hash
        cache_key = 'corpus_tokenize_' + self.hash

        self.tokens = self.cache.get(cache_key)
        if self.tokens == None:
            alphas = self.text.translate(self.PUNCTUATION_TBL)
            self.tokens = nltk.word_tokenize(alphas)[:10]
            self.cache.set(cache_key, self.tokens)

    # remove stopwords
    def remove_stopwords(self):
        if self.tokens == None: raise ValueError('Needs to be tokenized first!')

        # cache with self.hash
        cache_key = 'corpus_stopwords_' + self.hash

        self.filtered_tokens = self.cache.get(cache_key)
        if self.filtered_tokens == None:
            self.filtered_tokens = [w for w in self.tokens if not w.lower() in stopwords.words('english')]
            self.cache.set(cache_key, self.filtered_tokens)

    # downcase words and stem
    def stem(self):
        if self.filtered_tokens == None: raise ValueError('Stopwords need to be filtered first!')

        # cache with self.hash
        cache_key = 'corpus_stem_' + self.hash

        self.stemmed_tokens = self.cache.get(cache_key)
        if self.stemmed_tokens == None:
            self.stemmed_tokens = 
            self.cache.set(cache_key, self.stemmed_tokens)



cache = Cache()
c = Corpus.from_threads(db.threads.find(), cache)
c.tokenize()
c.remove_stopwords()
print c.tokens
print c.filtered_tokens

def stemmed(tokens):
    stemmer = PorterStemmer()
    stemmed = []
    for item in tokens:
        s = stemmer.stem(item)
        if r.get('stemmed_' + s) == None:
            r.set('stemmed_' + s, item)
            stemmed.append(item)
        else:
            stemmed.append(r.get('stemmed_' + s))
    return stemmed

def corpus_from_threads(threads, user):
    corpus = ""
    for thread in threads:
        messages = thread['messages']
        if user != None: messages = filter(lambda m: m['user'] == user, messages)
        corpus += " " + " ".join(map(lambda m: m['text'], messages))
    return corpus

def tokenize(corpus):
    corpus = corpus.lower()
    no_punctuation = corpus.translate(PUNCTUATION_TBL)
    tokens = nltk.word_tokenize(no_punctuation)
    return tokens

def without_stopwords(tokens):
    return [w for w in tokens if not w in stopwords.words('english')]

def process_corpus(corpus):
    key = 'processed_' + hashlib.md5(corpus.encode('utf-8')).hexdigest()
    if r.get(key) == None:
        p = stemmed(without_stopwords(tokenize(corpus)))
        r.set(key, pickle.dumps(p))
        return p
    else:
        return pickle.loads(r.get(key))

def wordcloud_from_frequencies(frequencies, filename):
    wordcloud = WordCloud(
            font_path='./droid_sans_mono.ttf',
            width=2000,
            height=1000
        ).generate_from_frequencies(frequencies)
    wordcloud.to_file(filename)

def generate_wordcloud(threads, slug, user):
    corpus = corpus_from_threads(threads, user)
    tokens = process_corpus(corpus)
    frequencies = Counter(tokens).most_common(250)
    wordcloud_from_frequencies(frequencies, 'plots/wordcloud_' + slug + '.png')


def generate_wordclouds():
    generate_wordcloud(db.threads.find(), 'me', ME)
    for user in FOCUS_USERS:
        slug = user.split(' ')[0].lower()
        generate_wordcloud(db.threads.find(), slug, user)


def users():
    threads = db.threads.find()
    uls = map(lambda t: t['users'], threads)
    return list(set(user for l in uls for user in l))

def generate_tfidf(threads, slug, user, documents):
    corpus = corpus_from_threads(threads, user)
    tokens = process_corpus(corpus)
    frequencies = Counter(tokens)

    num_docs = len(documents)
    tfidfs = []
    for token, freq in Counter(tokens).items():
        # see http://en.wikipedia.org/wiki/Tf%E2%80%93idf
        tf = freq
        docs_containing_token = len(filter(lambda document: document[token] > 0, documents))
        idf = math.log(num_docs / (1.0 + docs_containing_token))
        
        tfidfs.append((token, tf * idf))
    frequencies = sorted(tfidfs, key=lambda (token, tfidf): tfidf, reverse=True)[:250]
    wordcloud_from_frequencies(frequencies, 'plots/wordcloud_tfidf_' + slug + '.png')

def generate_tfidfs():
    if r.get('doc_freqs') == None:
        documents = []
        for user in users():
            print "Calculating document frequencies for " + user
            corpus = corpus_from_threads(db.threads.find(), user)
            tokens = process_corpus(corpus)
            documents.append(Counter(tokens))
        r.set('doc_freqs', pickle.dumps(documents))
    else:
        documents = pickle.loads(r.get('doc_freqs'))

    generate_tfidf(db.threads.find(), 'me', ME, documents)
    for user in FOCUS_USERS:
        slug = user.split(' ')[0].lower()
        generate_tfidf(db.threads.find(), slug, user, documents)
    
def generate_favourites_over_time(groups, top_users, chunk):
    counters = {}
    for user in users():
        if user == ME: next
        threads = db.threads.find({'users': user})
        counter = Counter([])
        for thread in threads:
            if groups or len(thread['users']) < 3:
                dates = map(lambda m: m['time'].date(), thread['messages'])
                counter = counter + Counter(dates)
        counters[user] = counter
    global_counter = reduce(lambda c1, c2: c1+c2, counters.values())

    if top_users:
        top_users = filter(lambda u: u != ME, users())
        top_users = sorted(top_users, key=lambda u: sum(counters[u].values()), reverse=True)[:7]

    dates = [list(set(counter)) for counter in counters.values()]
    dates = list(set(date for l in dates for date in l))
    start_date = min(dates)
    end_date = max(dates)
    num_days = (end_date + datetime.timedelta(days=1) - start_date).days

    date_labels = []
    dates = []
    for delta in range(num_days/chunk):
        date = start_date + datetime.timedelta(days=chunk*delta)
        dates.append(date)

    def calc_vals(counter):
        vals = map(lambda d: reduce(lambda c1, c2: c1+c2, map(lambda i: counter[d+datetime.timedelta(days=chunk*i)], range(chunk))), dates)
        vals = map(lambda v: v*1.0/chunk, vals)
        return vals

    if top_users:
        scatter_list = []
        for user in top_users:
            scatter_list.append(Scatter(
                x=dates,
                y=calc_vals(counters[user]),
                name=user
            ))
        data = Data(scatter_list)
    else:
        vals = calc_vals(global_counter)

        data = Data([
            Scatter(
                x=dates,
                y=vals
            )
        ])

    layout = Layout(
        autosize=False,
        width=2000,
        height=1000,
    )
    if groups:
        slug = 'daily_messages_' + str(chunk)
    else:
        slug = 'daily_messages_nogroups_' + str(chunk)
    if top_users: slug += '_users'
    plot_url = py.image.save_as({'data':data,'layout':layout}, filename='plots/' + slug + '.png')

def generate_day_of_week(user, slug):
    days = []
    threads = db.threads.find({'users': user})
    for thread in threads:
        for message in thread['messages']:
            days.append(message['time'].weekday())
    counter = Counter(days)

    vals = map(lambda i: counter[i], range(7))
    data = Data([
        Bar(
            x=WEEKDAYS,
            y=vals
        )
    ])
    layout = Layout(
        autosize=False,
        width=2000,
        height=1000,
        yaxis=YAxis(
            range=[0,max(vals)+1]
        )
    )
    plot_url = py.image.save_as({'data':data,'layout':layout}, filename='plots/weekdays_' + slug + '.png')

def generate_day_of_weeks():
    generate_day_of_week(ME, 'me')
    for user in FOCUS_USERS:
        slug = user.split(' ')[0].lower()
        generate_day_of_week(user, slug)

def generate_time_of_day(chunk):
    times = []
    threads = db.threads.find()
    for thread in threads:
        for message in thread['messages']:
            times.append(message['time'].time())
    counter = Counter(times)

    times = []
    vals = []
    for i in range(24*60/chunk):
        time = (datetime.datetime(2000,1,1,0,0,0) + datetime.timedelta(minutes=i*chunk)).time()
        times.append(time)

        vs = []
        for j in range(chunk):
            t = (datetime.datetime(2000,1,1,0,0,0) + datetime.timedelta(minutes=(i+j)*chunk)).time()
            vs.append(counter[t])
        vals.append(sum(vs)*1.0/len(vs))

    data = Data([
        Scatter(
            x=times,
            y=vals
        )
    ])

    layout = Layout(
        autosize=False,
        width=2000,
        height=1000,
        yaxis=YAxis(
            range=[0,max(vals)+1]
        )
    )
    plot_url = py.image.save_as({'data':data,'layout':layout}, filename='plots/time_' + str(chunk) + '.png')

def generate_who_initiates(user):
    TIME_DELTA = datetime.timedelta(minutes=30)
    threads = db.threads.find({'users': user})
    threads = filter(lambda t: len(t['users']) < 3 and ME in t['users'], threads)

    initiated = {ME: 0, user: 0}
    for thread in threads:
        prev_timestamp = datetime.datetime(1970, 1, 1, 0, 0)
        for message in thread['messages']:
            if abs(message['time'] - prev_timestamp) > TIME_DELTA:
                # new conversation
                initiated[message['user']] += 1

            prev_timestamp = message['time']

    # normalise
    total = initiated[ME] + initiated[user]
    initiated[ME] = initiated[ME] * 100.0 / total
    initiated[user] = initiated[user] * 100.0 / total

    return initiated

def generate_all_initiates():
    initiated = {}
    for user in FOCUS_USERS:
        initiated[user] = generate_who_initiates(user)

    me_trace = Bar(
        x = FOCUS_USERS,
        y = map(lambda user: initiated[user][ME], FOCUS_USERS),
        name = 'Me'
    )
    them_trace = Bar(
        x = FOCUS_USERS,
        y = map(lambda user: initiated[user][user], FOCUS_USERS),
        name = 'Other Person'
    )
    data = Data([me_trace, them_trace])
    layout = Layout(
        barmode='group',
        autosize=False,
        width=2000,
        height=1000
    )
    py.image.save_as({'data':data,'layout':layout}, filename='plots/who_initiates.png')



def generate_who_sends_most(user):
    threads = db.threads.find({'users': user})
    threads = filter(lambda t: len(t['users']) < 3 and ME in t['users'], threads)

    most = {ME: 0, user: 0}
    for thread in threads:
        prev_timestamp = datetime.datetime(1970, 1, 1, 0, 0)
        for message in thread['messages']:
            most[message['user']] += 1

    # normalise
    total = most[ME] + most[user]
    most[ME] = most[ME] * 100.0 / total
    most[user] = most[user] * 100.0 / total

    return most

def generate_all_sends_most():
    most = {}
    for user in FOCUS_USERS:
        most[user] = generate_who_sends_most(user)

    me_trace = Bar(
        x = FOCUS_USERS,
        y = map(lambda user: most[user][ME], FOCUS_USERS),
        name = 'Me'
    )
    them_trace = Bar(
        x = FOCUS_USERS,
        y = map(lambda user: most[user][user], FOCUS_USERS),
        name = 'Other Person'
    )
    data = Data([me_trace, them_trace])
    layout = Layout(
        barmode='group',
        autosize=False,
        width=2000,
        height=1000
    )
    py.image.save_as({'data':data,'layout':layout}, filename='plots/who_sends_most.png')



    
def generate_response_time(user):
    TIME_DELTA = datetime.timedelta(minutes=30)
    threads = db.threads.find({'users': user})
    threads = filter(lambda t: len(t['users']) < 3 and ME in t['users'], threads)

    times = {ME: [], user: []}
    for thread in threads:
        messages = thread['messages']
        for i in range(1, len(messages)):
            resp_time = abs(messages[i]['time'] - messages[i-1]['time'])
            # in same conversation and a reply to diff user
            if resp_time < TIME_DELTA and messages[i]['user'] != messages[i-1]['user']:
                times[messages[i]['user']].append(resp_time.total_seconds() / 60.0)

    return {
        ME: np.array(times[ME]),
        user: np.array(times[user])
    }


def generate_response_times():
    times = {}
    for user in FOCUS_USERS:
        times[user] = generate_response_time(user)

    me_trace = Bar(
        x = FOCUS_USERS,
        y = map(lambda user: np.mean(times[user][ME]), FOCUS_USERS),
        name = 'Me'
    )
    them_trace = Bar(
        x = FOCUS_USERS,
        y = map(lambda user: np.mean(times[user][user]), FOCUS_USERS),
        name = 'Other Person'
    )
    data = Data([me_trace, them_trace])
    layout = Layout(
        barmode='group',
        autosize=False,
        width=2000,
        height=1000
    )
    py.image.save_as({'data':data,'layout':layout}, filename='plots/response_times.png')

    
# TODO
    # sentiment analysis - dual error bars
    # response time
    # who talks about each other



# generate_wordcloduds()
# generate_tfidfs()
# for chunk in [1, 3, 5]:
    # generate_favourites_over_time(True, False, chunk, 1)
    # generate_favourites_over_time(False, False, chunk, 1)
# generate_favourites_over_time(False, True, 5)
# generate_time_of_day(60)
# generate_day_of_weeks()
# generate_all_initiates()
# generate_all_sends_most()
# generate_response_times()

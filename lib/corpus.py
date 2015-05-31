import sys, unicodedata, hashlib, nltk, math
import cPickle as pickle
from collections import Counter
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer

# full text corpus
class Corpus:
    # punctuation to remove
    PUNCTUATION_TBL = dict.fromkeys(i for i in xrange(sys.maxunicode) if unicodedata.category(unichr(i)).startswith('P'))

    def __init__(self, text, cache):
        self.text = text
        # for caching
        self.hash = hashlib.md5(self.text.encode('utf-8')).hexdigest()
        self.cache = cache

    # create from list of messages
    @classmethod
    def from_messages(cls, messages, cache):
        return cls(" ".join(message['text'] for message in messages), cache)

    # tokenize into words, removing non-alpha chars and downcasing
    def tokenize(self):
        # cache with self.hash
        cache_key = "corpus_tokenize_%s" % self.hash

        self.tokens = self.cache.get(cache_key)
        if self.tokens == None:
            alphas = self.text.lower().translate(self.PUNCTUATION_TBL)
            self.tokens = nltk.word_tokenize(alphas)
            self.cache.set(cache_key, self.tokens)

    # remove stopwords
    def remove_stopwords(self):
        if self.tokens == None: raise ValueError('Needs to be tokenized first!')

        # cache with self.hash
        cache_key = "corpus_stopwords_%s" % self.hash

        self.filtered_tokens = self.cache.get(cache_key)
        if self.filtered_tokens == None:
            self.filtered_tokens = [w for w in self.tokens if not w in stopwords.words('english')]
            self.cache.set(cache_key, self.filtered_tokens)

    # porter stem words
    def stem(self):
        if self.filtered_tokens == None: raise ValueError('Stopwords need to be filtered first!')

        # cache with self.hash
        cache_key = "corpus_stem_%s" % self.hash

        # tokens in here are not actually stemmed, but rather if word A
        # and word B both have stem X, then they are *both* stored as word A
        self.stemmed_tokens = self.cache.get(cache_key)
        if self.stemmed_tokens == None:
            stemmer = SnowballStemmer("english")
            self.stemmed_tokens = []
            for token in self.filtered_tokens:
                stemmed = stemmer.stem(token)

                # store a link from stemmed -> nonstemmed
                link_key = 'corpus_stemlink_' + stemmed
                if self.cache.get(link_key) == None:
                    self.cache.set(link_key, token)
                    self.stemmed_tokens.append(token)
                else:
                    self.stemmed_tokens.append(self.cache.get(link_key))
            self.cache.set(cache_key, self.stemmed_tokens)

    # helper method to tokenize/filter/stem
    def process(self):
        self.tokenize()
        self.remove_stopwords()
        self.stem()

    # generate counter for standard freq counts
    def counter(self):
        if self.stemmed_tokens == None: raise ValueError('Need to proccess corpus first!')
        return Counter(self.stemmed_tokens)

    # generate standard frequency counts [(word, freq)]
    def frequencies(self, limit=None):
        if limit == None:
            cache_key = "corpus_frequencies_%s" % self.hash
        else:
            cache_key = "corpus_frequencies_%s_%d" % (self.hash, limit)

        freqs = self.cache.get(cache_key)
        if freqs == None:
            if limit == None: freqs = self.counter().items()
            else: freqs = self.counter().most_common(limit)
            self.cache.set(cache_key, freqs)

        return freqs

    # generate term-frequency independent-document-frequency counts [(word, tfidf)]
    # for words frequent for that user compared to baseline
    def tfidfs(self, all_counters, limit=None):
        counter_hash = hashlib.md5(pickle.dumps(all_counters)).hexdigest()
        if limit == None:
            cache_key = "corpus_tfidfs_%s_%s" % (self.hash, counter_hash)
        else:
            cache_key = "corpus_tfidfs_%s_%s_%d" % (self.hash, counter_hash, limit)

        tfidfs = self.cache.get(cache_key)
        if tfidfs == None:
            tfidfs = []
            for token, freq in self.counter().items():
                # see an algorithm book/the internet
                term_frequency = freq
                docs_containing_token = len(filter(lambda doc: doc[token] > 0, all_counters))
                independent_doc_frequency = math.log(len(all_counters) / (1.0 + docs_containing_token))
                tfidfs.append((token, term_frequency * independent_doc_frequency))

            # order and limit
            tfidfs = sorted(tfidfs, key = lambda (token, tfidf): tfidf, reverse = True)
            if limit != None: tfidfs = tfidfs[:limit]

            self.cache.set(cache_key, tfidfs)

        return tfidfs

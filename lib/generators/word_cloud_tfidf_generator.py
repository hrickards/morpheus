import os.path, hashlib
import cPickle as pickle
from progressbar import ProgressBar
from lib.generator import Generator
from lib.corpus import Corpus
from lib.word_cloud_wrapper import WordCloudWrapper

class WordCloudTFIDFGenerator(Generator):
    name = 'wordcloud_tfidf'
    WORD_LIMIT = 250

    def pregenerate(self):
        # overriding as we have to calculate stuff for all users
        print "Generating global TFIDF data"
        pbar = ProgressBar()
        messages = self.threads.messages_by_from_user()
        users = messages.keys()
        self.counters = []

        for user in pbar(users):
            corpus = Corpus.from_messages(messages[user], self.cache)
            corpus.process()
            self.counters.append(corpus.counter())

    def generate_for_user(self, user):
        corpus = Corpus.from_messages(self.threads.messages_including_from_user(user), self.cache)
        corpus.process()

        tfidfs = corpus.tfidfs(self.counters, limit = self.WORD_LIMIT)

        # this step is slow, so don't redo it if the file already exists and the hash of tfidfs
        # hasn't changed
        filename = "%s/wordcloud_tfidf_%s.png" % (self.PLOTS_DIR, self.slug(user))
        tfidfs_hash = hashlib.md5(pickle.dumps(tfidfs)).hexdigest()
        cache_key = "wordcloudgenerator_%s" % filename
        if not (os.path.exists(filename) and self.cache.get(cache_key) == tfidfs_hash):
            self.cache.set(cache_key, tfidfs_hash)
            WordCloudWrapper.save(tfidfs, filename)


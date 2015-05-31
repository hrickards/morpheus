import os.path, hashlib
import cPickle as pickle
from lib.generator import Generator
from lib.corpus import Corpus
from lib.word_cloud_wrapper import WordCloudWrapper

class WordCloudGenerator(Generator):
    name = 'wordcloud'
    WORD_LIMIT = 250

    def generate_for_user(self, user):
        corpus = Corpus.from_messages(self.threads.messages_including_from_user(user), self.cache)
        corpus.process()

        frequencies = corpus.frequencies(limit = self.WORD_LIMIT)

        # this step is slow, so don't redo it if the file already exists and the hash of frequencies
        # hasn't changed
        filename = "%s/wordcloud_%s.png" % (self.PLOTS_DIR, self.slug(user))
        freqs_hash = hashlib.md5(pickle.dumps(frequencies)).hexdigest()
        cache_key = "wordcloudgenerator_%s" % filename
        if not (os.path.exists(filename) and self.cache.get(cache_key) == freqs_hash):
            self.cache.set(cache_key, freqs_hash)
            WordCloudWrapper.save(frequencies, filename)

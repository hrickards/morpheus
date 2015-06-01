import pymongo
from lib.cache import Cache
from lib.threads import Threads
from lib.generators.word_cloud_generator import WordCloudGenerator
from lib.generators.word_cloud_tfidf_generator import WordCloudTFIDFGenerator

# TODO import these from yaml
me = 'Harry Rickards'
focus_users = ['Jasmeet Arora', 'Emilio Pace', 'Robby Vasen', 'Camilo Espinosa'] + [me]

# connect to DB
client = pymongo.MongoClient()
db = client.morpheus

# setup app-wide singletons
cache = Cache()
threads = Threads(db, me)

from lib.generators.timeline_generator import TimelineGeneratorWrapper
TimelineGeneratorWrapper(threads, cache, me, focus_users).generate()

# generators = [
        # WordCloudGenerator,
        # WordCloudTFIDFGenerator
# ]
# for generator in generators: generator(threads, cache, me, focus_users).generate()

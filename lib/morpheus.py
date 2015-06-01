from lib.cache import Cache
from lib.threads import Threads
from lib.generators.connections_generator import ConnectionsGenerator
from lib.generators.hour_generator import HoursGenerator
from lib.generators.response_stats_generator import ResponseStatsGenerator
from lib.generators.timeline_generator import TimelineGeneratorWrapper
from lib.generators.weekday_generator import WeekdayGenerator
from lib.generators.word_cloud_generator import WordCloudGenerator
from lib.generators.word_cloud_tfidf_generator import WordCloudTFIDFGenerator

class Morpheus(object):
    generators = [
        ConnectionsGenerator,
        HoursGenerator,
        ResponseStatsGenerator,
        TimelineGeneratorWrapper,
        WeekdayGenerator,
        WordCloudGenerator,
        WordCloudTFIDFGenerator
    ]

    def __init__(self, db, me, focus_users):
        self.db = db
        self.me = me
        self.focus_users = focus_users

        # setup app-wide singletons
        self.cache = Cache()
        self.threads = Threads(self.db, self.me)

    def run(self):
        for generator in self.generators:
            generator(self.threads, self.cache, self.me, self.focus_users).generate()

import datetime
from lib.generators.time_generator import TimeGenerator
from lib.plotly_wrapper import PlotlyWrapper

# calls TimelineGenerator with different chunk lengths
# compatible with Generator api
class TimelineGeneratorWrapper():
    def __init__(self, threads, cache, me, focus_users):
        chunk_lengths = [5, 15]
        self.generators = [TimelineGenerator(threads, cache, me, focus_users, chunk_length) for chunk_length in chunk_lengths]

    def generate(self):
        for generators in self.generators: generators.generate()

# if calling directly, need to pass in chunk length
class TimelineGenerator(TimeGenerator):
    name = 'timeline'
    filename_slug = 'timeline'
    NUM_POPULAR_USERS = 10
    chunk_length = 1
    scale_factor = chunk_length

    xtitle = 'Date'
    ytitle = 'Average Number of Messages per Day'
    title = 'Messages over Time'
    overall_title = 'Most Talked To Friends over Time'

    def __init__(self, threads, cache, me, focus_users, chunk_length):
        super(TimelineGenerator, self).__init__(threads, cache, me, focus_users)
        self.chunk_length = chunk_length
        self.scale_factor = chunk_length
        self.filename_slug = "%s_%d" % (self.name, chunk_length)
        self.name = "%s %d" % (self.name, chunk_length)

    def pregenerate(self):
        # calculate users to track
        # favourite users, most talked to users
        self.users = self.focus_users + [self.me]

        all_other_users = [user for user in self.threads.users() if user != self.me]
        popular_users = sorted(all_other_users, key=lambda user: len(list(self.threads.messages_with_from_user(user))), reverse=True)
        self.users += popular_users[:self.NUM_POPULAR_USERS]

        # uniq
        self.users = list(set(self.users))

        # calculate start and end dates
        self.start = self.threads.first_message_date()
        self.end = self.threads.last_message_date()
        num_days = ((self.end - self.start).days + 1)/self.chunk_length
        self.possibilities = [self.start + datetime.timedelta(days=i*self.chunk_length) for i in range(num_days)]

    def graph_gen(self):
        return PlotlyWrapper.line

    def postgenerate(self):
        print "Generating overall %s" % self.name
        if self.me in self.vals: del self.vals[self.me]
        x = map(self.format_possibility, self.time_possibilities())
        PlotlyWrapper.line_multiple(x, self.vals, "%s/%s_overall.png" % (self.PLOTS_DIR, self.filename_slug), title=self.overall_title, xtitle=self.xtitle, ytitle=self.ytitle)

    def time_map_function(self, message):
        # we want (msg_date - start_date).days modulo chunk_length = 0
        delta = (message['time'] - self.start).days
        delta = delta - (delta % self.chunk_length)
        if delta < 0: delta += self.chunk_length
        return self.start + datetime.timedelta(days=delta)

    def time_possibilities(self):
        return self.possibilities

from collections import Counter
from lib.generator import Generator
from lib.plotly_wrapper import PlotlyWrapper

# also needs to be subclassed
class TimeGenerator(Generator):
    name = 'time'
    filename_slug = 'time'
    scale_factor = 1 # use if chunking: see TimelineGenerator
    ytitle = 'Messages Sent'
    
    # store data to potentially combine (so not user-specific) in postgenerate
    vals = {}

    def time_map_function(self, message):
        # implement in subclass
        return

    def time_possibilities(self):
        # implement in subclass
        return

    def format_possibility(self, possibility):
        # optionally implement in subclass
        return possibility

    def graph_gen(self):
        # override to change graph type
        return PlotlyWrapper.bar

    def generate_for_user(self, user):
        # if user is me, do for all messages
        # otherwise, just do for messages with user
        # this decision-making is implemented in Threads.messages_with_from_user
        messages = self.threads.messages_with_from_user(user)

        times = map(self.time_map_function, messages)
        counter = Counter(times)

        x = map(self.format_possibility, self.time_possibilities())
        y = [counter[possibility]*1.0/self.scale_factor for possibility in self.time_possibilities()]

        # store values in case we do something with them on postgenerate (see timeline_generate)
        self.vals[user] = y

        self.graph_gen()(x, y, "%s/%s_%s.png" % (self.PLOTS_DIR, self.filename_slug, self.slug(user)), title=self.title, xtitle=self.xtitle, ytitle=self.ytitle, color=self.color())

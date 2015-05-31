from collections import Counter
from lib.generator import Generator
from lib.plotly_wrapper import PlotlyWrapper

# also needs to be subclassed
class TimeGenerator(Generator):
    name = 'time'
    filename_slug = 'time'
    WEEKDAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    def time_map_function(self, message):
        # implement in subclass
        return

    def time_possibilities(self):
        # implement in subclass
        return

    def generate_for_user(self, user):
        # if user is me, do for all messages
        # otherwise, just do for messages with user
        # this decision-making is implemented in Threads.messages_with_from_user
        messages = self.threads.messages_with_from_user(user)

        times = map(self.time_map_function, messages)
        counter = Counter(times)

        x = self.time_possibilities()
        y = [counter[possibility] for possibility in self.time_possibilities()]
        PlotlyWrapper.bar(x, y, "%s/%s_%s.png" % (self.PLOTS_DIR, self.filename_slug, self.slug(user)))

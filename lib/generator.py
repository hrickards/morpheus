# subclass this
class Generator(object):
    PLOTS_DIR = './site/plots/'
    COLORS = ["#a4c2f4", "#A4F4D5", "#F4D5A4", "#F4A4C3", "#AFF4A4", "#F4B4A4", "#3D485B"]

    # Human name of generator
    name = 'plot'

    # focus users probably should include me
    def __init__(self, threads, cache, me, focus_users=None):
        self.threads = threads
        self.cache = cache
        self.me = me
        if focus_users == None: self.focus_users = [me]
        else: self.focus_users = focus_users
        self.users = self.focus_users

    def generate_for_user(self, user):
        # Implement in subclasses
        return

    # before hook
    def pregenerate(self):
        # Implement in subclasses
        return

    # after hook
    def postgenerate(self):
        # Implement in subclasses
        return

    # loop over all (by default) focus users
    def generate(self):
        self.pregenerate()
        for i in range(len(self.users)):
            user = self.users[i]
            print "Generating %s for %s" % (self.name, user.split(' ')[0])
            self.generate_for_user(user)
        self.postgenerate()

    # cycle through different colors
    color_counter = 0
    def color(self):
        self.color_counter = (self.color_counter + 1) % len(self.COLORS)
        return self.COLORS[self.color_counter]
    def colors(self, num):
        return [self.color() for i in range(num)]

    # used in filenames
    def slug(self, user):
        return user.split(' ')[0].lower()


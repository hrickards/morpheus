# subclass this
class Generator(object):
    PLOTS_DIR = './plots/'

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
        for user in self.users:
            print "Generating %s for %s" % (self.name, user.split(' ')[0])
            self.generate_for_user(user)
        self.postgenerate()

    # used in filenames
    def slug(self, user):
        return user.split(' ')[0].lower()


import math
import pygraphviz as pgv
from lib.generator import Generator

# take with a pinch of salt: if someone talks about
# "Harry" we just assume they're discussing the Harry you
# talk to most frequently
# also ignores nicknames, etc
class ConnectionsGenerator(Generator):
    name = "connections"
    users_shown = 10
    max_penwidth = 10
    SIZE = 2000
    DPI = 600

    def pregenerate(self):
        users = self.threads.users()
        sorted_users = sorted(users, key=lambda user: len(list(self.threads.messages_with_from_user(user))), reverse=True)
        self.users = list(set(sorted_users[:self.users_shown] + self.focus_users))

        # first name's we should check for
        self.names = list(set(self.slug(name) for name in self.users))
        # and corresponding most-popular users
        self.name_associations = {}
        for name in self.names:
            user = [u for u in sorted_users if self.slug(u) == name][0]
            self.name_associations[name] = user

        # graph to store connections in, and add nodes
        self.graph = pgv.AGraph(strict=False, directed=True)
        for user in self.users:
            self.graph.add_node(user)

        # find max count for weight scale factor
        max_count = 0
        for user in self.users:
            messages = " ".join(message['text'] for message in self.threads.messages_including_from_user(user))
            for name in self.names:
                count = messages.count(name) * 1.0 / len(messages)
                if count > max_count: max_count = count
        self.scale_factor = self.max_penwidth * 1.0 / max_count

    def generate_for_user(self, user):
        messages = " ".join(message['text'] for message in self.threads.messages_including_from_user(user))
        for name in self.names:
            count = messages.count(name) * 1.0 / len(messages)
            if count > 0: self.graph.add_edge(user, self.name_associations[name], penwidth=count*self.scale_factor)

    def postgenerate(self):
        inches = self.SIZE / self.DPI
        self.graph.graph_attr.update(size = "%.2f,%.2f" % (inches, inches))
        self.graph.graph_attr.update(dpi = self.DPI)
        self.graph.draw("%s/%s.png" % (self.PLOTS_DIR, self.name), prog='circo')

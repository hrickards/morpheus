import time, pymongo
from lxml import html
from datetime import datetime

class Parser(object):
    def __init__(self, db):
        self.db = db

    # stolen from SO #312443
    @classmethod
    def chunks(cls, l, n):
        """ Yield successive n-sized chunks from l.
        """
        for i in xrange(0, len(l), n):
            yield l[i:i+n]

    def parse_thread(self, thread):
        messages = []

        for child in Parser.chunks(list(thread), 2):
            message = {}
            message['user'] = child[0].xpath('.//span[@class="user"]')[0].text

            raw_time = child[0].xpath('.//span[@class="meta"]')[0].text
            global_time = time.strptime(raw_time,  "%A, %B %d, %Y at %I:%M%p %Z")
            message['time'] = datetime.fromtimestamp(time.mktime(global_time))

            message['text'] = child[1].text
            if message['text'] == None: message['text'] = ''
            messages.append(message)

        users = list(set(map(lambda m: m['user'], messages)))

        thread = {
            'users': users,
            'messages': messages
        }
        self.db.threads.insert_one(thread)

    def parse(self):
        doc = html.parse('data/html/messages.htm')
        threads = doc.xpath('//div[@class="thread"]')

        for thread in threads: self.parse_thread(thread)
        return len(threads)

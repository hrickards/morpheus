from lxml import html
import time, pymongo
from datetime import datetime

client = pymongo.MongoClient()
db = client.morpheus

db.threads.drop()

# stolen from SO #312443
def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def parse_thread(thread):
    messages = []

    for child in chunks(list(thread), 2):
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
    # print thread
    # print users
    db.threads.insert_one(thread)

doc = html.parse('data/html/messages.htm')
threads = doc.xpath('//div[@class="thread"]')

for thread in threads:
    parse_thread(thread)

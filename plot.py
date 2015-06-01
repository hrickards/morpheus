import scipy

import plotly.plotly as py
from plotly.graph_objs import *

import numpy as np

import math, datetime

        


def generate_favourites_over_time(groups, top_users, chunk):
    counters = {}
    for user in users():
        if user == ME: next
        threads = db.threads.find({'users': user})
        counter = Counter([])
        for thread in threads:
            if groups or len(thread['users']) < 3:
                dates = map(lambda m: m['time'].date(), thread['messages'])
                counter = counter + Counter(dates)
        counters[user] = counter
    global_counter = reduce(lambda c1, c2: c1+c2, counters.values())

    if top_users:
        top_users = filter(lambda u: u != ME, users())
        top_users = sorted(top_users, key=lambda u: sum(counters[u].values()), reverse=True)[:7]

    dates = [list(set(counter)) for counter in counters.values()]
    dates = list(set(date for l in dates for date in l))
    start_date = min(dates)
    end_date = max(dates)
    num_days = (end_date + datetime.timedelta(days=1) - start_date).days

    date_labels = []
    dates = []
    for delta in range(num_days/chunk):
        date = start_date + datetime.timedelta(days=chunk*delta)
        dates.append(date)

    def calc_vals(counter):
        vals = map(lambda d: reduce(lambda c1, c2: c1+c2, map(lambda i: counter[d+datetime.timedelta(days=chunk*i)], range(chunk))), dates)
        vals = map(lambda v: v*1.0/chunk, vals)
        return vals

    if top_users:
        scatter_list = []
        for user in top_users:
            scatter_list.append(Scatter(
                x=dates,
                y=calc_vals(counters[user]),
                name=user
            ))
        data = Data(scatter_list)
    else:
        vals = calc_vals(global_counter)

        data = Data([
            Scatter(
                x=dates,
                y=vals
            )
        ])

    layout = Layout(
        autosize=False,
        width=2000,
        height=1000,
    )
    if groups:
        slug = 'daily_messages_' + str(chunk)
    else:
        slug = 'daily_messages_nogroups_' + str(chunk)
    if top_users: slug += '_users'
    plot_url = py.image.save_as({'data':data,'layout':layout}, filename='plots/' + slug + '.png')

def generate_who_initiates(user):
    TIME_DELTA = datetime.timedelta(minutes=30)
    threads = db.threads.find({'users': user})
    threads = filter(lambda t: len(t['users']) < 3 and ME in t['users'], threads)

    initiated = {ME: 0, user: 0}
    for thread in threads:
        prev_timestamp = datetime.datetime(1970, 1, 1, 0, 0)
        for message in thread['messages']:
            if abs(message['time'] - prev_timestamp) > TIME_DELTA:
                # new conversation
                initiated[message['user']] += 1

            prev_timestamp = message['time']

    # normalise
    total = initiated[ME] + initiated[user]
    initiated[ME] = initiated[ME] * 100.0 / total
    initiated[user] = initiated[user] * 100.0 / total

    return initiated

def generate_all_initiates():
    initiated = {}
    for user in FOCUS_USERS:
        initiated[user] = generate_who_initiates(user)

    me_trace = Bar(
        x = FOCUS_USERS,
        y = map(lambda user: initiated[user][ME], FOCUS_USERS),
        name = 'Me'
    )
    them_trace = Bar(
        x = FOCUS_USERS,
        y = map(lambda user: initiated[user][user], FOCUS_USERS),
        name = 'Other Person'
    )
    data = Data([me_trace, them_trace])
    layout = Layout(
        barmode='group',
        autosize=False,
        width=2000,
        height=1000
    )
    py.image.save_as({'data':data,'layout':layout}, filename='plots/who_initiates.png')



def generate_who_sends_most(user):
    threads = db.threads.find({'users': user})
    threads = filter(lambda t: len(t['users']) < 3 and ME in t['users'], threads)

    most = {ME: 0, user: 0}
    for thread in threads:
        prev_timestamp = datetime.datetime(1970, 1, 1, 0, 0)
        for message in thread['messages']:
            most[message['user']] += 1

    # normalise
    total = most[ME] + most[user]
    most[ME] = most[ME] * 100.0 / total
    most[user] = most[user] * 100.0 / total

    return most

def generate_all_sends_most():
    most = {}
    for user in FOCUS_USERS:
        most[user] = generate_who_sends_most(user)

    me_trace = Bar(
        x = FOCUS_USERS,
        y = map(lambda user: most[user][ME], FOCUS_USERS),
        name = 'Me'
    )
    them_trace = Bar(
        x = FOCUS_USERS,
        y = map(lambda user: most[user][user], FOCUS_USERS),
        name = 'Other Person'
    )
    data = Data([me_trace, them_trace])
    layout = Layout(
        barmode='group',
        autosize=False,
        width=2000,
        height=1000
    )
    py.image.save_as({'data':data,'layout':layout}, filename='plots/who_sends_most.png')



    
def generate_response_time(user):
    TIME_DELTA = datetime.timedelta(minutes=30)
    threads = db.threads.find({'users': user})
    threads = filter(lambda t: len(t['users']) < 3 and ME in t['users'], threads)

    times = {ME: [], user: []}
    for thread in threads:
        messages = thread['messages']
        for i in range(1, len(messages)):
            resp_time = abs(messages[i]['time'] - messages[i-1]['time'])
            # in same conversation and a reply to diff user
            if resp_time < TIME_DELTA and messages[i]['user'] != messages[i-1]['user']:
                times[messages[i]['user']].append(resp_time.total_seconds() / 60.0)

    return {
        ME: np.array(times[ME]),
        user: np.array(times[user])
    }


def generate_response_times():
    times = {}
    for user in FOCUS_USERS:
        times[user] = generate_response_time(user)

    me_trace = Bar(
        x = FOCUS_USERS,
        y = map(lambda user: np.mean(times[user][ME]), FOCUS_USERS),
        name = 'Me'
    )
    them_trace = Bar(
        x = FOCUS_USERS,
        y = map(lambda user: np.mean(times[user][user]), FOCUS_USERS),
        name = 'Other Person'
    )
    data = Data([me_trace, them_trace])
    layout = Layout(
        barmode='group',
        autosize=False,
        width=2000,
        height=1000
    )
    py.image.save_as({'data':data,'layout':layout}, filename='plots/response_times.png')

    
# TODO
    # sentiment analysis - dual error bars
    # who talks about each other



# generate_wordcloduds()
# generate_tfidfs()
# for chunk in [1, 3, 5]:
    # generate_favourites_over_time(True, False, chunk, 1)
    # generate_favourites_over_time(False, False, chunk, 1)
# generate_favourites_over_time(False, True, 5)
# generate_time_of_day(60)
# generate_day_of_weeks()
# generate_all_initiates()
# generate_all_sends_most()
# generate_response_times()

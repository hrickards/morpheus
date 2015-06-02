import datetime
from textblob import TextBlob
from lib.generator import Generator
from lib.plotly_wrapper import PlotlyWrapper

class ResponseStatsGenerator(Generator):
    name = "response stats"
    wordlist = 'vendor/wordlist'

    CONVERSATION_THRESHOLD = datetime.timedelta(minutes=30)
    user_labels = []
    me_initiate_counts = []
    user_initiate_counts = []
    me_response_time_avgs = []
    user_response_time_avgs = []
    me_messages_counts = []
    user_messages_counts = []
    me_message_length_avgs = []
    user_message_length_avgs = []
    me_sentiments = []
    user_sentiments = []
    me_accuracies = []
    user_accuracies = []

    def pregenerate(self):
        # build fast in memory wordlist
        self.words = set(line.strip().lower() for line in open(self.wordlist))

    def generate_for_user(self, user):
        # don't want response times to ourself!
        if user == self.me: return

        # who initiates each conversation
        me_initiates = 0
        user_initiates = 0
        # average in-conversation response time
        me_response_times = []
        user_response_times = []
        # number messages
        me_message_count = 0
        user_message_count = 0
        # avg length messages
        me_message_lengths = []
        user_message_lengths = []

        me_corpus = []
        user_corpus = []

        for thread in self.threads.with_user(user):
            messages = thread['messages']
            for i in range(1, len(messages)):
                if messages[i]['user'] == self.me:
                    me_message_count += 1
                    me_message_lengths.append(len(messages[i]['text']))
                    me_corpus.append(messages[i]['text'])
                elif messages[i]['user'] == user:
                    user_message_count += 1
                    user_message_lengths.append(len(messages[i]['text']))
                    user_corpus.append(messages[i]['text'])

                resp_time = abs(messages[i]['time'] - messages[i-1]['time'])
                # new conversation
                if resp_time > self.CONVERSATION_THRESHOLD:
                    if messages[i]['user'] == self.me: me_initiates += 1
                    elif messages[i]['user'] == user: user_initiates += 1
                else:
                    # same conversation and responding to other person
                    if messages[i]['user'] != messages[i-1]['user']:
                        if messages[i]['user'] == self.me: me_response_times.append(resp_time.total_seconds()/60)
                        elif messages[i]['user'] == user: user_response_times.append(resp_time.total_seconds()/60)

        me_blob = TextBlob(" ".join(me_corpus))
        user_blob = TextBlob(" ".join(user_corpus))
        self.me_accuracies.append(len([1 for word in me_blob.words if word.lower() in self.words]) * 100.0 / len(me_blob.words))
        self.user_accuracies.append(len([1 for word in user_blob.words if word.lower() in self.words]) * 100.0 / len(user_blob.words))
        self.me_sentiments.append(me_blob.sentiment.polarity)
        self.user_sentiments.append(user_blob.sentiment.polarity)

        # normalise initiations to 100%-scale
        scale_factor = 100.0 / (me_initiates + user_initiates)
        me_initiates *= scale_factor
        user_initiates *= scale_factor

        # likewise with message counts
        scale_factor = 100.0 / (me_message_count + user_message_count)
        me_message_count *= scale_factor
        user_message_count *= scale_factor

        # average response times (std. dev too big to make useful/intersting errors
        # bars)
        me_response_time = sum(me_response_times) * 1.0 / len(me_response_times)
        user_response_time = sum(user_response_times) * 1.0 / len(user_response_times)

        # likewise with message length
        me_message_length = sum(me_message_lengths) * 1.0 / len(me_message_lengths)
        user_message_length = sum(user_message_lengths) * 1.0 / len(user_message_lengths)

        # storing in 8 separate arrays makes plotting trivial
        self.me_initiate_counts.append(me_initiates)
        self.user_initiate_counts.append(user_initiates)
        self.me_response_time_avgs.append(me_response_time)
        self.user_response_time_avgs.append(user_response_time)
        self.me_messages_counts.append(me_message_count)
        self.user_messages_counts.append(user_message_count)
        self.me_message_length_avgs.append(me_message_length)
        self.user_message_length_avgs.append(user_message_length)
        self.user_labels.append(user) # want same order

    def postgenerate(self):
        PlotlyWrapper.split_bar(self.user_labels, {
            'Me': self.me_initiate_counts,
            'Friend': self.user_initiate_counts
        }, "%s/initiates.png" % self.PLOTS_DIR,
            title="Who Initiates Conversations",
            ytitle="% initiated",
            colors=self.colors(2)
        )
        PlotlyWrapper.split_bar(self.user_labels, {
            'Me': self.me_response_time_avgs,
            'Friend': self.user_response_time_avgs
        }, "%s/response_times.png" % self.PLOTS_DIR,
            title="Average Response Time",
            ytitle="Response Time (minutes)",
            colors=self.colors(2)
        )
        PlotlyWrapper.split_bar(self.user_labels, {
            'Me': self.me_messages_counts,
            'Friend': self.user_messages_counts
        }, "%s/message_counts.png" % self.PLOTS_DIR,
            title="Message Counts",
            ytitle="Number of Messages (% of conversation)",
            colors=self.colors(2)
        )
        PlotlyWrapper.split_bar(self.user_labels, {
            'Me': self.me_message_length_avgs,
            'Friend': self.user_message_length_avgs
        }, "%s/message_lengths.png" % self.PLOTS_DIR,
            title="Average Message Length",
            ytitle="Message Length (characters)",
            colors=self.colors(2)
        )
        PlotlyWrapper.split_bar(self.user_labels, {
            'Me': self.me_sentiments,
            'Friend': self.user_sentiments
        }, "%s/message_sentiments.png" % self.PLOTS_DIR, epsilon=0.025,
            title="Message Sentiment",
            ytitle="Polarity (higher = happier, lower = sadder)",
            colors=self.colors(2)
        )
        PlotlyWrapper.split_bar(self.user_labels, {
            'Me': self.me_accuracies,
            'Friend': self.user_accuracies
        }, "%s/message_accuracies.png" % self.PLOTS_DIR, show_zero=False,
            title="Typing Accuracies",
            ytitle="% Accuracy",
            colors=self.colors(2)
        )

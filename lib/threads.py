class Threads:
    def __init__(self, db, me):
        self.db = db
        self.me = me

    def with_user(self, user):
        if user == self.me: return self.db.threads.find()

        return self.db.threads.find({
            '$or': [
                { 'users': [user, self.me] },
                { 'users': [self.me, user] }
            ]
        })

    # flattened version of the above
    def messages_with_user(self, user):
        threads = self.with_user(user)
        return (message for thread in threads for message in thread['messages'])

    # only sent from user, not to
    def messages_with_from_user(self, user):
        threads = self.with_user(user)
        return (message for thread in threads for message in thread['messages'] if message['user'] == user)

    def including_user(self, user):
        return self.db.threads.find({ 'users': user })

    # flattened version of the above
    def messages_including_user(self, user):
        threads = self.including_user(user)
        return (message for thread in threads for message in thread['messages'])

    # only sent from user, not to
    def messages_including_from_user(self, user):
        threads = self.including_user(user)
        return (message for thread in threads for message in thread['messages'] if message['user'] == user)

    # all users
    def users(self):
        all_threads = self.db.threads.find()
        user_lists = (thread['users'] for thread in all_threads)
        return list(set(user for user_list in user_lists for user in user_list))

    # all users and the threads they've spoken in
    def by_user(self):
        threads = {}
        for user in self.users():
            threads[user] = self.including_user(user)
        return threads

    # above flattened into messages
    def messages_by_user(self):
        messages = {}
        for user in self.users():
            messages[user] = self.messages_including_user(user)
        return messages

    # only sent from user, not to
    def messages_by_from_user(self):
        messages = {}
        for user in self.users():
            messages[user] = self.messages_including_from_user(user)
        return messages

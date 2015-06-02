from mako.template import Template

class Output(object):
    def __init__(self, me, friends):
        self.me = self.format_user(me)
        friends = [me] + list(set(friend for friend in friends if friend != me))
        self.friends = map(self.format_user, friends)

    # stolen from SO #312443
    def chunks(self, l, n):
        """ Yield successive n-sized chunks from l.
        """
        for i in xrange(0, len(l), n): yield l[i:i+n]


    def format_user(self, user):
        first = user.split(" ")[0]
        return {
            'name': first,
            'slug': first.lower(),
            'owner': first + "'s" # TODO: do this properly
        }

    def render(self):
        main_tpl = Template(filename='./templates/index.html')
        with open('./site/index.html', 'w') as f: f.write(main_tpl.render(me=self.me, friends=self.friends, chunks=self.chunks).encode('utf8'))

        results_tpl = Template(filename='./templates/results.html')
        with open('./site/results.html', 'w') as f: f.write(results_tpl.render(me=self.me, friends=self.friends, chunks=self.chunks).encode('utf8'))

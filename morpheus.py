import os, pymongo, webbrowser
from clint.textui import colored, puts
from lib.parser import Parser
from lib.morpheus import Morpheus

# db setup
client = pymongo.MongoClient()
db = client.morpheus
db.threads.drop()

puts('Hi there!')
puts()
puts("You can check out the results by opening " + colored.blue("output/index.html") + " in a browser (and")
puts("we've tried to open one automatically for you!")
full_path = os.path.realpath(__file__)
web_path = os.path.dirname(full_path) + "/output/index.html"
webbrowser.open(web_path)

puts("First things first, you'll need to head over to Facebook to download your data.")
puts("Go to " + colored.blue('https://www.facebook.com/settings') + " and click on ")
puts(colored.yellow('Download a copy of your Facebook data') + ". Just follow the onscreen instructions and")
puts("when you have the data, extract it into a folder called " + colored.blue("data") + " in this directory.")
puts()

puts("When you've done that, just hit enter!")
raw_input()

while not os.path.isdir('./data'):
    puts(colored.red("Oops - it looks as though you haven't put your data in the ") + colored.blue("data/") + colored.red(" folder."))
    puts("Try again, and hit enter when you're done")
    raw_input()

puts(colored.green("Great, we've got your chat data."))
puts("Now we're going to do some initial parsing of your data. This should only take")
puts("10 seconds or so.")
puts()

num_threads = Parser(db).parse()

puts(colored.green("Awesome - we managed to parse a whopping %d conversations!" % num_threads))
puts()

puts("Finally we just need to ask you a couple of quick questions. First of all, what")
puts("is " + colored.yellow("your full name on Facebook") + "? Make sure to capitalise and format this exactly")
puts("as it is on Facebook!")
me = raw_input("My Name: ")
puts()

while db.threads.find_one({ 'users': me }) == None:
    puts(colored.red("Oops - it doesn't look as though your name appears in your chat history!"))
    puts("Let's try that again!")
    me = raw_input("My Name: ")
    puts()

puts("Great! The last thing we need from you is a list of the friends you wish to")
puts("generate detailed stats about. You probably want to enter about " + colored.yellow("5 or so friends"))
puts(colored.yellow("that you message a lot") + " on Facebook. Again, make sure to enter their names")
puts("exactly as they appear on Facebook!")
puts(colored.yellow("Enter each friend's name followed by the enter key, and when you're done hit"))
puts(colored.yellow("enter on a new line"))

friends = []
last_input = raw_input()
while last_input != "":
    while db.threads.find_one({ 'users': last_input }) == None:
        puts()
        puts(colored.red("Ooops - it doesn't look as though that name appears in your chat history!"))
        puts("Let's try that again!")
        last_input = raw_input()
    friends.append(last_input)
    last_input = raw_input()
# uniq
friends = list(set(friends))
puts()

puts(colored.green("Awesome! Your job is done, now just sit back and wait while we process"))
puts(colored.green("everything.") + " This should take about 5 minutes or so, so please be patient!")

Morpheus(db, me, friends).run()

puts(colored.green("All done!"))
puts("You can check out the results by opening " + colored.blue("output/index.html") + " in a browser")

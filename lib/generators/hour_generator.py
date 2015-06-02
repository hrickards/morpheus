import datetime
from lib.generators.time_generator import TimeGenerator

class HoursGenerator(TimeGenerator):
    name = 'hours'
    filename_slug = 'hours'
    xtitle = 'Time of Day'
    ytitle = 'Total Number of Messages Sent'
    title = 'Number of Messages Sent by Hour of the Day'

    # mon = 0 as per datetime lib
    WEEKDAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    def time_map_function(self, message):
        return message['time'].hour

    def time_possibilities(self):
        return list(range(24))

    def format_possibility(self, hour):
        return datetime.time(hour, 0, 0)

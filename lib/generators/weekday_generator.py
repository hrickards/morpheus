from lib.generators.time_generator import TimeGenerator

class WeekdayGenerator(TimeGenerator):
    name = 'weekdays'
    filename_slug = 'weekdays'

    xtitle = 'Day of the Week'
    ytitle = 'Total Number of Messages Sent'
    title = 'Messages Sent by Day of the Week'

    # mon = 0 as per datetime lib
    WEEKDAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    def time_map_function(self, message):
        return self.WEEKDAYS[message['time'].weekday()]

    def time_possibilities(self):
        return self.WEEKDAYS

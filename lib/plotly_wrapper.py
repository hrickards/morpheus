import plotly.plotly as py
from plotly.graph_objs import Data, Layout, Bar, YAxis, Scatter, Line

class PlotlyWrapper:
    DEFAULT_LAYOUT = {
        'width': 2000,
        'height': 1000
    }

    def __init__(self, data, layout):
        self.data = data
        self.layout = layout

    def save(self, filename):
        py.image.save_as({'data':self.data,'layout':self.layout}, filename=filename)

    @classmethod
    def bar(cls, x, y, filename):
        data = Data([Bar(x = x, y = y)])
        layout = Layout(autosize = False, yaxis = YAxis(range = [0, max(y) + 1]), **cls.DEFAULT_LAYOUT)
        cls(data, layout).save(filename)

    @classmethod
    def split_bar(cls, x, ys, filename):
        data = Data([Bar(x = x, y = y, name=label) for (label, y) in ys.iteritems()])
        layout = Layout(autosize = False, yaxis = YAxis(range = [0, max(y) + 1]), **cls.DEFAULT_LAYOUT)
        cls(data, layout).save(filename)


    @classmethod
    def line(cls, x, y, filename):
        data = Data([Scatter(x = x, y = y, line=Line(shape='spline'))])
        layout = Layout(autosize = False, yaxis = YAxis(range = [0, max(y) + 1]), **cls.DEFAULT_LAYOUT)
        cls(data, layout).save(filename)

    @classmethod
    # data = dict of {user: data_array}
    def line_multiple(cls, x, ydata, filename):
        data = Data([Scatter(x=x, y=y, name=user, line=Line(shape='spline')) for (user, y) in ydata.iteritems()])
        max_val = max(max(y) for (user, y) in ydata.iteritems())
        layout = Layout(autosize = False, yaxis = YAxis(range = [0, max_val + 1]), **cls.DEFAULT_LAYOUT)
        cls(data, layout).save(filename)

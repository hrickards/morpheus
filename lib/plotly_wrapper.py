import plotly.plotly as py
from plotly.graph_objs import Data, Layout, Bar, YAxis

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

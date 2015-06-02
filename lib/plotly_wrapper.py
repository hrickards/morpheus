import plotly.plotly as py
from plotly.graph_objs import Data, Layout, Bar, YAxis, Scatter, Line, XAxis, Font, Marker, Legend

class PlotlyWrapper:
    def __init__(self, data, layout):
        self.data = data
        self.layout = layout

    def save(self, filename):
        py.image.save_as({'data':self.data,'layout':self.layout}, filename=filename)

    @classmethod
    def layout(cls, title, xtitle, ytitle, show_zero, min_val, max_val, epsilon):
        if show_zero:
            yaxis_options = { 'range': [0, max_val + epsilon] }
        else:
            yaxis_options = { 'range': [min_val - epsilon, max_val + epsilon] }
        return {
            'autosize': False,
            'width': 2000,
            'height': 1000,
            'title': title,
            'titlefont': Font(size=36),
            'legend': Legend(font=Font(size=36)),
            'xaxis': XAxis(
                title = xtitle,
                titlefont = Font(size=28),
                tickfont = Font(size=18)
            ),
            'yaxis': YAxis(
                title = ytitle,
                titlefont = Font(size=28),
                tickfont = Font(size=18),
                **yaxis_options
            )
        }

    @classmethod
    def bar(cls, x, y, filename, title="", xtitle="", ytitle="", epsilon=1, color = "#447adb", show_zero = True):
        data = Data([Bar(x = x, y = y, marker=Marker(color=color))])
        layout = Layout(
            **cls.layout(title, xtitle, ytitle, show_zero, min(y), max(y), epsilon)
        )
        cls(data, layout).save(filename)

    @classmethod
    def split_bar(cls, x, ys, filename, title="", xtitle="", ytitle="", epsilon=1, colors = ["#447adb", "#447adb"], show_zero = True):
        data = Data([Bar(x = x, y = ys[ys.keys()[i]], name=ys.keys()[i], marker=Marker(color=colors[i])) for i in range(len(ys.keys()))])
        min_val = min(min(y) for (label, y) in ys.iteritems())
        max_val = max(max(y) for (label, y) in ys.iteritems())
        layout = Layout(
            **cls.layout(title, xtitle, ytitle, show_zero, min_val, max_val, epsilon)
        )
        cls(data, layout).save(filename)


    @classmethod
    def line(cls, x, y, filename, title="", xtitle="", ytitle="",  epsilon=1, color = "#447adb", show_zero = True):
        data = Data([Scatter(x = x, y = y, marker=Marker(color=color), line=Line(shape='spline'))])
        layout = Layout(
            **cls.layout(title, xtitle, ytitle, show_zero, min(y), max(y), epsilon)
        )
        cls(data, layout).save(filename)

    @classmethod
    # data = dict of {user: data_array}
    def line_multiple(cls, x, ys, filename, title="", xtitle="", ytitle="", epsilon=1, show_zero = True):
        data = Data([Scatter(x=x, y=y, name=label, line=Line(shape='spline')) for (label, y) in ys.iteritems()])
        min_val = min(min(y) for (label, y) in ys.iteritems())
        max_val = max(max(y) for (label, y) in ys.iteritems())
        layout = Layout(
            **cls.layout(title, xtitle, ytitle, show_zero, min_val, max_val, epsilon)
        )
        cls(data, layout).save(filename)

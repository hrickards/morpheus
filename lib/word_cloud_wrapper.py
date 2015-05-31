from wordcloud import WordCloud

class WordCloudWrapper:
    FONT_PATH = './droid_sans_mono.ttf'
    WIDTH = 2000
    HEIGHT = 1000

    def __init__(self, frequencies):
        self.wordcloud = WordCloud(font_path=self.FONT_PATH, width=self.WIDTH, height=self.HEIGHT).generate_from_frequencies(frequencies)

    def to_file(self, filename):
        self.wordcloud.to_file(filename)

    @classmethod
    def save(cls, frequencies, filename):
        wc = cls(frequencies)
        wc.to_file(filename)

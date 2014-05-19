from frequencer.interface import BaseFilter
import time
import logging

class StopwordsFilter(BaseFilter):

    stop_words = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 
    'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 
    'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 
    'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did',
     'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 
     'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below',
      'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 
      'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 
      'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will',
       'just', 'don', 'should', 'now', "'tis", "'twas", 'able', 'across', "ain't", 'almost', 'also', 'among', "aren't", 
       "can't", 'cannot', 'could', "could've", "couldn't", 'dear', "didn't", "doesn't", "don't", 'either', 'else', 
       'ever', 'every', 'get', 'got', "hasn't", "he'd", "he'll", "he's", "how'd", "how'll", "how's", 'however', "i'd", 
       "i'll", "i'm", "i've", "isn't", "it's", 'least', 'let', 'like', 'likely', 'may', 'might', "might've", "mightn't", 
       'must', "must've", "mustn't", 'neither', 'often', 'rather', 'said', 'say', 'says', "shan't", "she'd", "she'll", 
       "she's", "should've", "shouldn't", 'since', "that'll", "that's", "there's", "they'd", "they'll", "they're", 
       "they've", 'tis', 'twas', 'us', 'wants', "wasn't", "we'd", "we'll", "we're", "weren't", "what'd", "what's", 
       "when'd", "when'll", "when's", "where'd", "where'll", "where's", "who'd", "who'll", "who's", "why'd", "why'll", 
       "why's", "won't", 'would', "would've", "wouldn't", 'yet', "you'd", "you'll", "you're", "you've", "'s", "'t", "n't"
       ,"'ve", "'d", "'ll", "'re", "'m" ]

    def __init__(self, filter=None, extra_stopwords=[]):
        super(StopwordsFilter, self).__init__(filter)
        self.extra_stopwords = extra_stopwords
        self.logger = logging.getLogger('StopwordsFilter')
        if self.extra_stopwords:
            self.stop_words = self.stop_words + self.extra_stopwords

    def process(self, words):
        start = time.time()
        result = {}
        for item in words:
            if item not in self.stop_words:
                result[item] = words[item]

        cost = (time.time() - start) * 1000.0
        self.logger.debug("process cost: %0.3f" % cost)
        return result
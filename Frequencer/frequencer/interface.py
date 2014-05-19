import time
import logging

class BaseFilter(object):
    """Base filter class"""
    def __init__(self, filter=None):
        self.chainFilter = filter
#        self.arg = arg

    def processChain(self, words):
        todo = words
        if self.chainFilter:
            todo = self.chainFilter.processChain(words)
        return self.process(todo)

    def process(self, words):
        return words



class BaseExtractor(object):
    """Base extractor class"""
    def __init__(self, extractor=None):
        self.chainExtractor = extractor

    def processChain(self, content):
        todo = content
        if self.chainExtractor:
            todo = self.chainExtractor.processChain(content)
        return self.process(todo)

    def process(self, content):
        return content


class BaseTokenizer(object):
    """Base tokenizer class"""
    def __init__(self, tokenizer=None):
        self.chainTokenizer = tokenizer

    def processChain(self, content):
        todo = None
        if self.chainTokenizer:
            todo = self.chainTokenizer.processChain(content)
        else:
            todo = self.processContent(content)

        return self.process(todo)

    def process(self, tokens):
        return tokens

    def processContent(self, content):
        pass


class BaseReducer(object):
    """Base Reducer class"""
    def __init__(self):
        self.logger = logging.getLogger('BaseReducer')
        pass

    def process(self, tokens):
        start = time.time()
        result = {}
        for item in tokens:
            if item in result:
                result[item] += 1
            else:
                result[item] = 1

        cost = (time.time() - start) * 1000.0
        self.logger.debug("Reducer cost: %0.3f" % cost)
        return result
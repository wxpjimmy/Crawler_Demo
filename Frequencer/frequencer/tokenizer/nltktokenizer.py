import nltk
from frequencer.interface import BaseTokenizer
import time
import logging

class NLTKTokenizer(BaseTokenizer):

    delimiters = ["~", "`", "!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "_", "+", "=",
                    "{", "[", "}", "]", "|", "\\", ":", ";", "\"", "<", ",", ">", ".", "?", 
                    "/", "\n", "\b", "\r", " ", "'", "-"]

    def __init__(self, tokenizer=None):
        super(NLTKTokenizer, self).__init__(tokenizer)
        self.logger = logging.getLogger('NLTKTokenizer')

    def process(self, tokens):
        start = time.time()
        result = []
        if tokens:
            result = [token for token in tokens if token not in self.delimiters]
        
        cost = (time.time() - start) * 1000.0
        self.logger.debug("Filter delimiters cost: %0.3f" % cost)
        return result

    def processContent(self, content):
        try:
            start = time.time()
            tokens = nltk.word_tokenize(content)
            cost = (time.time() - start) * 1000.0
            self.logger.debug("Token cost: %0.3f" % cost)
            return tokens
        except Exception, e:
            print e
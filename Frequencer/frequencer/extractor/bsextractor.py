from frequencer.interface import BaseExtractor
from bs4 import BeautifulSoup
import time
import logging

class BSExtractor(BaseExtractor):
    def __init__(self, extractor=None):
        super(BSExtractor, self).__init__(extractor)
        self.logger = logging.getLogger('BSExtractor')

    def process(self, content):
        start = time.time()
        soup = BeautifulSoup(content, 'lxml')
#        tmp = [s.extract() for s in soup(['style', 'script', '[document]', 'head', 'title'])]
        text = soup.getText()
        cost = (time.time() - start) * 1000.0
        self.logger.debug("Page process cost: %0.3f" % cost)
        return text
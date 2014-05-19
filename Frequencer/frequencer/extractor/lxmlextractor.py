from frequencer.interface import BaseExtractor
from lxml.html import document_fromstring
import time
import logging

class LXMLExtractor(BaseExtractor):
    def __init__(self, extractor=None):
        super(LXMLExtractor, self).__init__(extractor)
        self.logger = logging.getLogger('LXMLExtractor')

    def process(self, content):
        start = time.time()
        page = document_fromstring(content)
        text = page.cssselect('body')[0].text_content()
        cost = (time.time() - start) * 1000.0
        self.logger.debug("Page process cost: %0.3f" % cost)
        return text
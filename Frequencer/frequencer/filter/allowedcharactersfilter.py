from frequencer.interface import BaseFilter
import re
import time
import logging


class AllowedCharactersRegexFilter(BaseFilter):
    def __init__(self, filter=None):
        super(AllowedCharactersRegexFilter, self).__init__(filter)
        self.allowed_pattern = re.compile(r'^[0-9a-zA-Z\.\-\_\,]+$')
        self.logger = logging.getLogger('AllowedCharactersRegexFilter')

    def process(self, words):
        start = time.time()
        toremove=[]
        for item in words:
            if not self.allowed_pattern.match(item):
                toremove.append(item)

        for item in toremove:
            del words[item]

        cost = (time.time() - start) * 1000.0
        self.logger.debug("process cost: %0.3f" % cost)
        return words
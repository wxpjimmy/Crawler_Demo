from frequencer.interface import BaseFilter
import re
import time
import logging


class BaseRegexFilter(BaseFilter):
    def __init__(self, filter=None, regToFunc={}, loggername='BaseRegexFilter'):
        super(BaseRegexFilter, self).__init__(filter)
        self.regToFunc = regToFunc #{r"[\w0-9]*\.$", lambda x: x[0:-1]}
        self._regpattern = {}
        self.logger = logging.getLogger(loggername)
        for item in self.regToFunc:
            self._regpattern[item] = re.compile(item)

    def process(self, words):
        if self.regToFunc:
            start = time.time()
            toremove=[]
            toadd={}

            for item in words:
                for key in self.regToFunc:
                    ptn = self._regpattern[key]
                    if ptn.match(item):
                        count = words[item]
                        toremove.append(item)
                        if self.regToFunc[key]:
                            changed = self.regToFunc[key](item)
                            if changed:
                                if changed in toadd:
                                    toadd[changed] = toadd[changed] + count
                                else:
                                    toadd[changed] = count
                        break
            """
            for k in self.regToFunc:
                ptn = re.compile(k)
                for item in words:
                    if ptn.match(item):
                        count = words[item]
                        toremove[item] = count
                        changed = self.regToFunc[k](item)
                        if changed:
                            if changed in toadd:
                                toadd[changed] = toadd[changed] + count
                            else:
                                toadd[changed] = count
            """
            for item in toremove:
                del words[item]
            for item in toadd:
                if item in words:
                    words[item] = words[item] + toadd[item]
                else:
                    words[item] = toadd[item]

            cost = (time.time() - start) * 1000.0
            self.logger.debug("process cost: %0.3f" % cost)
            return words
        else:
            return words


class DotRemoveRegexFilter(BaseRegexFilter):
    def __init__(self, filter=None):
        super(DotRemoveRegexFilter, self).__init__(filter, {r"[\w0-9]*\.$": lambda x: x[0:-1]}, 'DotRemoveRegexFilter')


class TotalRegexFilter(BaseRegexFilter):

    patterns = {r'^[0-9\.\,\:]+$': None}

    def __init__(self, filter=None):
        super(TotalRegexFilter, self).__init__(filter, self.patterns, 'TotalRegexFilter')
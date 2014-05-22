"""tool used to generate query data for accuracy test from wikipedia data """

from bz2 import BZ2File
import random
import json
from extract import parsewpxml
import sys
import os

class TestDataGenerator(object):

    def __init__(self, max_span, goal):
        self.count = 0
        self.dic = {}
        self.sampledic = {}
        self.max_span=max_span
        self.target = 0
        self.find = 0
        self.goal = goal

    def page_handler(self, page):
        print(self.target)
#        print(json.dumps(self.sampledic))
        if self.target == 0:
            self.target += random.randint(1, self.max_span)
        for rev in page['revisions']:
            if rev is not None:
                title = page['title']
                content = rev.get('text')
                if content is not None:
                    self.count += 1
                    if self.count == self.target:
                        self.dic[title] = content
                        length = len(content)
                        pos = random.randint(int(length*0.1), int(length*0.2))
                        end = pos + 100
                        testdata = content[pos:end]
                        if len(testdata.strip()) < 20:
                            self.target += 1
                            print("Empty: %d, len: %d" % (self.count, len(testdata.strip())))
                        else:
                            self.sampledic[title] = testdata
                            self.find += 1
                            if self.find == self.goal:
                                path = os.path.dirname(__file__)
                                origin_path = os.path.join(path, 'original.txt')
                                sample_path = os.path.join(path, 'sample.txt')
                                p = json.dumps(self.dic)
                                s = json.dumps(self.sampledic)
                                filehandle = open(origin_path, 'w')
                                filehandle.write(p)
                                filehandle.close()
                                sample = open(sample_path, 'w')
                                sample.write(s)
                                sample.close()
                                raise Exception("Find is done")
                            else:
                                self.target += random.randint(1, self.max_span)

    def get_test_data(self, total, num, FILE):
        self.max_span = total/num
        self.goal = num
        parsewpxml(FILE, self.page_handler)

    def reset(self):
        self.count = 0
        self.dic = {}
        self.sampledic = {}
        self.max_span=10
        self.target = 0
        self.find = 0
        self.goal = 0

def main(argv=None, input=sys.stdin):
    p = TestDataGenerator(100, 10000)
#    p.get_test_data(1000000, 10000, input)
    parsewpxml(input, p.page_handler)

if __name__ == '__main__':
    main()

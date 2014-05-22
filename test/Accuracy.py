from ElasticsearchClient import ES
import json
import sys
import os

class SearchAccuracyTest(object):
    def __init__(self, hosts, index=None, doc_type=None):
        self.es = ES(hosts)
        self.index = index
        self.cost = 0
        self.min_cost = 10000000
        self.max_cost = -1
        self.doc_type = doc_type

    def test(self, FILE, index=None, doc_type=None):
        reload(sys)
        sys.setdefaultencoding('utf-8')
        f = open(FILE)
        content = f.read()
        f.close()
        data = json.loads(content)
        most_match = 0
        top3_match = 0
        top5_match = 0
        no_result = 0
        fail = 0
        failed={}
        empty={}
        item_count=0
        i = index or self.index
        t = doc_type or self.doc_type
        for (title, page) in data.items():
           res = self.get_most_matched(page, i, t)
           item_count += 1
           if res is None:
               no_result += 1
               empty[title] = page
#               print 'fail-empty'
           elif res[0] == title:
               most_match += 1
#               print 'match'
           elif title in res[0:3]:
               top3_match += 1
           elif title in res:
               top5_match += 1
           else:
               fail += 1
               failed[title] = page
#               print 'fail'

        print("succeed: (first-match: %d, top3-match: %d, top5-match: %d), fail-empty: %d, fail: %d" % (most_match, top3_match, top5_match, no_result, fail))
        print("Totalcost: %d, avg: %d, max: %d, min: %d" % (self.cost, self.cost/item_count, self.max_cost, self.min_cost)) 
        filehandler = open('result.txt', 'w')
        filehandler.write("Result empty:" + '\n')
        for (title, page) in empty.items():
            filehandler.write(title + ":  " + page + '\n')
        filehandler.write('\n\n\nResult Wrong:\n') 
        for (title, page) in failed.items():
            filehandler.write(title + ":  " + page + '\n')
        filehandler.close()


    def get_most_matched(self, content, index, doc_type):
        result = self.es.search_index_type(index, doc_type, content, True)
        data = result['result']
        ct = int(result['cost'])
        print ct
        self.cost += ct
        if ct < self.min_cost:
            self.min_cost = ct
        elif ct > self.max_cost:
            self.max_cost = ct
        else:
            pass
        res = []
        if data == []:
            return None
        else:
            for item in data:
                res.append(item['url'])

            return res


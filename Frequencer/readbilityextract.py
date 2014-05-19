from readability.readability import Document
import json

def timeit(func):
    def wrap(*args):
        time1 = time.time()
        ret = func(*args)
        time2 = time.time()
        cost = (time2-time1)*1000.0
        log.msg('%s function took %0.3f ms' % (func.func_name, cost), log.DEBUG)
        # should replace the printing with record to StatsD(categorized by func_name)
#        datadog.gauge('crawler.es.bulk.index.cost', cost)
        return ret
    return wrap


@timeit
def extract(content):
    return Document(content).summary()


log = 'Consumer-0.log'
dic = {}
row = 0
with open(log, 'r+') as handler:
    lines = handler.readlines()
    for line in lines:
        words = json.loads(line)
        print(len(words))
        for key in words:
            if key not in dic:
                dic[key] = words[key]
            else:
                dic[key] = dic[key] + words[key]

for item in dic:
    print(item + ", " + str(dic[item]))

print len(dic)
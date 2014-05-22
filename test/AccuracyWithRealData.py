import json
from utils import search_accuracy_test
from ElasticsearchClient import ES
import time
import sys

index = 'prod'
doc_type = 'test'
c_file = "round_0_queries.jsons"

if len(sys.argv) > 1:
    c_file = sys.argv[1]

if len(sys.argv) > 2:
    index = sys.argv[2]

if len(sys.argv) > 3:
    doc_type = sys.argv[3]

es = ES({"localhost":9200}, index, doc_type)

data = map(json.loads, open(c_file))

extracted = []

fail_crawl = []

for item in data:
    tmp = {}
    tmp['url'] = item['url']
    qy = item['queries']
    qy.sort(cmp=lambda x,y:cmp(len(x), len(y)))
    tmp['queries'] = qy
    tmp['id'] = item['id']
    extracted.append(tmp)
    try:
        es.index_url(item['url'])
    except Exception, e:
        fail_crawl.append(item['url'])

print("failed cound: %d" % len(fail_crawl))

failed = open('fail_crawl.txt', 'w+')
for item in fail_crawl:
    failed.write(item + '\n')

failed.close()

time.sleep(30)

re_handle = open('Prod_test.txt', 'w+')

first_match = 0
top3_match = 0
top5_match = 0
fail_empty = 0
fail_not_empty = 0
num = 0

for item in extracted:
    url_id = item['id']
    url = item['url']
    if url in fail_crawl:
        num += 1
        pass
    else:
        resp_code = []
        for query in item['queries']:
            result = {}
            length = len(query)
            count = len(query.strip().split(" "))
            ans = search_accuracy_test(es, query, url)
            print ans
            resp_code.append(ans)
            result['id'] = url_id
            result['url'] = url
            result['q_len'] = length
            result['q_w_len'] = count
            result['match']=ans
#        result['q'] = query
            txt = json.dumps(result)
            re_handle.write(txt + '\n')

        if 'first_match' in resp_code:
            first_match += 1
        elif 'top3_match' in resp_code:
            top3_match += 1
        elif 'top5_match' in resp_code:
            top5_match += 1
        elif 'fail_not_empty' in resp_code:
            fail_not_empty += 1
        else:
            fail_empty += 1
print num
print("total: %d, first: %d, top3: %d, top5: %d, fail_not_empty: %d, fail_empty: %d, fail_crawl: %d" % (len(data), first_match, top3_match, top5_match, fail_not_empty, fail_empty, len(fail_crawl)))
re_handle.close()

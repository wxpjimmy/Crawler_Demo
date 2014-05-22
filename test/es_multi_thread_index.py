from ElasticsearchClient import ES
from utils import timeit
from extract import parsewpxml
from Queue import Queue
import time
from threading import Thread
import os
from bz2 import BZ2File
import sys

q = Queue(1000)
num_threads = 50
es = ES({"localhost":"9200"}, 'speed50', 'perf')
total = 0

def test_handler(page):
    pass


def page_handler(page):
    """Write the right bits to the right files."""
    global total
    if total == 10000:
        total += 1
        print("End: %f" % (time.time()))
        pass
    elif total > 10000:
#        if q.empty():
#            raise Exception("finished processing")
#        else:
         pass
#    elif total < 251848:
#        total += 1
#        pass
    else:
        for rev in page['revisions']:
            if rev is not None:
                text = rev.get('text')
                if text is not None:
                    q.put([page['title'], rev['text']])
                    total += 1

def Worker():
    count = 0
    size = 0
    start = time.time()
    while True:
        try:
            print q.qsize()
            item = q.get(block=True, timeout=60)
            es.index(item[0], item[1])
            count += 1
            size += len(item[1])
            q.task_done
            if count%10 == 0:
                print("index-Num: %d" % (count))
        except Exception, e:
            print e
            break
    end = time.time() - 60
    cost = end - start
    print("Finishe processing count: %d, datasize: %d, start: %f--stop: %f, cost: %f" % (count, size, start, end, cost))

def main(argv=None, input=sys.stdin):
#    FILE = os.path.join(os.path.dirname(__file__), 'test.xml')
#    path =  os.path.join(os.path.dirname(__file__), 'test.xml.bz2')
#path =  os.path.join(os.path.dirname(__file__), 'enwiki-20140203-pages-articles-multistream.xml.bz2')
    threads = []
    for i in range(num_threads):
        t = Thread(target=Worker)
        t.daemon = True
        threads.append(t)
        t.start()
    print("Start: %f" %  (time.time()))
    parsewpxml(input, page_handler)
    while 1:
        alive = False
        for thread in threads:
            alive = alive or thread.isAlive()
            if alive:
                break
        if not alive:
            self.logger.info("All threads have been successfully stopped!")
            break
        else:
            self.logger.info("Runing......")
            time.sleep(3)

if __name__ == '__main__':
    main()

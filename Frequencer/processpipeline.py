import importlib
import redis
from settings import *
from Queue import Queue
import time
import signal
import json
import os
from threading import Thread
from frequencer.dbadapter import DBAdapter
import logging
from datetime import datetime
from frequencer.monitors import datadog
import ast

curtime = datetime.utcnow()

logfile = "frequencer_%s.log" % curtime

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

logging.basicConfig(filename = os.path.join(LOG_DIR, logfile), level = logging.DEBUG)

class ConsumerTask(Thread):
    def __init__(self, queue, build_processor, threadname):
#        Thread.__init__(self)
        super(ConsumerTask, self).__init__(name = threadname)
        self.logger = logging.getLogger('ConsumerTask-' + threadname)
        self._queue = queue
        self._tokenizer = build_processor(TOKENIZERS)
        self._reducer = build_processor(REDUCER)
        self._filter = build_processor(FILTERS)
        self._extractor = build_processor(EXTRACTORS)
        self._running = False
        self._query_handler = None
        if EXTRACT_TEST_QUERY:
            qlog = "%s_query.log" % threadname
            qlog = os.path.join(DATA_DIR, qlog)
            if os.path.exists(qlog):
                self._query_handler = open(qlog, 'a+')
            else:
                self._query_handler = open(qlog, 'w+')

    def process(self, page, url):
        content = self._extractor.processChain(page)
        if EXTRACT_TEST_QUERY:
            length = len(content)
            start = int(length * 0.25)
            end = int(length * 0.35)
            query = content[start:end]
            query = " ".join(query.split())
            self._query_handler.write(url + "\t")
            self._query_handler.write(query)
            self._query_handler.write("\n")
        words = self._tokenizer.processChain(content)
        reduced = self._reducer.process(words)
        result = self._filter.processChain(reduced)
        return result

    def run(self):
        self.logger.info("Consumer Thread [%s] starting..." % self.name)
        self._running = True
        empty_count = 0
        max_count = MAX_IDLE_TIME//MAX_SLEEP_INTERVAL
        filename = "%s.log" % self.name
        filename = os.path.join(DATA_DIR, filename)
        handler = open(filename, 'a+')
        log_interval = 10
        processed = 0
        total_processed = 0
        log_cost = 0
        while self._running:
            try:
                if self._queue.empty():
                    self.logger.info("Queue is empty!")
                    if processed:
                        handler.flush()
                    if empty_count > max_count:
                        if processed:
                            self.logger.info("[%s] Processed %d items, So far total processed %d items." % (self.name, processed, total_processed))
                        self.logger.info("[%s] Seems all data have been processed, stop processing..." % self.name)
                        break
                    time.sleep(MAX_SLEEP_INTERVAL)
                    empty_count += 1
                    continue
                empty_count = 0
                item = self._queue.get(block=True, timeout=30)
                start = time.time()
                words = self.process(item[0], item[1])
                cost = (time.time() - start) * 1000.0
                log_cost += cost
 #               self.logger.debug("[%s] Pure processing cost: %0.3f" % (self.name, cost))
                content = json.dumps(words)
                handler.write(content)
                handler.write('\n')
                self._queue.task_done()
                processed += 1
                total_processed += 1
                if processed == log_interval:
                    handler.flush()
                    processed = 0
                    self.logger.info("[%s] Processed %d items cost %0.3f ms, So far total processed %d items." % (self.name, log_interval, log_cost, total_processed))
                    log_cost = 0
                    if self._query_handler:
                        self._query_handler.flush()
            except Exception, e:
#                print e
                if not self._running:
                    break

        handler.close()
        if self._query_handler:
            self._query_handler.close()
        self.logger.info("Consumer Thread [%s] running stopped!" % self.name)
#        print("Finished processing %d, datasize: %d, time: %f" % (count, size, cost))
    
    def stop_running(self):
        if self._running:
            self._running = False  


class ProducerTask(Thread):
    def __init__(self, queue, redis, threadname):
 #       Thread.__init__(self)
        super(ProducerTask, self).__init__(name = threadname)
        self.logger = logging.getLogger('ProducerTask')
        self._queue = queue
        self._redis = redis
        self._redis_keys = REDIS_KEYS
        self._running = False
        self._backup_key = BACKUP_KEY
        self._redis_keys.append(self._backup_key)

    def run(self):
        self.logger.info("Producer thread [%s] starting..." % self.name)
        self._running = True
        num = 0
        max_num = MAX_IDLE_TIME//MAX_SLEEP_INTERVAL
        total_processed = 0
        while self._running:
            found = False
            try:
                if self._queue.full():
                    self.logger.info("Queue is full!")
                    time.sleep(1)
                    continue
                found_num = 0
                for key in self._redis_keys:
                    item = self._redis.rpop(key)
                    if item:
                        found = True
                        found_num += 1
                        item = ast.literal_eval(item) # convert back to list
                        self._queue.put(item, block=True)

                total_processed += found_num
                self.logger.info("Found %d items. So far total items: %d, Queue size: %d" % (found_num, 
                    total_processed, self._queue.qsize()))
                if found:
                    num = 0
                else:
                    if num > max_num:
                        self.logger.info("[%s] All items have been processed, redis is empty!" % self.name)
                        break
                    time.sleep(MAX_SLEEP_INTERVAL)
                    num += 1
            except Exception, e:
                self.logger.error(e)
                if not self._running:
                    break
        datadog.gauge('frequencer.page.process.num', total_processed)
        self.logger.info("Producer thread [%s] stopped!" % self.name)

    def stop_running(self):
        if self._running:
            self._running = False
            if not self._queue.empty():
                self.logger.info("Saving not processed pages to backup queue in redis......")
                count = 0
                while not self._queue.empty():
                    try:
                        item = self._queue.get(block=True, timeout=30)
                        self._redis.lpush(self._backup_key, item)
                        count += 1
                    except Exception,e:
                        self.logger.error(e)
                        continue
                self.logger.info("Saving finished! save %d items to backup queue" % count)


class Pipeline(object):
    def __init__(self):        
        self.logger = logging.getLogger('Pipeline')
        self._numthread = THREADS
        self._queue = Queue(QUEUE_SIZE)
        self._redis = redis.Redis()
        self._threads = []
    
    def build_processor(self, types):
        processor = None
        if isinstance(types, list):
            for item in types:
                index = item.rindex(".")
                module = item[:index]
                name = item[index+1:]
                mdu = importlib.import_module(module)
                if hasattr(mdu, name):
                    cls = getattr(mdu, name)
                    processor = cls(processor)
                else:
                    self.logger.error("Can't find %s in module: %s" % (name, module))
        elif isinstance(types, str):
            index = types.rindex(".")
            module = types[:index]
            name = types[index+1:]
            mdu = importlib.import_module(module)
            if hasattr(mdu, name):
                cls = getattr(mdu, name)
                processor = cls()
            else:
                self.logger.error("Can't find %s in module: %s" % (name, module))
        return processor

    def start(self):
        self.start_producer_thread()
        self.start_consumer_threads(self._numthread)

    def stop(self, signum, frame):
        self.logger.info("receive a signal %d" % signum)
        self.logger.info("Stoping processing....")
        for thread in self._threads:
            thread.stop_running()

    def join(self):
        while 1:
            alive = False
            for thread in self._threads:
                alive = alive or thread.isAlive()
                if alive:
                    break
            if not alive:
                self.logger.info("All threads have been successfully stopped!")
                break
            else:
                self.logger.info("Runing......")
                time.sleep(3)

    def start_consumer_threads(self, num_threads=1):
        self.logger.info("Start %d Consumer threads..." % num_threads)
        for i in range(num_threads):
            t = ConsumerTask(self._queue, self.build_processor, "Consumer-" + str(i))
            t.daemon = True
            self._threads.append(t)
            t.start()

    def start_producer_thread(self):
        self.logger.info("Start producer thread...")
        t = ProducerTask(self._queue, self._redis, "Producer-0")
        t.daemon = True
        self._threads.append(t)
        t.start()


if __name__ == "__main__":
    p = Pipeline()
    signal.signal(signal.SIGINT, p.stop)
    signal.signal(signal.SIGTERM, p.stop)
    start = time.time()
    logging.info("Pipeline starting...")
    p.start()
    p.join()
    cost = (time.time() - start) * 1000.0
    cost_in_seconds = cost/1000 - MAX_IDLE_TIME
    datadog.gauge('frequencer.page.process.cost', cost_in_seconds)
    logging.info("All Content processing cost: %0.3f s" %  cost_in_seconds)
    logging.info("Processing all logs......")
    #process the files
    dic = {}
    for i in range(THREADS):
        filelog = "Consumer-" + str(i) + ".log"
        filelog = os.path.join(DATA_DIR, filelog)
        with open(filelog, 'r+') as handler:
            lines = handler.readlines()
            if lines:
                for line in lines:
                    data = json.loads(line)
                    for item in data:
                        if item not in dic:
                            dic[item] = data[item]
                        else:
                            dic[item] = dic[item] + data[item]
    
    bak = os.path.join(DATA_DIR,'Overall.log')
    if os.path.exists(bak):
        logging.info("Loading backup data from log....")
        with open(bak, 'r+') as handler:
            content = handler.readlines()
            if content:
                for line in content:
                    data = json.loads(line)
                    for item in data:
                        if item not in dic:
                            dic[item] = data[item]
                        else:
                            dic[item] = dic[item] + data[item]

    logging.info("logs processing finished, found words: %d" % len(dic))
    logging.info("deleting logs......")
    for i in range(THREADS):
        filelog = "Consumer-" + str(i) + ".log"
        filelog = os.path.join(DATA_DIR, filelog)
        os.remove(filelog)
        logging.info("%s delete succeed!" % filelog)

    logging.info("deleting logs finished!")

    
    if len(dic):
        #back up the data incase processing failed
        with open(bak, 'w+') as handler:
            content = json.dumps(dic)
            handler.write(content)
        logging.info("insert/updating words with frequency to db......")
        #insert or update db
        start = time.time()
        opts = DBAdapter('root', 'hohoyi123')
        opts.create_db_or_table_if_not_exist()
        opts.insert_or_update_values(dic)
        cost = (time.time() - start) * 1000.0
        logging.info("Update DB cost: %0.3f" % cost)
        datadog.gauge('frequencer.db.update.cost', cost/1000)
        #delete backup file
        os.remove(bak)
    else:
        logging.info("Words list is empty, escape db processing")
    

    #merge query file to one if existed:
    if EXTRACT_TEST_QUERY:
        mode = 'w+'
        qlog = QUERY_FILE % curtime.strftime('%Y-%m-%d')
        qlog = os.path.join(DATA_DIR, qlog)
        if os.path.exists(qlog):
            mode = 'a+'
        with open(qlog, mode) as writer:
            for i in range(THREADS):
                filelog = "Consumer-" + str(i) + "_query.log"
                filelog = os.path.join(DATA_DIR, filelog)
                with open(filelog, 'r+') as handler:
                    lines = handler.readlines()
                    if lines:
                        for line in lines:
                            writer.write(line)
                #delete the subfile after merging
                os.remove(filelog)
                logging.info("%s delete succeed!" % filelog)

    logging.info("Pipeline processing finished!")
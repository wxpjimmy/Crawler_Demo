#!/usr/bin/python
#-*-coding:utf-8-*-

import redis
from scrapy.utils.misc import load_object
from .dupefilter import RFPDupeFilter
from scrapy import log
from datetime import datetime, timedelta


# default values
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
SCHEDULER_PERSIST = False
QUEUE_KEY = '%(spider)s:requests'
QUEUE_CLASS = '.queue.SpiderPriorityQueue'
DUPEFILTER_KEY = '%(spider)s:df:%(date)s'
EXTRA_DUPEFILTER_KEYS = {DUPEFILTER_KEY:-1}


class Scheduler(object):
    """Redis-based scheduler"""

    def __init__(self, server, persist, queue_key, queue_cls, dupefilter_key, dupefilter_expire):
        """Initialize scheduler.

        Parameters
        ----------
        server : Redis instance
        persist : bool
        queue_key : str
        queue_cls : queue class
        dupefilter_key : str
        """
        self.server = server
        self.persist = persist
        self.queue_key = queue_key
        self.queue_cls = queue_cls
        self.dupefilter_key = dupefilter_key
        self.dupefilter_expire = dupefilter_expire

    def __len__(self):
        return len(self.queue)

    @classmethod
    def from_settings(cls, settings):
        host = settings.get('REDIS_HOST', REDIS_HOST)
        port = settings.get('REDIS_PORT', REDIS_PORT)
        persist = settings.get('SCHEDULER_PERSIST', SCHEDULER_PERSIST)
        queue_key = settings.get('SCHEDULER_QUEUE_KEY', QUEUE_KEY)
        queue_cls = load_object(settings.get('SCHEDULER_QUEUE_CLASS', QUEUE_CLASS))
        dupefilter_key = settings.get('DUPEFILTER_KEY', DUPEFILTER_KEY)
        dupefilter_expire = settings.get('DUPEFILTER_EXPIRE', 172800)
#        dupefilter_extra_keys = settings.get('EXTRA_DUPEFILTER_KEYS', EXTRA_DUPEFILTER_KEYS)
        server = redis.Redis(host, port)
        return cls(server, persist, queue_key, queue_cls, dupefilter_key, dupefilter_expire)

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        cls.stats = crawler.stats
        return cls.from_settings(settings)

    def open(self, spider):
        """
            execute this function when open one spider
        """
        
        self.spider = spider
        self.queue = self.queue_cls(self.server, spider, self.queue_key)
        time = datetime.utcnow()
        key = self.dupefilter_key % {'spider': spider, 'date': time.strftime('%Y%m%d')}
        extra_keys = []
        num = self.dupefilter_expire/86400
        for index in range(1, num):
            lst_time = time - timedelta(days=index)
            extra_key = self.dupefilter_key % {'spider': spider, 'date': time.strftime('%Y%m%d')}
            extra_keys.append(extra_key)
        exist = self.server.exists(key)
        self.df = RFPDupeFilter(self.server, key, extra_keys, exist, self.dupefilter_expire)
        # notice if there are requests already in the queue to resume the crawl
        if len(self.queue):
            spider.log("Resuming crawl (%d requests scheduled)" % len(self.queue))

    def close(self, reason):
        print reason
        self.df.close(reason)
        if not self.persist:
#            self.df.clear()
            self.queue.clear()

    def enqueue_request(self, request):
        if not request.dont_filter and self.df.request_seen(request):
            log.msg("Found duplicate url: %s" % request.url)
            self.stats.inc_value('scheduler/duplicate/url', spider = self.spider)
            return
        self.stats.inc_value('scheduler/enqueued/redis', spider=self.spider)
        self.queue.push(request)

    def next_request(self):
        request = self.queue.pop()
        if request:
            self.stats.inc_value('scheduler/dequeued/redis', spider=self.spider)
        return request

    def has_pending_requests(self):
        return len(self) > 0

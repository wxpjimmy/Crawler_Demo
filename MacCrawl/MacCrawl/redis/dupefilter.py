#!/usr/bin/python
#-*-coding:utf-8-*-

import redis
import time
#from scrapy import log

from scrapy.dupefilter import BaseDupeFilter
from scrapy.utils.request import request_fingerprint
from scrapy import log


class RFPDupeFilter(BaseDupeFilter):
    """Redis-based request duplication filter"""

    def __init__(self, server, key, extra_filter_keys=None, key_exist = False, key_expire=2):
        """Initialize duplication filter

        Parameters
        ----------
        server : Redis instance
        key : str
            Where to store fingerprints
        """
        self.server = server
        self.key = key
        self.extra_filter_keys = extra_filter_keys
        self.key_exist = key_exist
        self.key_expire = key_expire
        self.fp_persist = set()
        self.fp_to_persist = set()
        start = time.time()
        if self.key_exist:
            persisted = server.smembers(self.key)
            if persisted:
                self.fp_persist.update(persisted)
            if self.extra_filter_keys:
                for extra_key in self.extra_filter_keys:
                    rs = server.smembers(extra_key)
                    if rs:
                        self.fp_persist.update(persisted)
        cost = (time.time() - start)*1000.0
        log.msg('load persisted fingerprints from redis:(cost: %0.3f) (num: %d)' % (cost, len(self.fp_persist)), log.WARNING)

    @classmethod
    def from_settings(cls, settings):
        host = settings.get('REDIS_HOST', 'localhost')
        port = settings.get('REDIS_PORT', 6379)
        server = redis.Redis(host, port)
        # create one-time key. needed to support to use this
        # class as standalone dupefilter with scrapy's default scheduler
        # if scrapy passes spider on open() method this wouldn't be needed
        key = "dupefilter:%s" % int(time.time())
        return cls(server, key)

    @classmethod
    def from_crawler(cls, crawler):
        return cls.from_settings(crawler.settings)

    def request_seen(self, request):
        """
            use sismember judge whether fp is duplicate.
        """
 #       log.msg("Duplicate key: %s" % self.key)
        fp = request_fingerprint(request)
 #       log.msg("Url: %s  Fingerprint: %s type: %s" % (request.url, fp, str(type(fp))), log.WARNING)
        if self.key_exist:
            if fp in self.fp_persist or fp in self.fp_to_persist:
                return True
            self.fp_to_persist.add(fp)
        else:
            self.server.sadd(self.key, fp)
            self.fp_persist.add(fp)
            self.server.expire(self.key, self.key_expire)
            self.key_exist = True
            
        return False

    def close(self, reason):
        """Delete data on close. Called by scrapy's scheduler"""
#        self.clear()
        log.msg('DupeFilter closing...')
        if self.fp_to_persist:
            count = len(self.fp_to_persist)
            log.msg('fingerprints to persist num: %d' % count)
            start = time.time()
            self.server.sadd(self.key, *self.fp_to_persist)
            cost = (time.time() - start)*1000.0
            log.msg('Persist %d fingerprints to redis on closing, cost: %0.3f' % (len(self.fp_to_persist), cost))
            self.fp_to_persist.clear()
            self.fp_persist.clear()

    def clear(self):
        """Clears fingerprints data"""
        self.server.delete(self.key)
        if self.extra_filter_keys is not None:
            for extra_key in self.extra_filter_keys:
                self.server.delete(self.extra_key)

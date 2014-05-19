from scrapy.statscol import StatsCollector
from datetime import datetime
import redis
from .monitors import datadog
import os
import pprint

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
STATS_KEEP = 50

class MacStatsCollector(StatsCollector):
    def __init__(self, crawler):
        super(MacStatsCollector, self).__init__(crawler)
        self.spider_stats = {}

    def _persist_stats(self, stats, spider):
        self.spider_stats[spider.name] = stats
        #statsd metric
        cost = (stats['finish_time'] - stats['start_time']).total_seconds()
        norm_cost = cost//60
        tag = str(spider)
        tag = tag.replace(":", "_")
        tag = "crawler:%s" % tag
        datadog.gauge('crawler.crawl.cost', cost, tags=[tag])
        datadog.gauge('crawler.crawl.cost.norm_in_minute', norm_cost, tags=[tag])
        datadog.gauge('crawler.es.index.success', stats['es/index/success'], tags=[tag])
        datadog.gauge('crawler.es.index.failed', stats['es/index/failed'], tags=[tag])
        datadog.gauge('crawler.scraped.count', stats.get('item_scraped_count', 0), tags=[tag])
        excep_count = 0
        for k in stats:
            if k.startswith('spider_exceptions'):
                excep_count += stats[k]
        datadog.gauge('crawler.spider.exceptions', excep_count, tags=[tag])

        #save running stats to local file
        date = datetime.utcnow().date()
        host = spider.settings.get('REDIS_HOST', REDIS_HOST)
        port = spider.settings.get('REDIS_PORT', REDIS_PORT)
        num = spider.settings.get('STATS_KEEP', STATS_KEEP)

        server = redis.Redis(host, port)
        key = "%s:%s" % (spider, "stats")
        server.lpush(key, stats)
        #keep the latest num stats in redis for each crawler
        server.ltrim(key, 0, num-1)

        rootdir = spider.settings.get('STATS_LOG_PATH', '/var/log/scrapyd/stats/')
        filename = "Stats_%s_%s.log" % (spider._type, date)
        filename = os.path.join(rootdir, filename)
        
        with open(filename, 'a+') as fs:
            stats = pprint.pformat(stats)
            fs.write(stats + '\n\n')

    def close_spider(self, spider, reason):
        super(MacStatsCollector, self).close_spider(spider, reason)
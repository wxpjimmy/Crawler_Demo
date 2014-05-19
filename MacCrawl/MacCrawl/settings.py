# Scrapy settings for hn project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'MacCrawl'

SPIDER_MODULES = ['MacCrawl.spiders']
NEWSPIDER_MODULE = 'MacCrawl.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'hn (+http://www.yourdomain.com)'
ITEM_PIPELINES = {
#        'hn.pipelines.MSNPipeline':400,
#        'hn.pipelines.TcNewPipeline': 400,
         'MacCrawl.pipelines.generalsitemap.GeneralSitemapPipeline' : 400
        }

PIPELINE_SPIDERS = {
        'TcNewPipeline':['tcnew'],
        'MSNPipeline': ['msn'],
        'GeneralSitemapPipeline': ['sitemap', 'general']
        }

DEPTH_LIMIT = 3
DOWNLOADER_MIDDLEWARES = {
    'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None,
    'MacCrawl.contrib.downloadmiddleware.rotate_useragent.RotateUserAgentMiddleware':400,
}

STATS_CLASS = 'MacCrawl.utils.macstats.MacStatsCollector'

LOG_FORMATTER = 'MacCrawl.contrib.logformatter.PoliteLogFormatter'

LOG_LEVEL = 'INFO'

USER_AGENT = ''

COOKIES_ENABLED = False

#LOG_STDOUT = True
DOWNLOAD_DELAY = 0.25

SCHEDULER = "MacCrawl.redis.scheduler.Scheduler"
SCHEDULER_PERSIST = False
SCHEDULER_QUEUE_CLASS = 'MacCrawl.redis.queue.SpiderPriorityQueue'


REDIS_HOST = 'localhost'
REDIS_PORT = 6379
QUEUE_KEY = '%(spider)s:requests'
QUEUE_CLASS = '.queue.SpiderPriorityQueue'
DUPEFILTER_KEY = '%(spider)s:df:%(date)s'
# in seconds
DUPEFILTER_EXPIRE = 172800

ES_SERVER = 'localhost'
ES_PORT = '9200'
ES_INDEX = 'news'
ES_DOC_TYPE = 'perf'

STATS_LOG_PATH = '/var/log/scrapyd/stats/'

from datetime import datetime, timedelta
from bs4 import BeautifulSoup as bs
from scrapy.spider import Spider
from scrapy.http import Request, XmlResponse
from MacCrawl.items import TcNewItem
from ElasticsearchClient import ES
import re
import os
from scrapy import log
from MacCrawl.utils.sitemap_util import SitemapUtil, sitemap_urls_from_robots
from scrapy.utils.gz import gunzip, is_gzipped
from sitemap_util import *
import logging
from scrapy.log import ScrapyFileLogObserver
import dateutil
from dateutil.parser import parse
import redis


class GeneralSitemapSpider(Spider):
    name = 'sitemap'

    start_urls = []

    def __init__(self, key=None, **kwargs):
        if key is None:
            raise Exception("Must specify a spider type!")
        else:
            self._type = key
            print key
            time =  datetime.utcnow()
            log_path = '/var/log/scrapyd/logs/'
#            exist = os.path.exists(log_path)
#            if not exist:
#                os.makedirs(log_path)
            logfile = "scrapy_%s_%s_%s.log" % (self.name, self._type,time)
            logfile = os.path.join(log_path, logfile)
            print logfile
            handle = open(logfile, 'w')
            log_observer = ScrapyFileLogObserver(handle, level=logging.INFO)
            log_observer.start()
            
            error_file = "scrapy_%s_%s_%s_Error.log" % (self.name, self._type, time)
            error_file = os.path.join(log_path, error_file)
            error_handle = open(error_file, 'w')
            error_observer = ScrapyFileLogObserver(error_handle, level=logging.WARNING)
            error_observer.start()

            self.key = "%s:%s" % (self.name, self._type)
            self.lastmodified = datetime.utcnow()

            # load urls, load last crawled time
        super(GeneralSitemapSpider, self).__init__(self.name, **kwargs)

    def start_requests(self):
        #some initialize, have to put here for we need settings in crawler, but in __init__the
        #crawler haven't been set
        host = self.settings.get('REDIS_HOST', 'localhost')
        port = self.settings.get('REDIS_PORT', 6379)
        self.server = redis.Redis(host, port)

        cached = self.server.get(self.key)
        if cached is None:
            now = datetime.utcnow()
            start = now - timedelta(days=7)
            self.lastmodified = datetime(start.year, start.month, start.day)
        else:
            self.lastmodified = datetime.strptime(cached, '%Y-%m-%d %H:%M:%S')

        print self.lastmodified
        urls = SM_URL.get(self._type)
        print urls
        #log.msg("Test warning/error log", logging.WARNING)
        for url in urls:
            yield Request(url, callback=self._parse_sitemap, dont_filter=True)

#                func = SM_FUNC.get(self._type)
#                print func.__name__
#                for req in func(self, s):
    def _parse_sitemap(self, response):
        print response.url
        if response.url.endswith('/robots.txt'):
            for url in sitemap_urls_from_robots(response.body):
                yield Request(url, callback=self._parse_sitemap, dont_filter=True)
        else:
            body = self._get_sitemap_body(response)
            if body is None:
                log.msg(format="Ignoring invalid sitemap: %(response)s",
                        level=log.WARNING, spider=self, response=response)
                return
            try:
                s = SitemapUtil(body)
                print s.type
                if s.type == 'sitemapindex':
                    for link in self._filter_loc(s):
                        print link
                        yield Request(link, callback=self._parse_sitemap, dont_filter=True)
                elif s.type == 'urlset':
                    for req in self.process_urlset(s):
                        yield req

            except Exception,e:
                log.msg("Exception occurred: %s" % e, log.ERROR)
                log.msg("Content: %s" % response.body, log.ERROR)

    def process_urlset(self, s):
        for values in s:
            link = values['loc']
            format = SM_DATE.get(self._type)
            title = values.get('title')
            item = None
            if title:
                date = values.get('publication_date')
                item = SitemapItem()
                item['title'] = title
                if format:
                    item['update'] = datetime.strptime(date, format)
                else:
                    dt = parse(date)
                    dt_utc = dt.astimezone(dateutil.tz.tzutc()).replace(tzinfo=None)
                    item['update'] = dt_utc
            else:
                #format 2014-04-27
                date = values.get('lastmod')
                if date:
                    item = SitemapItem()
                    if format:
                        item['update'] = datetime.strptime(date, format)
                    else:
                        dt = parse(date)
                        dt_utc = dt.astimezone(dateutil.tz.tzutc()).replace(tzinfo=None)
                        item['update'] = dt_utc

            req = Request(link, callback = self.process_page)
            if item:
                date = item.get('update')
                if date and self.lastmodified > date:
                    print "Filtered: " , date
                    self.crawler.stats.inc_value('spider/date/filter', spider=self)
                    continue
                else:
                    req.meta['item'] = item
                    yield req
            else:
                yield req        
    
    def process_page(self, response):
        item = response.meta.get('item')
        if item is None:
            item = SitemapItem()
            title = self._extract_title(response.body)
            if title:
                item['title'] = title.string

        item['link'] = response.url
        item['content'] = response.body_as_unicode()
        yield item
#        func = PAGE_FUNC.get(self._type)
#        print func.__name__
#        for item in func(response):
#            yield item

    def _extract_title(self, data):
        func = TITLE_FUNC.get(self._type)
        if func:
            return func(data)
        return

    def _filter_loc(self, locs):
        log.msg("filter starts")
        rules = SM_FILTER.get(self._type)
        if rules is None:
            log.msg("no rule found")
            for item in locs:
                yield item['loc']
        else:
            print rules
            for item in locs:
                should_filter = False
                for rule in rules:
                    ptn = re.compile(rule, re.IGNORECASE)
                    match = ptn.match(item['loc'])
                    if match is not None:
                        should_filter = True
                        break
                if should_filter:
                    continue
                else:
                    yield item['loc']


    def _get_sitemap_body(self, response):
        """Return the sitemap body contained in the given response, or None if the
        response is not a sitemap.
        """
        if isinstance(response, XmlResponse):
            return response.body
        elif is_gzipped(response):
            return gunzip(response.body)
        elif response.url.endswith('.xml'):
            return response.body
        elif response.url.endswith('.xml.gz'):
            return gunzip(response.body)
        elif response.url.endswith('.xmlo'):
            return response.body

    def __str__(self):
        return self.key

    __repr__ = __str__

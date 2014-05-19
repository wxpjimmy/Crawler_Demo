from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from MacCrawl.items import SitemapItem
from scrapy.http import Request, HtmlResponse
import logging
from scrapy import log
from scrapy.log import ScrapyFileLogObserver
from general_util import *
import datetime
import re
import os

class GeneralSpider(CrawlSpider):
    name = 'general'
    start_urls = []
    rules = ()
#    rules = (
#            Rule(SgmlLinkExtractor(deny=('\.js', '\.php', 'search.yahoo.com','yahoo.uservoice.com', '\?q=')), callback='parse_content', follow=True),
#            )

    def __init__(self, key=None, **kwargs):
        #fetch general to crawl list here from file or DB
        if key is None:
            raise Exception("No start urls selected!")
        else:
            print key
            self._type = key
            self.start_urls = URL_MAP.get(key)
            print(self.start_urls)
            self.rules = RULE_MAP.get(key)
            print(self.rules)

            time =  datetime.datetime.utcnow()
            log_path = '/var/log/scrapyd/logs/'
            logfile = "scrapy_%s_%s_%s.log" % (self.name, self._type, time)
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

            self.first_not_filter = []
            #select self_start_urls and self_rules based on the parameter
#        self.start_urls = ['http://www.yahoo.com']
        super(GeneralSpider, self).__init__(self.name, **kwargs)

#    def start_requests(self):
#        yield Request('http://www.yahoo.com', self.parse)

    def _requests_to_follow(self, response):
        if not isinstance(response, HtmlResponse):
            return
        seen = set()
        for n, rule in enumerate(self._rules):
            ls = rule.link_extractor.extract_links(response)
            links = [l for l in ls if l not in seen]
            if links and rule.process_links:
                links = rule.process_links(links)
            for link in links:
                seen.add(link)
                not_filter_rules = DONT_FILTER.get(self._type)
                dont_filter = False
                if link.url not in self.first_not_filter: ## or consider using depth to control this???
                    if not_filter_rules:
                        for r in not_filter_rules:
                            ptn = re.compile(r)
                            match = ptn.match(link.url)
                            if match:
                                dont_filter = True
                                self.first_not_filter.append(link.url)
                                break
                r = Request(url=link.url, callback=self._response_downloaded, dont_filter=dont_filter)
                r.meta.update(rule=n, link_text=link.text)
                yield rule.process_request(r)


    def process_content(self, response):
 #       depth = response.meta['depth']
 #       print depth
        print response.url

        item = SitemapItem()
        item['link'] = response.url
        try:
            item['content'] = response.body_as_unicode()
        except Exception, e:
            log.msg('Error: %s' % e, log.ERROR)
            item['content'] = response.body
        return item

    def __str__(self):
        return "%s:%s" % (self.name, self._type)

    __repr__ = __str__

from scrapy.command import ScrapyCommand
import urllib
import urllib2
from scrapy import log

class AllCrawlCommand(ScrapyCommand):

requires_project = True
default_settings = {'LOG_ENABLED': False}

def short_desc(self):
    return "Schedule a run for all available spiders"

def run(self, args, opts):
    url = 'http://localhost:6800/schedule.json'
    for s in self.crawler.spiders.list():
        values = {'project' : 'YOUR_PROJECT_NAME', 'spider' : s}
        data = urllib.urlencode(values)
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        log.msg(response)

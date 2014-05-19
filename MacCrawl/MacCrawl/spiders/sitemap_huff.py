from bs4 import BeautifulSoup as bs
from scrapy.http import Request
from MacCrawl.items import SitemapItem
import dateutil
from dateutil.parser import parse


## processing huffingtonpost

def process_huffingtonpost_sitemap(spider, body):
    print "Enter processing sitemap for huff"
    data = bs(body)
    urls = data.find_all('url')
    for url in urls:
        link = url.loc.text
        news = url.find('n:news')
        item = None
        if news is not None:
            item = SitemapItem()
            title = news.find('n:title')
            item['title'] = title.text
            #format: 2014-04-26T23:59:01-04:00
            date = news.find('n:publication_date')
            dt = parse(date.text)
            dt_utc = dt.astimezone(dateutil.tz.tzutc()).replace(tzinfo=None)
            item['update'] = dt_utc
        
        req = Request(link, callback = spider.process_page)
        if item is not None:
            req.meta['item'] = item
        else:
            pass
        yield req

def extract_title(page):
    data = bs(page)
    title = data.find('h1', {"class": "title"})
    return title


def process_huffingtonpost_page(response):
    item = response.meta.get('item')
    if item is None:
        item = SitemapItem()
        data = bs(response.body)
        title = data.find('h1', {"class": "title"})
        if title is not None:
            item['title'] = title.string
        else:
            pass
    else:
        pass
    item['link'] = response.url
    item['content'] = response.body
    yield item

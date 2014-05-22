from scrapy.contrib.spiders import Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from MacCrawl.contrib.linkextractors.lxmllinkextract import CustomLinkExtractor


URL_MAP = {
        "gnews": ["https://news.google.com"],
        "theverge": ["http://www.theverge.com"]}


RULE_MAP = { 
            "gnews":  (
            Rule(SgmlLinkExtractor(allow=(r'https?://news.google.com/news/section.*'), deny=(r'.*ict=clu_top'), restrict_xpaths=(r'//*[@id="nav-menu-wrapper"]', r'//*[@id="main-pane"]/div/div/div[3]'))),
            # for those website in the deny_domains are already crawled by sitemap crawler, here we don't need to re-crawl them, just ignore them
            Rule(SgmlLinkExtractor(allow=(r'.*'), deny=(r'.*.google.*/.*', r'.js', r'.php', r'.*/videos?/.*', r'.*/photos?/.*'), 
                deny_domains=('huffingtonpost.com', 'wsj.com','cnn.com','reuters.com','bbc.co.uk','bbc.com','forbes.com','usatoday.com','lifehacker.com','mashable.com',
                'washingtonpost.com','news.yahoo.com','news.msn.com', 'nytimes.com')), callback='process_content'),
            ),
            "theverge": (
            Rule(CustomLinkExtractor(allow=(r'http://www.theverge.com/\d{4}/\d{1,2}/\d{1,2}/.*')), callback='process_content'),
            Rule(CustomLinkExtractor(allow=(r'http://www.theverge.com/\w+$', r'http://www.theverge.com/us-world$'), 
                deny=(r'http://www.theverge.com/.*/.*', r'/search', r'/forums', r'/longform', r'video', r'/jobs', r'/archives'))),
#            Rule(SgmlLinkExtractor(allow=(r'/.*/archives$', r'/.*/archives/\d+$'))),
            )
            }

DONT_FILTER = {
                "gnews": [r'https?://news.google.com/news/section.*'],
                "theverge": [r'http://www.theverge.com/\w+$', r'http://www.theverge.com/us-world$']
                }

from sitemap_huff import *
"""
from sitemap_wsj import *
from sitemap_cnn import *
from sitemap_reuter import *
from sitemap_bbc import *
from sitemap_forbes import *
from sitemap_usatoday import *
from sitemap_lifehacker import *
from sitemap_mashable import *
from sitemap_washingtonpost import *

from sitemap_yahoo import *
from sitemap_msn import *
from sitemap_nytimes import *



SM_FUNC = { "huff": process_huffingtonpost_sitemap,
            "wsj": process_wsj_sitemap,
            "cnn": process_cnn_sitemap,
            "reuter": process_reuter_sitemap,
            "bbc": process_bbc_sitemap,
            "forbes": process_forbes_sitemap,
            "usatoday": process_usatoday_sitemap,
            "lifehacker": process_lifehacker_sitemap,
            "mashable": process_mashable_sitemap,
            "washingtonpost": process_washingtonpost_sitemap,
            "yahoo": process_yahoo_sitemap,
            "msn": process_msn_sitemap,
            "nytimes": process_nytimes_sitemap}

PAGE_FUNC = { "huff": process_huffingtonpost_page,
              "wsj": process_wsj_page,
              "cnn": process_cnn_page,
              "reuter": process_reuter_page,
              "bbc": process_bbc_page,
              "forbes": process_forbes_page,
              "usatoday": process_usatoday_page,
              "lifehacker": process_lifehacker_page,
              "mashable": process_mashable_page,
              "washingtonpost": process_washingtonpost_page,
              "yahoo": process_yahoo_page,
              "msn": process_msn_page,
              "nytimes": process_nytimes_page}
"""

TITLE_FUNC = {
                "huff": extract_title
              }

##here None means the date format is with timezone info, need to use dateutil to help parse
SM_DATE = {
            "huff": None, 
            "wsj": None,
            "cnn": '%Y-%m-%dT%H:%M:%SZ',
            "reuter": None,
            "bbc": '%Y-%m-%dT%H:%M:%SZ',
            "forbes": '%Y-%m-%d',
            "usatoday": None,
            "lifehacker": None,
            "mashable": '%Y-%m-%dT%H:%M:%SZ',
            "washingtonpost": '%Y-%m-%dT%H:%M:%SZ',
            "yahoo": None,
            "msn": '%Y-%m-%dT%H:%M:%SZ',
            "nytimes": None,
            "gulfnews": '%Y-%m-%d',
            "techcrunch": None
          }

SM_URL = { 
        "huff": [ 'http://www.huffingtonpost.com//sitemap.xml'],
        "wsj": ['http://online.wsj.com/x_google_news.html', 
                'http://online.wsj.com/x_google_news_ap.html',
                'http://online.wsj.com/x_google_news_wire.html'
#                'http://online.wsj.com/sitemap.xml'
#                'http://online.wsj.com/public/resources/documents/google/wsj/google_sitemap_index.xml'
                ],
        "cnn": ['http://edition.cnn.com/sitemaps/sitemap-news.xml'],
#                'http://edition.cnn.com/sitemaps/sitemap-index.xml'],
        "reuter": ['http://www.reuters.com/sitemap_news_index.xml'],
        "bbc": ['http://www.bbc.co.uk/news/news_sitemap.xml',
                'http://www.bbc.co.uk/news/sitemap.xml'],
        "forbes": ['http://www.forbes.com/news_sitemap.xml'],
        "usatoday": ['http://www.usatoday.com/news_sitemap_index.xml'],
        "lifehacker": ['http://lifehacker.com/robots.txt'],
        "mashable": ['http://mashable.com/sitemap-news.xmlo',
                     'http://mashable.com/sitemap-posts-2.xml',
                     'http://mashable.com/sitemap-posts-1.xml'],
        "ask": ['http://www.ask.com/robots.txt'],
        "washingtonpost": ['http://www.washingtonpost.com/news-sitemap-index.xml',
                           'http://www.washingtonpost.com/web-sitemap-index.xml'],
        "abcnews": ['http://abcnews.go.com/xmlLatestStories'],
        "yahoo": ['http://news.yahoo.com/sitemap/stories/index.xml',
                  'http://news.yahoo.com/sitemap/original/index.xml',
                  'http://news.yahoo.com/_s/sitemap-story.xml'],
        "msn": ['http://news.msn.com/robots.txt'],
        "nytimes": ['http://www.nytimes.com/sitemaps/sitemap_news/sitemap.xml.gz'],
        "gulfnews": ['http://gulfnews.com/robots.txt'],
        "techcrunch": ['http://techcrunch.com/news-sitemap.xml']
        }

SM_FILTER = {"cnn": ['.*/sitemap-specials-.*', '.*/sitemap-gallery-.*'],
            "msn": ['.*/photos/.*', '.*/videos/.*']}

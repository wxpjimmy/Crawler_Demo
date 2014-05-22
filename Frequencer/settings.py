TOKENIZERS = ['frequencer.tokenizer.nltktokenizer.NLTKTokenizer']

REDUCER = 'frequencer.interface.BaseReducer'

FILTERS = ['frequencer.filter.stopwordsfilter.StopwordsFilter',
           'frequencer.filter.allowedcharactersfilter.AllowedCharactersRegexFilter',
           'frequencer.filter.regexfilter.DotRemoveRegexFilter',
           'frequencer.filter.regexfilter.TotalRegexFilter']

#EXTRACTORS = ['frequencer.extractor.regexextractor.RegexExtractor']
#EXTRACTORS = ['frequencer.extractor.bsextractor.BSExtractor']
EXTRACTORS = ['frequencer.extractor.lxmlextractor.LXMLExtractor']

THREADS = 20
QUEUE_SIZE = 500

REDIS_SERVER = "localhost"

REDIS_PORT = "6379"

REDIS_KEYS = [ "sitemap:msn:items", "sitemap:yahoo:items", "sitemap:huff:items", "sitemap:wsj:items", "sitemap:cnn:items", 
               "sitemap:reuter:items", "sitemap:bbc:items", "sitemap:forbes:items", "sitemap:usatoday:items", "sitemap:lifehacker:items",
               "sitemap:mashable:items", "sitemap:washingtonpost:items", "sitemap:nytimes:items", "sitemap:gulfnews:items",
               "sitemap:techcrunch:items", "general:gnews:items", "general:theverge:items"]

BACKUP_KEY = "frequencer:bak:items"

MAX_IDLE_TIME = 30
MAX_SLEEP_INTERVAL = 10

DBHOST = "localhost"
DBNAME = 'Sight'
TABLENAME = 'Dictionary'
DUMP_DICFILE = 'mac_dictonary.txt'

EXTRACT_TEST_QUERY = True
QUERY_FILE = "SampleQuery_%s.txt"

LOG_DIR = "/var/log/frequencer/logs/"
DATA_DIR = "/var/log/frequencer/data/"

import sys
import redis

cmd = None

if len(sys.argv) > 1:
    cmd = sys.argv[1]

redis_server = 'localhost'
redis_port = 6379

checklist = [ "sitemap:msn", "sitemap:yahoo", "sitemap:huff", "sitemap:wsj", "sitemap:cnn", 
               "sitemap:reuter", "sitemap:bbc", "sitemap:forbes", "sitemap:usatoday", "sitemap:lifehacker",
               "sitemap:mashable", "sitemap:washingtonpost", "sitemap:nytimes", "sitemap:gulfnews",
               "sitemap:techcrunch", "general:gnews", "general:theverge"]

if len(sys.argv) > 2:
    redis_server = argv[2]

if len(sys.argv) > 3:
    redis_port = int(argv[3])

redis = redis.Redis(redis_server, redis_port)

def checkstatus():
    print("Crawler\t\t\t\tQueued Items\t\t\tDic Items")
    for item in checklist:
        queued = item + ":requests"
        queued_num = redis.zcard(queued)
        cached = item + ":items"
        cached_num = redis.llen(cached)
        print("%s\t\t\t%d\t\t\t\t%d" % (item, queued_num, cached_num))


def clean():
    for item in checklist:
        queued = item + ":requests"
        queued_num = redis.zcard(queued)
        if queued_num > 0:
            redis.delete(queued)
        cached = item + ":items"
        cached_num = redis.llen(cached)
        if cached_num > 0:
            redis.delete(cached)
    print("Clean all queued requests successfully!")

def usage():
    print "Check crawler running status. "
    print "Usage: "
    print "    -c|-clean: remove all queued pages"
    print "    -l|-list:  list current processing status"

if cmd == '-clean' or cmd == '-c':
    clean()
elif cmd == "-l" or cmd == '-list':
    checkstatus()
else:
    usage()

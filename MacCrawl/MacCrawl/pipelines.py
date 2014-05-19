# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from ElasticsearchClient import ES
import os
import datetime


class HnPipeline(object):
    def process_item(self, item, spider):
        return item


class MSNPipeline(object):

    def __init__(self):
        self._es = ES({"localhost":9200}, 'msn', 'perf')
        self._name = 'MSNPipeline'


    def process_item(self, item, spider):
        settings = spider.settings.get('PIPELINE_SPIDERS')
#        print(settings)
        if spider.name not in settings[self._name]:
            return item
        print "Process in Pipeline!"
        self._es.index(item['link'], item['content'])
        return item


class TechCrunchPipeline(object):

    def __init__(self):
        self._es = ES({"localhost":9200}, 'techcrunch', 'perf')
        exist = os.path.isfile('lastupdate.txt')
        self._handle = open('lastupdatetime.txt', 'r+')
        if exist:
            last = self._handle.readline()
            self._last = datetime.datetime.strptime(last, '%Y-%m-%d %H:%M:%S')
        else:
            self._last = datetime.datetime(1970, 1, 1)

    def process_item(self, item, spider):
        pass

class TcNewPipeline(object):

    def __init__(self):
        print "initialing TcNewPipeline"
        self._es = ES({"localhost":9200}, 'techcrunch', 'perf')
        exist = os.path.isfile('/Users/jimmy/lastcrawled.txt')
        print exist
        if exist:
            handle = open('/Users/jimmy/lastcrawled.txt', 'r+')
            last = handle.readline()
            self._last = datetime.datetime.strptime(last.strip(), '%Y-%m-%d %H:%M:%S')
            handle.close()
        else:
            self._last = datetime.datetime(1970, 1, 1)
        self._max = self._last
        self._name = 'TcNewPipeline'

#    def open_spider(self, spider):
#        if spider.name == 'tcnew':


    def process_item(self, item, spider):
        settings = spider.settings.get('PIPELINE_SPIDERS')
        test = spider.name in settings[self._name]
        print test
        if not test:
            return item
        date = datetime.datetime.strptime(item['update'], '%Y-%m-%dT%H:%M:%SZ')
        if self._last > date:
            print "ignore"
            pass
        else:
            self._es.index(item['link'], item['content'])
            print "insert one"
            if self._max < date:
                self._max = date
            else:
                pass

        return item

    def close_spider(self, spider):
        print "Closing spider called!"
        settings = spider.settings.get('PIPELINE_SPIDERS')
        test = spider.name in settings[self._name]
        print test
        if test:
            print self._max
            handle = open('/Users/jimmy/lastcrawled.txt', 'w+')
            handle.write(self._max.strftime('%Y-%m-%d %H:%M:%S'))
            handle.close()
        else:
            print spider.name
            print "not run this spider"

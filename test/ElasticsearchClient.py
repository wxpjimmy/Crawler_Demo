from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient
import urllib2
import json
from datetime import datetime
from utils import timeit

class ES(object):
	"""
	Elasticsearch API wrapper
	"""

	def __init__(self, nodes, index=None, doc_type=None):
		self.nodes = nodes
		self.instance = Elasticsearch(hosts=nodes)
		if index is None:
			self._index = 'test4'
		else:
			self._index = index
		if doc_type is None:
			self._doc_type = 'en'
		else:
			self._doc_type=doc_type

	def __build_index_content(self, url, content):
		return {"url":url, "data":content, "lastupdate": datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

	def __build_search_content(self, text):
		return {"query": 
        	           {"match": {"data": {"query": text, "minimum_should_match": "80%"}}
        			        }
                }

	def __parse_index_response(self, data):
		created = data["created"]
		version = data["_version"]
		if version>1:
			return True
		return created & (version==1)

	def __parse_search_response(self, data):
		result = []
		hits = data["hits"]["hits"]
		cost = data["took"]
		for record in hits:
			res = {}
			score = record["_score"]
			url=record["_source"]["url"]
			res["url"]= url
			res["score"] = score
			result.append(res)
		return {"cost": cost, "result":result}

	def bulk_index(self, **url_data_pairs):
		raise NotImplementedError();

	def index_url(self, url):
                print url
                try:
		    response = urllib2.urlopen(url)
                except urllib2.URLError, e:
                    print e
                    if e.code == '403':
                        print 'retrying'
                        headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
                        req = urllib2.Request(url=url, headers=headers)
                        response = urllib2.urlopen(req)
		data = response.read()
		return self.index(url, data)
        
        @timeit
	def index(self, url, content):
		return self.index_customize(self._index, self._doc_type, url, content)

	def index_customize(self, index, doc_type, url, content):
		data = self.__build_index_content(url, content)
		h_id = hex(hash(url))
		#exist = self.instance.exists(index = self._index, doc_type = self._doc_type, id = h_id)
		p = self.instance.index(index=index, doc_type=doc_type, id= h_id, body=data)
		if not self.__parse_index_response(p):
			print("Error occurred when indexing: %s; Results: %s" % (url, p))
		return p
        
        @timeit
	def search(self, text, needwrap):
                return self.search_index_type(self._index, self._doc_type, text, needwrap)

	def search_customize(self, index, doc_type, data, analyzer, _source_include, _source_exclude, size):
		raw = self.instance.search(index = index, doc_type=doc_type, body=data, analyzer = analyzer, _source_include = _source_include
			, _source_exclude = _source_exclude, size=size)
		return self.__parse_search_response(raw)

	def search_index_type(self, index, doc_type, text, needwrap):
		data = text
		if needwrap:
			data = self.__build_search_content(text)
		raw = self.instance.search(index=index, doc_type=doc_type, body=data, _source_include=['url'], size=5)
		return self.__parse_search_response(raw)

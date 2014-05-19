#!/usr/bin/env python2
# encoding: utf8
import redis
import os

class CrawlerMonitor(object):

    crawlers = {
        "sitemap": [],
        "general": []
    }

    def __init__(self, ip='localhost', port=6379, root='/var/log/scrapy/'):
        self.server = redis.Redis(ip. port)
        self.root = root
        pass

    def status(self):
        pass
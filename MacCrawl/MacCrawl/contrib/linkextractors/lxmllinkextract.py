import re
from urlparse import urlparse
from w3lib.url import safe_url_string
from scrapy.selector import Selector
from lxml import etree
#from lxml.cssselect import CSSSelector
import lxml.html
from scrapy.link import Link
from scrapy.utils.misc import arg_to_iter
from scrapy.linkextractor import IGNORED_EXTENSIONS
from scrapy.utils.python import unique as unique_list, str_to_unicode
from scrapy.contrib.linkextractors.lxmlhtml import LxmlParserLinkExtractor
from scrapy.utils.url import canonicalize_url, url_is_from_any_domain, url_has_any_extension

_re_type = type(re.compile("", 0))

_matches = lambda url, regexs: any((r.search(url) for r in regexs))
_is_valid_url = lambda url: url.split('://', 1)[0] in set(['http', 'https', 'file'])

class CustomLinkExtractor(object):
    def __init__(self, allow=(), deny=(), allow_domains=(), deny_domains=(), restrict_xpaths=(), 
                tags=('a',), attrs=('href',), canonicalize=True, unique=True, process_value=None,
                deny_extensions=None):
        self.allow_res = [x if isinstance(x, _re_type) else re.compile(x) for x in arg_to_iter(allow)]
        self.deny_res = [x if isinstance(x, _re_type) else re.compile(x) for x in arg_to_iter(deny)]
        self.allow_domains = set(arg_to_iter(allow_domains))
        self.deny_domains = set(arg_to_iter(deny_domains))
        self.restrict_xpaths = tuple(arg_to_iter(restrict_xpaths))
        self.canonicalize = canonicalize
        if deny_extensions is None:
            deny_extensions = IGNORED_EXTENSIONS
        self.deny_extensions = {'.' + e for e in arg_to_iter(deny_extensions)}
        self.tag_func = lambda x: x in arg_to_iter(tags)
        self.attr_func = lambda x: x in arg_to_iter(attrs)
        self.process_func = process_value if callable(process_value) else lambda v: v
        self.unique = unique

    def extract_links(self, response):
        if self.restrict_xpaths:
            sel = Selector(response)
            body = u''.join(f
                            for x in self.restrict_xpaths
                            for f in sel.xpath(x).extract()
                            ).encode(response.encoding, errors='xmlcharrefreplace')
        else:
            body = response.body

        links = self._extract_links(body, response.url, response.encoding)
        links = self._process_links(links)
        return links

    def _extract_links(self, response_text, response_url, response_encoding):
        links = []
        html = lxml.html.fromstring(response_text)
        html.make_links_absolute(response_url)
        for e, a, l, p in html.iterlinks():
            if self.tag_func(e.tag):
                if self.attr_func(a):
                    l = safe_url_string(l, response_encoding)
                    text = u''
                    if e.text:
                        text = str_to_unicode(e.text, response_encoding, errors='replace').strip()
                    link = Link(self.process_func(l), text=text)
                    links.append(link)

        links = unique_list(links, key=lambda link: link.url) \
                if self.unique else links

        return links

    def _process_links(self, links):
        links = [x for x in links if self._link_allowed(x)]
        return links

    def _link_allowed(self, link):
        parsed_url = urlparse(link.url)
        allowed = _is_valid_url(link.url)
        if self.allow_res:
            allowed &= _matches(link.url, self.allow_res)
        if self.deny_res:
            allowed &= not _matches(link.url, self.deny_res)
        if self.allow_domains:
            allowed &= url_is_from_any_domain(parsed_url, self.allow_domains)
        if self.deny_domains:
            allowed &= not url_is_from_any_domain(parsed_url, self.deny_domains)
        if self.deny_extensions:
            allowed &= not url_has_any_extension(parsed_url, self.deny_extensions)
        if allowed and self.canonicalize:
            link.url = canonicalize_url(parsed_url)
        return allowed

    def matches(self, url):
        if self.allow_domains and not url_is_from_any_domain(url, self.allow_domains):
            return False
        if self.deny_domains and url_is_from_any_domain(url, self.deny_domains):
            return False

        allowed = [regex.search(url) for regex in self.allow_res] if self.allow_res else [True]
        denied = [regex.search(url) for regex in self.deny_res] if self.deny_res else []
        return any(allowed) and not any(denied)
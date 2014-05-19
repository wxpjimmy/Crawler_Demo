"""
Module for processing Sitemaps.

Note: The main purpose of this module is to provide support for the
SitemapSpider, its API is subject to change without notice.
"""
import lxml.etree


class SitemapUtil(object):
    """Class to parse Sitemap (type=urlset) and Sitemap Index
    (type=sitemapindex) files"""

    def __init__(self, xmltext):
        xmlp = lxml.etree.XMLParser(recover=True, remove_comments=True, resolve_entities=False)
        self._root = lxml.etree.fromstring(xmltext, parser=xmlp)
        rt = self._root.tag
        self.type = self._root.tag.split('}', 1)[1] if '}' in rt else rt

    def __iter__(self):
        for elem in self._root.getchildren():
            d = {}
            for el in elem.getchildren():
                tag = el.tag
                name = tag.split('}', 1)[1] if '}' in tag else tag

                if name == 'link':
                    if 'href' in el.attrib:
                        d.setdefault('alternate', []).append(el.get('href'))
                elif name == 'news':
                    for item in el.getchildren():
                        itag = item.tag
                        iname = itag.split('}', 1)[1] if '}' in itag else itag
                        if iname in ['title', 'publication_date']:
                            d[iname] = item.text.strip() if item.text else ''
                        else:
                            pass
                else:
                    d[name] = el.text.strip() if el.text else ''

            if 'loc' in d:
                yield d


def sitemap_urls_from_robots(robots_text):
    """Return an iterator over all sitemap urls contained in the given
    robots.txt file
    """
    for line in robots_text.splitlines():
        if line.lstrip().startswith('Sitemap:'):
            yield line.split(':', 1)[1].strip()
__author__ = 'Adam'
from bs4 import BeautifulSoup
from data import format_templates, accurate_data
from css_selector_algorithm_3 import SourceScraper
ss = SourceScraper(accurate_data['yelp'], format_templates['yelp'])
#print ss._get_class_based_selectors('name', 'html > body', 'div', ['class1', 'class2', 'class3'])
#print ss.build_selector_element_list(BeautifulSoup('<html somattr="SOMEATTRVAL"><head></head><body><div id="notsaskatoon"></div><div class="a" id="city">saskatoon</div></body></html>').find('div', text='saskatoon'))
#print ss.build_selector(ss.build_selector_element_list(BeautifulSoup('<html somattr="SOMEATTRVAL"><head></head><body><div id="notsaskatoon"></div><div class="a" id="city">saskatoon</div></body></html>').find('div', text='saskatoon')), 'city')
for k, v in ss.get_single_occurrence_selectors().iteritems():
    print k
    for i in v:
        print '\t', i


"""
from bs4 import BeautifulSoup
from data import format_templates, accurate_data
from css_selector_algorithm_3 import SourceScraper
ss = SourceScraper(accurate_data['urbanspoon'], format_templates['urbanspoon'])
#print ss._get_class_based_selectors('name', 'html > body', 'div', ['class1', 'class2', 'class3'])
#print ss.build_selector_element_list(BeautifulSoup('<html somattr="SOMEATTRVAL"><head></head><body><div id="notsaskatoon"></div><div class="a" id="city">saskatoon</div></body></html>').find('div', text='saskatoon'))
#print ss.build_selector(ss.build_selector_element_list(BeautifulSoup('<html somattr="SOMEATTRVAL"><head></head><body><div id="notsaskatoon"></div><div class="a" id="city">saskatoon</div></body></html>').find('div', text='saskatoon')), 'city')
ss.get_single_occurrence_selectors()
"""

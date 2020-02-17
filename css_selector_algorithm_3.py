#TODO: IDEAS TO INCREASE RESULT QUALITY AND USABILITY

#TODO: Analyze markup for business related information? For example, yelp uses the class
#TODO: biz-country-ca for canadian companies and biz-country-us for american companies

#TODO: When comparing against other accurate data, if we know the country/state/etc... are the same
#TODO: Then that information can be used for calculating a score for the selector because if the
#TODO: Selectors are very different, then odds are they aren't what we want since we know at least those
#TODO: values should be the same. E.G: It would filter out things like reviews that mention the city since
#TODO: lots of information in the tag is likely only good if it's something like "555 road, 90210, saskatoon, sk, ca"
#TODO: instead of "Hey, I went to saskatoon and tried this great food"

#TODO: Make sure accurate data includes edge cases and multiple cities/states/countries in case there are
#TODO: classes/attributes/tags that are location specific.

#TODO: Could pass the soup/comparison soups into get_single_occurrence_selectors so that it can be more easily
#TODO: used to compare segments of a page instead of just different pages. This would make it usable for finding
#TODO: things like multiple reviews on a page, or listings when all the listings are on one page, or analyzing
#TODO: search results

#TODO: Build python code that gets executed instead of using select? Would this be faster/have more options?
#TODO: Would it be a good fallback if select is actually faster, but more limited (it is more limited)?

#TODO: make skip_substring_check go down to a datatype level on the url. So if we want to check state, then
#TODO: skip_substring_check will return False if the state is a substring of another datatype value in that data,
#TODO: but if we are checking city then skip_substring_check may return differently. E.G.: If city is a substring of
#TODO: company name, then it would return True

#TODO: in get_selector_for_each_data_instance we may want to use a couple for initial comparison,
#TODO: or build the unique selectors for every successful case in any of the pages
#TODO: so that if this page happens to suck we don't just fail

import re
from bs4 import BeautifulSoup
from itertools import combinations, chain
from operator import add
from urllib2 import urlopen
DEBUG = False
INFO = False


class SourceScraper(object):
    CONTENT_TYPES = ['name', 'phone_number', 'city', 'state', 'zip', 'address']
    TERMINAL_TAG = '[document]'
    BAD_TAGS = ['script']
    BAD_CLASSES = []  # Might want to avoid using classes for things like page formatting in jquery
    BAD_ATTRIBUTES_NAMES = []
    GOOD_ATTRIBUTE_PRIORITY = ['itemprop']
    GOOD_TAG_PRIORITY = ['address', 'title', 'a', 'span', 'li']
    GOOD_CLASS_PRIORITY = []
    MIN_SELECTOR_SCORE = 0  # Out of 100
    SUB_SCORE_WEIGHTS = {
        'good_content': 1,
        'bad_content': 1,
        'selector_quality': 1,
        'selector_success': 1,
    }
    CLASS_SELECTION_TEMPLATES = [
        u'.{classes}',
        u'{tag}.{classes}',
        u'{parent}{separator}.{classes}',
        u'{parent}{separator}{tag}.{classes}',
    ]
    ATTR_SELECTION_TEMPLATE = u'{parent}{separator}{tag}[{attr}{sign}{attr_value}]'
    ID_SELECTION_TEMPLATE = u'#{0}'
    PRIMARY_POSITION_TEMPLATE = u'{parent}{separator}{tag}'
    ALTERNATE_POSITION_TEMPLATE = u'{parent}{separator}{tag}:nth-of-type({position})'

    def __init__(self, accurate_source_data, source_templates):
        """
        :arg accurate_source_data: A dictionary of listing information known to be correct in the format
            {
                '<url to listing>: {
                    '<data type>': '<content expected to be found>',
                    ...
                    '<data type with multiple segments>: {
                        '<segment name>': '<content expected to be found>',
                        ...
                    },
                    ...
                },
                ...
            }
        :arg source_templates: a dict of the templates that data types split into segments should follow in the format
            {
                '<data type with multiple segments>': '<string template for said segments>',
                ...
            }
        """
        self.accurate_source_data = accurate_source_data
        self.source_templates = source_templates

        self._fetch_url_data()
        self._format_accurate_source_data()

    @staticmethod
    def _debug(indent, *args):
        """
        Print the text you want if DEBUG is True
        :param indent: how many tabs the line should be indented
        :param args: what to print in the format "(<title>, <value>), (...), ..."
        """
        if DEBUG:
            for name, value in args:
                print u'{indent}{name}:\t\t{value}'.format(indent='\t'*indent, name=name, value=value)
            print

    def _fetch_url_data(self):
        """
        Prefetch all pages for optimization since the data is reviewed multiple times
        Creates test soups with new lines and capitalization removed
        """
        self.soups = {
            url: BeautifulSoup(self.clean_text(urlopen(url).read()))
            for url in self.accurate_source_data.iterkeys()
        }

    def _format_accurate_source_data(self):
        """
        Applies formatting templates to convert dictionaries of values to strings and removes
        any string formatting that was also removed from the soups to make comparisons easier
        """
        for url, correct_content in self.accurate_source_data.iteritems():
            for content_type, expected_value in correct_content.iteritems():
                if isinstance(expected_value, dict):
                    expected_value = self.source_templates[content_type].format(**expected_value)
                self.accurate_source_data[url][content_type] = self.clean_text(expected_value)

    def _get_scored_id_based_selectors(self, tag_id, key_data_type, parent_selector, tag_name):
        """

        :param key_data_type:
        :param tag_id:
        :return:
        """
        if tag_id:
            new_selector = self.ID_SELECTION_TEMPLATE.format(tag_id)
            return [(new_selector, self.check_selector_success(new_selector, key_data_type))]
        else:
            return []

    def _get_scored_class_based_selectors(self, classes, key_data_type, parent_selector, tag_name):
        """

        :param key_data_type:
        :param classes:
        :param parent_selector:
        :param tag_name:
        :return:
        """
        return [
            (new_selector, self.check_selector_success(new_selector, key_data_type))
            for new_selector
            in chain(*[
                [
                    template.format(
                        parent=parent_selector,
                        separator=' > ' if parent_selector else '',
                        tag=tag_name,
                        classes=class_combo
                    )
                    for class_combo
                    in (
                        '.'.join(x)
                        for x
                        in chain(*[
                            combinations(classes, length)
                            for length in xrange(1, 1 + len(classes))
                        ])
                    )
                ]
                for template
                in self.CLASS_SELECTION_TEMPLATES
            ])
        ]

    def _get_scored_attribute_based_selectors(self, attributes, key_data_type, parent_selector, tag_name):
        """

        :param key_data_type:
        :param attributes:
        :param parent_selector:
        :param tag_name:
        :return:
        """
        return [
            (new_selector, self.check_selector_success(new_selector, key_data_type))
            for new_selector
            in (
                self.ATTR_SELECTION_TEMPLATE.format(
                    parent=parent_selector,
                    separator=' > ' if parent_selector else '',
                    tag=tag_name,
                    attr=attr,
                    attr_value=attr_value,
                    sign='=' if attr_value else ''
                )
                for attr, attr_value
                in attributes.iteritems()
                if attr not in ['id', 'class']
                and isinstance(attr_value, str)
                #TODO: Remove this when BeautifulSoup supports dashes in attribute names
                #TODO: https://bugs.launchpad.net/beautifulsoup/+bug/1304007 as supposed to be a fix for the issue
                and '-' not in attr
                #TODO: Change this to allow spaces when BeautifulSoup supports
                #TODO: spaces in attribute values, will also require quotes
                and ' ' not in attr_value
                and attr_value.isalnum()
            )
        ]

    def _get_scored_position_based_selectors(self, sibling_position, key_data_type, parent_selector, tag_name):
        """

        :param key_data_type:
        :param sibling_position:
        :param parent_selector:
        :param tag_name:
        :return:
        """
        if sibling_position == 1:
            template = self.PRIMARY_POSITION_TEMPLATE
        else:
            template = self.ALTERNATE_POSITION_TEMPLATE
        new_selector = template.format(
            separator=' > ' if parent_selector else '',
            parent=parent_selector,
            tag=tag_name,
            position=sibling_position
        )
        return [(new_selector, self.check_selector_success(new_selector, key_data_type))]

    def build_selector(self, selector_element_list, key_data_type, selector=''):
        """
        Creates a CSS selector that
        :param selector_element_list:
        :param key_data_type:
        :return: A CSS selector that can be used to find the type of data that key_data_type is specifying
        """
        if INFO:
            print '.',
        # Work with the topmost element and return the current selector if there are no elements left
        if selector_element_list:
            element = selector_element_list.pop(0)
        else:
            if INFO:
                print '^'
            return selector
        # Build the selector segment options
        args = [key_data_type, selector, element['name']]
        selector_score_map = self._get_scored_id_based_selectors(element['attributes'].get('id'), *args)
        selector_score_map += self._get_scored_class_based_selectors(element['attributes'].get('class', []), *args)
        selector_score_map += self._get_scored_attribute_based_selectors(element['attributes'], *args)
        selector_score_map += self._get_scored_position_based_selectors(element['sibling_position'], *args)
        # Order selector list based on quality from best at 0 to worst at -1
        selector_score_map.sort(key=lambda x: x[1], reverse=True)
        # Step down a level to the child element and add a selector segment to get to that
        for best_selector, score in selector_score_map:
            more_precise_selector = self.build_selector(selector_element_list, key_data_type, selector=best_selector)
            if more_precise_selector:
                if INFO:
                    print '>',
                return more_precise_selector
            if INFO:
                print 's',
        # Ran out of selector usable segments for this level so this branch failed to find the data
        if INFO:
            print 'x'
        return ''

    @classmethod
    def build_selector_element_list(cls, current_element):
        """
        Builds a list of the tags a selector can use to find the data in current_element
        NOTE: Any class listed in BAD_CLASSES is not included as a class in the response
        :param current_element: the BeautifulSoup navigable string for the tag in which the selector should find data
        :return: A list of tags a CSS selector can use to find the data in current_element in the format
                 [
                    <outermost element>,
                    {'name': '<tag name>', 'attributes': {<tag attributes>}, 'sibling_position': <nth-of-type number>}
                    , ...,
                    <current_element>
                 ]
        """
        path = []
        while current_element.parent.name != cls.TERMINAL_TAG:
            if current_element.name in cls.BAD_TAGS:
                return None
            sibling_position = 1
            previous_sibling = current_element.previous_sibling
            while previous_sibling is not None:
                if previous_sibling.name == current_element.name:
                    sibling_position += 1
                previous_sibling = previous_sibling.previous_sibling
            current_element.attrs['class'] = [
                klass for klass in current_element.attrs.get('class', []) if klass not in cls.BAD_CLASSES
            ]
            path.insert(0, {
                'name': current_element.name,
                'attributes': current_element.attrs,
                'sibling_position': sibling_position
            })
            current_element = current_element.parent
        return path

    def check_selector_success(self, selector, key_data_type):
        """
        Using the selector on each soup and finds out how many soups for which the selector found the correct data
        :param selector: the CSS selector to use on each page
        :param key_data_type: the type of data to look for
        :return: the rate of success this selector had (0 to 1)
        """
        #TODO: Possibly make this score or more than just how many results are returned.
        #TODO: Could be the same or similar logic to the final prioritization possibly
        #TODO: Take into account ATTRIBUTE_PRIORITY
        score = reduce(
            add,
            [
                100
                for url, soup in self.soups.iteritems()
                if self.non_substring_data_instance_exists(url, selector, key_data_type)
                and len(soup.select(selector))
                and self.accurate_source_data[url][key_data_type] in soup.select(selector)[0].text
            ] or [0]
        ) / len(self.soups)
        if DEBUG:
            for soup in self.soups.itervalues():
                find = soup.select(selector)
                self._debug(0, ('CHECK SUCCESS FOR', selector), ('RESULT', find[0].text if find else 'FAILED'))
            self._debug(0, ('SUCCESS SCORE', score))
        return score

    def non_substring_data_instance_exists(self, url, selector, key_data_type):
        """
        Finds out if the data type value found is just a substring of another data type value
        :return: True if this is a real find, False if it is only substring of other data type values

        # TODO: optimize this function with skip_substring_check
        if self.skip_substring_check[url]:
            return True
        accurate_data = self.accurate_source_data.viewvalues()[0]
        for url, soup in self.soups.iteritems():
            selected_text = soup.select(selector).text
            for data_type, data_value in accurate_data:
                index = 0
                keep_trying = True
                while keep_trying:
                    selected_text.find(data_value, start=index)
                # Find out which types of content show up using the selector
                existing_content_types = accurate_data.keys()
                selector_contents = lambda x: soup.select(x) and soup.select(x)[0].contents
                    and soup.select(x)[0].contents[0] or ''
                occurrence_positions = {
                    existing_content_type: [
                        (x.start(), x.start()+len(accurate_data[url][existing_content_type]))
                        for x
                        in re.finditer(
                            self.clean_text_for_regex(accurate_data[url][existing_content_type]),
                            selected_text
                        )
                    ]
                    for existing_content_type in existing_content_types + [data_type]
                }

        """
        #TODO: Make this function work
        return True

    @property
    def skip_substring_check(self):
        """
        One type of data could be a substring of another type of data which can screw up finding the best
        selector. E.G.: in {'state': 'sk', 'city':'saskatoon'} sk is a substring of saskatoon. If this
        doesn't happen in the data then this time consuming check doesn't have to be done, so this function
        finds out if the check needs to be done
        :return: True if content sub strings are an issue, False if they are not
        """
        # TODO: use of this function can be better optimized by narrowing down to data type instead of url
        # TODO: If we know which types are substrings of which types then those are all we need to worry about
        if not hasattr(self, '_skip_substring_check'):
            self._skip_substring_check = {}
            for url, page_content in self.accurate_source_data.iteritems():
                self._skip_substring_check[url] = True
                for data_type, value in page_content.iteritems():
                    for substring_data_type, substring_value in page_content.iteritems():
                        if substring_data_type != data_type:
                            if substring_value in value:
                                self._skip_substring_check[url] = False
                                break
                    if not self._skip_substring_check[url]:
                        break
        return self._skip_substring_check

    @staticmethod
    def clean_text(string):
        """
        Prepares a string for data comparison and searching by removing characters we never want
        :param string: The string to clean
        :return: The cleaned up string
        """
        return string.replace('\n', '').replace('\r', '').strip(' ').lower()

    @staticmethod
    def clean_text_for_regex(string):
        """
        Prepares a string to be searched for in a regular expression
        :param string: The search string
        :return: The search string with regex special characters escaped
        """
        return ''.join(('\{0}'.format(char) if char in '.^$?+*{}[]()|' else char for char in string))

    def get_selector_for_each_data_instance(self, data_type):
        # Pull any old page to use for finding selectors. The other data is to check how successful the selector is
        comparison_url = next(self.accurate_source_data.iterkeys())
        comparison_data = self.accurate_source_data.pop(comparison_url)
        comparison_soup = self.soups.pop(comparison_url)
        selectors = set()
        clean_search_string = self.clean_text_for_regex(comparison_data[data_type])
        #TODO: Remove this hack for apostrophes in text. Can't figure out how to handle apostrophes right now
        if "'" in clean_search_string:
            segments = clean_search_string.split("'")
            clean_search_string = ''
            for segment in segments:
                if len(segment) >= len(clean_search_string):
                    clean_search_string = segment
        regex = re.compile(clean_search_string)
        navigable_strings = comparison_soup.findAll(text=regex)
        self._debug(0, ('CLEAN SEARCH STRING', clean_search_string), ('SEARCH RESULTS', navigable_strings))
        for navigable_string in navigable_strings:
            final_tag = navigable_string.parent
            element_list = self.build_selector_element_list(final_tag)
            self._debug(1, ('NAVIGABLE STR:', navigable_string), ('FINAL TAG', final_tag), ('ELEMENTS', element_list))
            if element_list:
                if INFO:
                    print '\nG',
                selector = self.build_selector(element_list, data_type)
                if INFO:
                    print
                selectors.add(selector)
                self._debug(2, ('SELECTOR', selector))
            if '' in selectors:
                selectors.remove('')
        if INFO:
            print 'Selectors for: ', data_type
            for selector in selectors:
                print selector
            print

        self.accurate_source_data[comparison_url] = comparison_data
        self.soups[comparison_url] = comparison_soup
        return selectors

    def get_single_occurrence_selectors(self):
        """
        Generate the CSS selectors for a source with them ordered from best first to worst last
        :return: {'<content_type':[<best css selector path>, ..., <worst css selector path>]}
        """
        ranked_selectors = {}
        for content_type in self.CONTENT_TYPES:
            selectors = []
            for selector in self.get_selector_for_each_data_instance(content_type):
                score = self.get_selector_score(selector)
                if score > self.MIN_SELECTOR_SCORE:
                    print score
                    selectors.append((selector, score))
            selectors.sort(key=lambda x: x[1], reverse=True)
            ranked_selectors[content_type] = [ranked_selector for ranked_selector, _ in selectors]
        return ranked_selectors

    @classmethod
    def get_selector_score(cls, selector_path):
        sub_scores = {}

        # Build the score for the number of content types found with the selector
        sub_scores['good_content'] = 100

        # Build the score for the amount of extraneous data found with the selector
        sub_scores['bad_content'] = 100

        # Build the score for the quality of the selector itself
        sub_scores['selector_quality'] = 100

        # Build the score for the number of urls on which the selector found good data
        # TODO: Get this score from when it was computed earlier
        # TODO: Maybe just compute the whole score earlier in check_selector_success and keep the score?
        sub_scores['selector_success'] = 100

        # Build final score using weighted versions of all other scores
        score = reduce(add, (sub_scores[score_type] * weight for score_type, weight in cls.SUB_SCORE_WEIGHTS.items()))
        return score
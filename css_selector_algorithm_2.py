import re
import urllib2
from bs4 import BeautifulSoup

from data import format_templates, accurate_data, site_urls


# pages that don't work properly with this method
# http://www.yelp.com/biz/lazy-bear-san-francisco (phone, zip, state)
# http://www.yellowpages.ca/bus/Saskatchewan/Saskatoon/Urban-Barn/5223596.html (name)
# http://www.urbanspoon.com/r/23/1421264/restaurant/Pittsburgh/Penn-Hills/Green-Forest-Churrascaria-Penn-Hills-Twp (city?)

BAD_TAGS = ['script']
GOOD_TAGS = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a', 'span', 'i', 'div']
MIN_NUM_URLS_WITH_PATH = 2
HIERARCHY_ONLY = True
DEBUG = True


def regex_sanitization(x):
    return ''.join(('\{0}'.format(char) if char in '\.^$?+*{}[]()|' else char for char in x)).lower()


# I'm thinking I could build the selector paths with id, classes, and other attributes being selected for
# then compare them against other paths found from different urls and if the ids/classes/attrs differ
# then try to back changes off until the paths are the same, and find the data being looked for
# right now it works pretty well without id/class/attrs, the only real issue is with hierarchy being different

# -Dont use IDs if there are duplicates on the page
# -Drop parent tags if an ID/Class/Custom attribute is found to make restructuring cause fewer problems

def build_selector_path(navigable_string, comparison_soups):
    """
    Converts a navigable string into a css selector path
    :param navigable_string: A NavigableString
    :return: the css selector path to the given NavigableString
    """
    path = []
    current_position = navigable_string
    while current_position.parent.name != '[document]':
        current_position = current_position.parent
        selector_text = current_position.name
        if selector_text in BAD_TAGS:
            return None

        if not HIERARCHY_ONLY:
            if 'id' in current_position.attrs:
                selector_text += '#{id}'.format(id=current_position.attrs.pop('id'))

                # Only use IDs that return results over multiple urls since IDs with long numbers seem to be a thing

            if '#' not in selector_text and 'class' in current_position.attrs:
                for klass in current_position.attrs.pop('class'):
                    selector_text += '.{0}'.format(klass)
                # Have to use nth-of-type if using classes doesn't narrow down to 1 tag because nth-of-type
                # can't be used in combination with selecting on classes
                if len() > 1:
                    selector_text

            # Other attributes work if there aren't spaces in them.
            # e.g.: <div someattr='ABC'></div> can be found using [someattr=ABC] while <div someattr='A B C'></div>
            # can only be found by one of [someattr~=A] or [someattr~=B] or [someattr~=C]
            # I think [someattr="A B C"] should work according to the standards, but it throws an error
            # ALSO beautiful soup only seems to support one attr being selected for so just go with the first one for
            # now I guess, but I would like to make it go for one that has a synonym for the content type being found
            # if possible, otherwise just go with the first. Could also just check them all when comparing against
            # other URLs to see which works best
            for attribute, attribute_value in current_position.attrs.iteritems():
                if ' ' not in attribute_value:
                    selector_text += '[{0}={1}]'.format(attribute, attribute_value)
                    break  # So that we only take the first attribute for now

        # need to choose the correct child if there are more than one of the same type of tag at the same level
        sibling_position = 1
        previous_sibling = current_position.previous_sibling
        while previous_sibling is not None:
            if previous_sibling.name == current_position.name:
                sibling_position += 1
            previous_sibling = previous_sibling.previous_sibling
        if sibling_position > 1:
            selector_text += ':nth-of-type({position})'.format(position=sibling_position)

        path.append(selector_text)
    path.reverse()
    return ' > '.join(path)


def get_selector_paths(site_name, accurate_data, format_templates):
    # Prefetch all pages for optimization since the data is reviewed multiple times
    soups = {}
    for url, correct_content in accurate_data.iteritems():
        # Create test soups with new lines and capitalization removed
        soups[url] = BeautifulSoup(urllib2.urlopen(url).read().replace('\n', '').replace('\r', '').lower())
        for content_type, expected_value in correct_content.iteritems():
            # Apply formatting template if there is one available
            if isinstance(expected_value, dict):
                expected_value = format_templates[content_type].format(**expected_value)
            # Remove capitalization from comparison data
            accurate_data[url][content_type] = expected_value.lower()
    # Loop through different pages to find content in them and paths to said content
    selector_paths = {}
    selector_paths_content_positions = {}
    for url, correct_content in accurate_data.iteritems():
        soup = soups[url]
        selector_paths[url] = {}
        selector_paths_content_positions[url] = {}
        for content_type, correct_value in correct_content.iteritems():
            # Good tags that contain text
            paths_to_content = (
                y for y
                in (build_selector_path(x, [soups[url]]) for x in soup.findAll(text=re.compile(regex_sanitization(correct_value))))
                if y is not None
            )

            # Clean up paths and build up data around them needed for pulling content at the path
            for path in paths_to_content:
                # Find out which types of content show up using the selector
                existing_content_types = selector_paths[url].get(path, [])
                selector_contents = lambda x: soup.select(x) and soup.select(x)[0].contents and soup.select(x)[0].contents[0] or ''
                occurrence_positions = {
                    existing_content_type: [
                        (x.start(), x.start()+len(accurate_data[url][existing_content_type]))
                        for x
                        in re.finditer(
                            regex_sanitization(accurate_data[url][existing_content_type]),
                            selector_contents(path).text if hasattr(selector_contents(path), 'text') else selector_contents(path)
                        )
                    ]
                    for existing_content_type in existing_content_types + [content_type]
                }
                existing_occurrence_positions = occurrence_positions.copy()
                del existing_occurrence_positions[content_type]

                # Clean out substring occurrences (e.g. state 'sk' is not actually in '8th street, saskatoon', but we will find it inside 'saskatoon')
                for existing_content_type, existing_content_type_positions in existing_occurrence_positions.iteritems():
                    for (existing_occurrence_start, existing_occurrence_end) in existing_content_type_positions:
                        for (new_occurrence_start, new_occurrence_end) in occurrence_positions[content_type]:
                            # new content type is a substring at this occurrence so remove it
                            if new_occurrence_start >= existing_occurrence_start and new_occurrence_end <= existing_occurrence_end:
                                occurrence_positions[content_type].remove((new_occurrence_start, new_occurrence_end))
                            # existing content type is a substring at this occurrence so remove it
                            elif existing_occurrence_start >= new_occurrence_start and existing_occurrence_end <= new_occurrence_end:
                                occurrence_positions[existing_content_type].remove((existing_occurrence_start, existing_occurrence_end))
                    # Remove the existing content type if the finds were all false positives
                    if not len(occurrence_positions[existing_content_type]):
                        del existing_content_types[existing_content_type]
                # Add the new content type if the finds weren't all false positives
                if len(occurrence_positions[content_type]):
                    existing_content_types.append(content_type)

                # Set information relating to the selector path
                if existing_content_types:
                    selector_paths[url][path] = existing_content_types
                    selector_paths_content_positions[url][path] = {x: occurrence_positions[x] for x in existing_content_types}
    # Filter out selector paths that don't show up over enough URLs
    # Maybe compare differences in selector paths and drop differences in them (like IDs and classes)
    #     and see if they still return results
    for url, selector_paths_on_url in selector_paths.copy().iteritems():
        for path, types in selector_paths_on_url.copy().iteritems():
            num_urls_with_path = 1
            for comparison_url in selector_paths.iterkeys():
                if url != comparison_url and path in selector_paths[comparison_url]:
                    num_urls_with_path += 1
            if num_urls_with_path < MIN_NUM_URLS_WITH_PATH:
                if DEBUG:
                    print 'REMOVING SELECTOR', '\t\t', selector_paths[url][path], '\t\t', path, '\t\t', url
                del selector_paths[url][path]
            else:
                if DEBUG:
                    print 'KEEPING SELECTOR', '\t\t', selector_paths[url][path]
    # Prioritize selectors so those with the least amount of garbage content are chosen first
    # and create the formatting function for the data
    # Prefer selectors with the same garbage data layouts (i.e. the garbage data looks the same over multiple pages)
    garbage = {}
    content_order = {}
    for url, selector_paths_on_url in selector_paths.iteritems():
        soup = soups[url]
        garbage[url] = {}
        content_order[url] = {}
        for path, types in selector_paths_on_url.iteritems():
            positions_last_to_first = []
            for type_at_positions, positions in selector_paths_content_positions[url][path].iteritems():
                positions_last_to_first += [(s, e, type_at_positions) for (s, e) in positions]
            positions_last_to_first.sort(key=lambda z: z[0], reverse=True)
            field_contents = soup.select(path)[0].contents[0].text if hasattr(soup.select(path)[0].contents[0], 'text') else soup.select(path)[0].contents[0]
            garbage[url][path] = []
            content_order[url][path] = content_order[url].get(path, [])
            for (start, end, type_at_position) in positions_last_to_first:
                if field_contents[end:]:
                    garbage[url][path].append(field_contents[end:])
                field_contents = field_contents[0:start]
                content_order[url][path].append(type_at_position)
            if field_contents:
                garbage[url][path].append(field_contents)
            garbage[url][path].reverse()
            content_order[url][path].reverse()

    # Use the selector content with the least garbage for each content type
    content_types = ['name', 'phone_number', 'address', 'zip', 'city', 'state'] # , 'country']
    final_selector_paths = {}
    final_selector_trash = {}
    final_selector_content_order = {}
    for content_type in content_types:
        lowest = 1000
        best_path = None
        for url, selector_paths_on_url in selector_paths.iteritems():
            soup = soups[url]
            for path, garbage_content in garbage[url].iteritems():
                garbage_content_length = len(''.join(garbage_content))
                if content_type in selector_paths[url][path] and garbage_content_length < lowest:
                    lowest = garbage_content_length
                    best_path = path
        final_selector_paths[content_type] = best_path
        final_selector_trash[content_type] = garbage[url].get(best_path)
        final_selector_content_order[content_type] = content_order[url].get(best_path)

    return final_selector_paths, final_selector_trash, final_selector_content_order


if __name__ == '__main__':
    # Find some selectors
    for site_name in accurate_data.iterkeys():
        print '{0:-^90}'.format(site_name)
        selector_paths, selector_trash, selector_content_order = get_selector_paths(site_name, accurate_data[site_name], format_templates[site_name])

        # Use the selectors on the sites and see how the data looks
        for url in site_urls[site_name]:
            print '\t{0}'.format(url)
            soup = BeautifulSoup(urllib2.urlopen(url).read().replace('\n', '').replace('\r', '').lower())

            for name, path in selector_paths.iteritems():
                data = None
                if path:
                    data = soup.select(path)
                    if len(data):
                        data = data[0].contents
                        if len(data):
                            data = data[0]
                            if hasattr(data, 'text'):
                                data = data.text
                            else:
                                data = unicode(data).encode('utf8')
                if not data:
                    data = 'no selector found'

                dirty_content = data
                cleaned_content = []
                if selector_trash[name]:
                    #selector_trash[name].reverse()
                    for trash_piece in selector_trash[name]:
                        if dirty_content.split(trash_piece, 1)[0]:
                            cleaned_content.append(dirty_content.split(trash_piece, 1)[0])
                        if len(dirty_content.split(trash_piece, 1)) > 1:
                            dirty_content = dirty_content.split(trash_piece, 1)[1]
                        else:
                            dirty_content = ''
                    if dirty_content:
                        cleaned_content.append(dirty_content)
                    try:
                        # 'http://www.yellowpages.ca/bus/Saskatchewan/Saskatoon/Urban-Barn/5223596.html' is getting
                        # a selector with only name, city, and state for the address selector
                        # 'html[xmlns:fb=http://ogp.me/ns/fb#] > head > title' for some reason
                        content_index = selector_content_order.get(name, []).index(name)
                    except ValueError as e:
                        pass
                    if len(cleaned_content) > content_index:
                        cleaned_content = cleaned_content[content_index].strip(' ')
                    else:
                        cleaned_content = ''
                else:
                    cleaned_content = data.strip(' ')
                if DEBUG:
                    print '\t\t{name:-<30}{data:-<30}{trash:-<30}{content_order:-<30}{output}'.format(
                        name=name, data=data, trash=selector_trash[name], content_order=selector_content_order[name],
                        output=cleaned_content
                    )
                else:
                    print '\t\t{name:-<20}{output}'.format(name=name, output=cleaned_content)
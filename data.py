format_templates = {
    'urbanspoon': {
        'phone_number': '({area_code}) {prefix}-{line_number}',
        'address': '{number} {name} {type} {direction}',
    },
    'yelp': {
        'phone_number': '({area_code}) {prefix}-{line_number}',
        'address': '{number} {name} {type} {direction}',
    },
    'yellowpages': {
        'phone_number': '{area_code}-{prefix}-{line_number}',
        'address': '{number} {name} {type} {direction}',
    },
}


accurate_data = {
    'urbanspoon': {
        'http://www.urbanspoon.com/r/281/1422761/restaurant/Downtown/Spadina-Freehouse-Saskatoon': {
            'name': 'Spadina Freehouse',
            'phone_number': {
                'area_code': '306',
                'city_code': '',
                'prefix': '668',
                'line_number': '1000',
            },
            'address': {
                'number': '608',
                'name': 'Spadina',
                'type': 'Cres',
                'direction': 'E',
            },
            'zip': 'S7K3G8',
            'city': 'Saskatoon',
            'state': 'SK',
            #'country': 'CA',
        },
        "http://www.urbanspoon.com/r/281/1674489/restaurant/Downtown/Earls-Restaurant-Saskatoon": {
            'name': 'Earls Restaurant',
            'phone_number': {
                'area_code': '306',
                'city_code': '',
                'prefix': '664',
                'line_number': '4060',
            },
            'address': {
                'number': '610',
                'name': '2nd',
                'type': 'Avenue',
                'direction': 'N',
            },
            'zip': 'S7K2C8',
            'city': 'Saskatoon',
            'state': 'SK',
            #'country': 'CA',
        },
        "http://www.urbanspoon.com/r/281/1442867/restaurant/Downtown/Flint-Saskatoon": {
            'name': 'Flint',
            'phone_number': {
                'area_code': '306',
                'city_code': '',
                'prefix': '651',
                'line_number': '2255',
            },
            'address': {
                'number': '259',
                'name': '2nd',
                'type': 'Avenue',
                'direction': 'South',
            },
            'zip': 'S7K1K8',
            'city': 'Saskatoon',
            'state': 'SK',
            #'country': 'CA',
        },
    },
    'yelp': {
        'http://www.yelp.ca/biz/spadina-freehouse-saskatoon-2': {
            'name': 'Spadina Freehouse',
            'phone_number': {
                'area_code': '306',
                'city_code': '',
                'prefix': '668',
                'line_number': '1000',
            },
            'address': {
                'number': '608',
                'name': 'Spadina',
                'type': 'Cres',
                'direction': 'E',
            },
            'zip': 'S7K 3G9',
            'city': 'Saskatoon',
            'state': 'SK',
            #'country': 'CA',
        },
        "http://www.yelp.ca/biz/earls-restaurant-and-lounge-saskatoon": {
            'name': "Earl's Restaurant",
            'phone_number': {
                'area_code': '306',
                'city_code': '',
                'prefix': '664',
                'line_number': '4060',
            },
            'address': {
                'number': '610',
                'name': '2nd',
                'type': 'Avenue',
                'direction': 'N',
            },
            'zip': 'S7K 2C8',
            'city': 'Saskatoon',
            'state': 'SK',
            #'country': 'CA',
        },
        "http://www.yelp.ca/biz/flint-saskatoon": {
            'name': 'Flint',
            'phone_number': {
                'area_code': '306',
                'city_code': '',
                'prefix': '651',
                'line_number': '2255',
            },
            'address': {
                'number': '259',
                'name': '2nd',
                'type': 'Ave',
                'direction': 'S',
            },
            'zip': 'S7K 1K8',
            'city': 'Saskatoon',
            'state': 'SK',
            #'country': 'CA',
        },
    },
    'yellowpages': {
        'http://www.yellowpages.ca/bus/Saskatchewan/Saskatoon/Urban-Barn/5223596.html': {
            'name': 'Urban Barn',
            'phone_number': {
                'area_code': '306',
                'city_code': '',
                'prefix': '933',
                'line_number': '9770',
            },
            'address': {
                'number': '3142',
                'name': 'Clarence',
                'type': 'Ave',
                'direction': 'S',
            },
            'zip': 'S7T 0C9',
            'city': 'Saskatoon',
            'state': 'SK',
            #'country': 'CA',
        },
        "http://www.yellowpages.ca/bus/Saskatchewan/Saskatoon/Red-Lobster/100217036.html": {
            'name': 'Red Lobster',
            'phone_number': {
                'area_code': '306',
                'city_code': '',
                'prefix': '500',
                'line_number': '0239',
            },
            'address': {
                'number': '2501',
                'name': '8th',
                'type': 'Street',
                'direction': 'E',
            },
            'zip': 'S7H 0V4',
            'city': 'Saskatoon',
            'state': 'SK',
            #'country': 'CA',
        },
        "http://www.yellowpages.ca/bus/Saskatchewan/Saskatoon/The-Greek-House/6692681.html": {
            'name': 'The Greek House',
            'phone_number': {
                'area_code': '306',
                'city_code': '',
                'prefix': '500',
                'line_number': '6133',
            },
            'address': {
                'number': '204',
                'name': '33rd',
                'type': 'St',
                'direction': 'W',
            },
            'zip': 'S7L 0V1',
            'city': 'Saskatoon',
            'state': 'SK',
            #'country': 'CA',
        },
    },
}

new_site_urls = {
    'urbanspoon': [
        'http://www.urbanspoon.com/r/281/1423373/restaurant/8th-Street/The-Granary-Saskatoon',
        'http://www.urbanspoon.com/r/23/1421264/restaurant/Pittsburgh/Penn-Hills/Green-Forest-Churrascaria-Penn-Hills-Twp',
        'http://www.urbanspoon.com/r/23/271548/restaurant/Downtown-CBD/Ruths-Chris-Steak-House-Pittsburgh',
    ],
    'yelp': [
        'http://www.yelp.ca/biz/the-granary-saskatoon',
        'http://www.yelp.com/biz/lazy-bear-san-francisco',
        'http://www.yelp.com/biz/gary-danko-san-francisco',
    ],
    'yellowpages': [
        'http://www.yellowpages.ca/bus/Saskatchewan/Furdale/The-Willows/4401138.html',
        'http://www.yellowpages.ca/bus/Saskatchewan/Saskatoon/Orange-Julius/5987059.html',
        'http://www.yellowpages.ca/bus/Saskatchewan/Saskatoon/Smitty-s-Family-Restaurant/2541264.html',
    ]
}

site_urls = {
    site_name: [url for url in site_data.iterkeys()] + new_site_urls[site_name]
    for site_name, site_data
    in accurate_data.iteritems()
}
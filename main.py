# encoding: utf8
from __future__ import print_function
from bs4 import BeautifulSoup
import re
import requests
import textwrap

address = '<your_place_here>'
endpoint_uri = (
    'https://www.just-eat.fr/restaurants-livraison-a-domicile/'
    'zone-livraison/' + address
)

def do_show_restaurants(cookies, token, page):
    results = requests.post(
        endpoint_uri,
        data=dict(mode='showMore', p=page),
        cookies=cookies,
        headers={'X-CSRF-TOKEN': token}
    ).json()
    restaurant_list = results['dataLayer']['serpData']['results']['trData']
    restaurants = {
        int(restaurant['trId']): restaurant for restaurant in restaurant_list
    }
    soup = BeautifulSoup(results['restaurants'], 'html.parser')

    for li in soup.ul.children:
        if not hasattr(li, 'div') or not li.div:
            continue
        id = int(li.div['data-ar-restaurant-id'])
        name = li.find(**{'class': 'name'}).a.text
        restaurant = restaurants[id]
        print(textwrap.dedent(u'''
            %s: >=%s€ + %s€ - %s
        ''' % (
            name.ljust(40),
            restaurant['minAmount'] or 0.0,
            restaurant['deliveryCost'] or 0.0,
            'Open' if restaurant['open'] else 'Closed'
        )).strip())

    if not int(soup.ul['data-ar-has-more']):
        return False
    return True

response = requests.get(endpoint_uri)

token_regexp = re.compile('meta name="csrf-token" content="(.*)"')
token = token_regexp.findall(response.text)[0]

for cookie in response.cookies:
    if cookie.name.startswith('__'):
        response.cookies.clear(domain=cookie.domain, path=cookie.path, name=cookie.name)

page = 0
while True:
    page += 1
    if not do_show_restaurants(response.cookies, token, page):
        break

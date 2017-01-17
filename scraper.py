"""Scrape health data."""
import requests
from bs4 import BeautifulSoup
import geocoder


URL = 'http://info.kingcounty.gov/health/ehs/foodsafety/inspections/Results.aspx'
SEARCH_PARAMS = {
    'Output': 'W',
    'Business_Name': '',
    'Business_Address': '',
    'Longitude': '',
    'Latitude': '',
    'City': 'Seattle',
    'Zip_Code': '',
    'Inspection_Type': 'All',
    'Inspection_Start': '',
    'Inspection_End': '',
    'Inspection_Closed_Business': 'A',
    'Violation_Points': '',
    'Violation_Red_Points': '',
    'Violation_Descr': '',
    'Fuzzy_Search': 'N',
    'Sort': 'B'
}


'''It must accept keyword arguments for the possible query parameters
It will build a dictionary of request query parameters from incoming keywords
It will make a request to the King County server using this query
It will return the bytes content of the response and the encoding if there is no error
It will raise an error if there is a problem with the response'''


def get_inspection_page(**queries):
    """Query king county health inspection data and return html content."""
    print('Requesting inspection page...')
    params = SEARCH_PARAMS.copy()
    for key, val in queries.items():
        if key in params:
            params[key] = val
    response = requests.get(URL, params=params)
    response.raise_for_status()
    with open('./inspection_page.html', 'w') as page:
        page.write(response.text)
    return response.content, response.encoding


def load_inspection_page(**queries):
    '''Return stored inspection data html.'''
    print('Loading inspection page...')
    with open('./inspection_page.html') as page:
        f = page.read()
    return f.encode(), 'utf-8'


def parse_source(r_body):
    '''Soupify html content.'''
    print('Soupifying...')
    return BeautifulSoup(r_body[0], 'html5lib', from_encoding=r_body[1])


def extract_data_listings(soup):
    '''Return list of divs containing inpsection data for each restaurant.'''
    def id_ends_with_squiggle(tag):
        return tag.has_attr('id') and tag.attrs['id'][-1] == '~'
    return soup.find(id='container').find(id='contentcol').find_all(id_ends_with_squiggle)


def has_two_tds(element):
    '''Return true if element is a tr and has two tds inside.'''
    return element.name == 'tr' and len(element.find_all('td')) == 2


def clean_data(cell):
    '''Return content of a td cell with extraneous chars removed.'''
    try:
        return cell.string.strip(' \n:-')
    except:
        return ''


def extract_restaurant_metadata(listing):
    '''Return a dictionary containing a restaurant's metadata.'''
    metadata = {}
    trs = listing.find('tbody').find_all(has_two_tds, recursive=False)
    for tr in trs:
        tds = tr.find_all('td', recursive=False)
        key = clean_data(tds[0])
        if key:
            metadata[key] = clean_data(tds[1])
        else:
            metadata['Address'] += ', ' + clean_data(tds[1])
    return metadata


def is_inspection_row(row):
    '''Return true if tr is an inspection row.'''
    tds = row.find_all('td')
    if row.name == 'tr' and len(tds) == 4:
        content = tds[0].string
        return 'Inspection' in content and content.split()[0] != 'Inspection'


def extract_score_data(listing):
    '''Return dict of inspection score info for a restaurant.'''
    inspection_rows = listing.find_all(is_inspection_row)
    high_score = 0
    total = 0
    for row in inspection_rows:
        score = int(row.find_all('td')[2].string)
        total += score
        if score > high_score:
            high_score = score
    if inspection_rows:
        avg_score = total / len(inspection_rows)
    else:
        avg_score = 'N/A'
    return {
        'High Score': high_score,
        'Average Score': avg_score,
        'Total Inspections': len(inspection_rows)
    }


def generate_results(args):
    if args.test:
        res = load_inspection_page()
    else:
        res = get_inspection_page(Zip_Code='98109')
    soup = parse_source(res)
    listings = extract_data_listings(soup)
    print('Extracting data...')
    if args.all:
        args.number = len(listings)
    for listing in listings[:args.number]:
        metadata = extract_restaurant_metadata(listing)
        score_data = extract_score_data(listing)
        metadata.update(score_data)
        yield metadata


def get_geojson(search):
    if search['Address']:
        response = geocoder.google(search['Address'])
        try:
            search['Address'] = response.json['address']
        except KeyError:
            pass
        del search['Longitude']
        del search['Latitude']
        geojson = response.geojson
        geojson['properties'] = search
        return geojson
    return None


if __name__ == '__main__':
    from pprint import pprint
    import json
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', "--test", help="use written file data", action='store_true')
    parser.add_argument('-s', "--sort", help="specify sort method")
    parser.add_argument('-n', "--number", help="specify number of results shown")
    parser.add_argument('-r', "--reverse", help="sort by lowest scores", action='store_true')
    parser.add_argument('-a', "--all", help="compare all", action='store_true')
    args = parser.parse_args()
    if not args.number:
        args.number = 10
    total_result = {'type': 'FeatureCollection', 'features': []}

    for result in generate_results(args):
        geojson = get_geojson(result)
        total_result['features'].append(geojson)
    if args.sort:
        sorts = {
            'highscore': 'High Score',
            'avgscore': 'Average Score',
            'numinspections': 'Total Inspections',
        }
        total_result['features'] = sorted(total_result['features'],
                                          key=lambda f: f['properties'][sorts[args.sort]],
                                          reverse=args.reverse)
    if args.all:
        total_result['features'] = total_result['features'][:args.number]
    pprint(total_result['features'])
    with open('my_map.json', 'w') as fh:
        json.dump(total_result, fh)

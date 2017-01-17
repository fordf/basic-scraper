# King County Restaurant Inspection Data Scraper Script

### To run:
python scraper.python

#### Options:
- -t (--test): Run script with saved html file.
- -n (--number): Specify number of results to be spit out. Default is 10.
- -s (--sort) (highscore, avgscore, numinspections): Specify a sorting method for results.
- -a (--all): Analyze and compare all restaurants. Use at own risk, it isn't optimized.
            Can still work in conjunction with -n.

### Output:
Prints list of geojson features for each restaurant that matches query parameters
(request parameters are hardcoded for now). Each feature contains properties made up of
metadata (restaurant name, address, etc.) and inspection data (average score,
high score, and number of inpsections).

Writes geojson to my_map.json.

#### Ex:
```
...
{'bbox': [-122.3481996, 47.6263575, -122.3477151, 47.6266153],
  'geometry': {'coordinates': [-122.3479573, 47.6264864], 'type': 'Point'},
  'properties': {'Address': '803 5th Ave N, Seattle, WA 98109, USA',
                 'Average Score': 20.357142857142858,
                 'Business Category': 'Seating 51-150 - Risk Category III',
                 'Business Name': 'MARINEPOLIS SUSHILAND',
                 'High Score': 100,
                 'Phone': '',
                 'Total Inspections': 28},
  'type': 'Feature'},
 ...
```

### Dependencies:

 - BeautifulSoup4
 - Requests
 - argparse
 - geocoder

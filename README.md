# King County Restaurant Inspection Data Scraper Script

To run: python scraper.python

Returns: List of dictionaries for each restaurant that matches query parameters
(request parameters are hardcoded for now). Each dictionary contains metadata like
restaurant name, address, etc. as well as inspection data average score,
high score, and number of inpsections. Longitudes are wrong.

Ex:
```
{'Address': '174 ROY ST, Seattle, WA 98109',
 'Average Score': 8.75,
 'Business Category': 'Seating 51-150 - Risk Category III',
 'Business Name': 'STREAMLINE TAVERN',
 'High Score': 10,
 'Latitude': '47.6256182493',
 'Longitude': '122.3529627079',
 'Phone': '(206) 931-9883',
 'Total Inspections': 4}
```

Built with BeautifulSoup and Requests libraries.
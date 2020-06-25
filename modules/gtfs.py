import requests
import json
from dotenv import load_dotenv
import os
import pandas as pd
load_dotenv()

# documentation for the TransitFeed API: https://transitfeeds.com/api/swagger/
# this script downloads all GTFS feeds within Canada, according to what is available from TransitFeed (OpenMobilityData) API

get_gtfs_feeds():
    key = os.environ.get('GTFS_API_KEY') # obtain a key through GitHub signup to OpenMobilityData
    location = '32' # location 32 is Canada

    # first, get the number of pages to retrieve all GTFS feeds in Canada
    url_pages = 'https://api.transitfeeds.com/v1/getFeeds?key='+key+'&location='+location+'&descendants=1&limit=100'
    page_number = json.loads(requests.get(url_pages).content)['results']['numPages']

    # loop through the pages and get all feeds within each page
    for page in range(page_number):
        # page starts at 1, not 0
        page += 1

        # retrieves feeds based on location specified (currently all GTFS feeds in Canada)
        url_feeds = 'https://api.transitfeeds.com/v1/getFeeds?key='+key+'&location='+location+'&descendants=1&page='+str(page)+'&limit=100'

        # store GTFS feeds within Canada
        feeds = json.loads(requests.get(url_feeds).content)

        # get zipped feed GTFS data per each feed
        for feed in feeds['results']['feeds']:

            # store feed id
            feed_id = feed['id']

            # create url to get specific feed from API
            url_get = 'https://api.transitfeeds.com/v1/getLatestFeedVersion?key='+key+'&feed='+feed_id

            # save downloaded feed into a data/gtfs folder
            with open('../data/gtfs/'+feed_id.replace('/','_')+'.zip', 'wb') as f:
                f.write(requests.get(url_get).content)
                f.close()

        total = json.loads(requests.get(url_pages).content)['results']['total']
        print(f'Completed {total}')

clip_osm():
    
    
#api():

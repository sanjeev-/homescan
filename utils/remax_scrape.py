from scraping_utils import *
import pandas as pd
import argparse    
from bs4 import BeautifulSoup
import time
import os
import sys
import subprocess
from datetime import datetime
import pickle
import pandas as pd
from django.core.wsgi import get_wsgi_application
import json
from dateutil import parser as dateparser
from scraping_utils import fetch_from_google_storage, send_to_google_storage
from scraping_utils import find_latest_csvname
from dateutil import parser

def df_filename():
    """This returns csv filename for today

    Keyword arguments:
        None

    Returns:
        df_filename: [string] csv filename data_[todays_date].csv
    """
    now = datetime.now()
    datestr = now.strftime('%Y%m%d')
    df_filename = 'data_{}.csv'.format(datestr)
    return df_filename

def implement_arg_parse():
    """This implements the command line arguments
    Keyword arguments:
        None
    
    Returns:
        Implements --city: [cl argument] city you want to scrape
                   --state: [cl argument] state you want to scrape

                   as command line arguments
    """
    parser = argparse.ArgumentParser(description='Process some arguments')
    parser.add_argument('--city',metavar='C',type=str,help='city that you want to scrape e.g. "charlotte" ')
    parser.add_argument('--state',metavar='S',type=str,help='two letter abbrv of the state of the city you want to scrape e.g. "NC"')
    arg_check = parser.parse_args()
    args = vars(parser.parse_args())
    return arg_check, args

def find_last_scrape_date(df):
    """Find the date of the most recently scraped property in the csv

    Keyword arguments:
        df: [pandas dataframe] dataframe of scraped properties from last scraped csv

    Returns:
        datetime of the most recently scraped property in the dataframe
    """
    df['features_start_date_on_site']=df['features_start_date_on_site'].apply(parser.parse)
    latest_date = max(df['features_start_date_on_site'])
    latest_date_datetime = latest_date.to_datetime()
    return latest_date_datetime

def check_date_vs_last_scrape_date(property_date,last_scrape_date):
    """Takes the date of a scraped property and compares it to the last scraped date
       in old dateframe

    Keyword arguments:
        property_date: [datetime] the date of a remax property to be scraped
        last_scrape_date: [datetime] the date of the most recently scraped property
                                     in the old dataframe

    Returns:
        is_ahead_of_last_scrape_date: [Boolean] True if more recent, else False
    """
    is_ahead_of_last_scrape_date = property_date >= last_scrape_date
    return is_ahead_of_last_scrape_date

def scrape_remax(city,state):
    """Loops through pages of Remax site, scraping data and stopping when hits StopDate

    Keyword arguments:
        city: [string] city of area you want to scrape
        state: [string] state of the area you want to scrape
        stop_date: [string] string (YYYY-MM-DD) of the date at which you wish to 
                            stop scraping

    Returns:
        csv of the dataframe
    """
    df_old = pd.read_csv('csv_data/'+csv_filename)
    last_scrape_date = find_last_scrape_date(df_old)
    d={}
    pg = 0
    keep_on_scraping = True
    while keep_on_scraping:
        pg += 1
        print('scraping page %s' % (str(pg)))
        page = createRemaxCityURL(city,state,pg)
        urls = findReMaxURLS(BeautifulSoup(get(page,verify=False).text,'html.parser'))
        for url in urls:
            try:
                print('napping for a bit')
                time.sleep(1.5)
                print(keep_on_scraping)
                home = pullHomeData(url)
                flat = flatten_dict(home)
                slug = flat['address_slug']
                d[slug] = flat
                property_date = parser.parse(home['features_start_date_on_site']).to_datetime()
                keep_on_scraping = check_date_vs_last_scrape_date(property_date,last_scrape_date)
                print('current propery date is: {}  last df property date is: {}'.format(property_date,last_scrape_date))
            except:
                    pass
        df_new = pd.DataFrame.from_dict(d,orient='index')
        df_combined = pd.concat([df_old, df_new])
        new_df_filename = df_filename()
        df_combined.to_csv(new_df_filename,encoding='utf-8')
    print('scraping update completed!')

if __name__ == '__main__':
    arg_check, args = implement_arg_parse()
    if arg_check.city == 'check_string_for_empty':
        print('you didnt supply a city.  please try again.')
    if arg_check.state == 'check_string_for_empty':
        print('you didnt supply a state.  please try again')
    city=args['city']
    state=args['state']
    print('scraping home data: ')
    csv_filename = find_latest_csvname()
    fetch_from_google_storage('rooftop-data','properties_data',csv_filename,
                              'csv_data')
    scrape_remax(city, state)
    new_df_filename = df_filename()
    send_to_google_storage('rooftop-data','properties_data',new_df_filename,'')
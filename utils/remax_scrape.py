from scraping_utils import *
import pandas as pd 
import argparse    
from bs4 import BeautifulSoup
import time
import os
import sys
import subprocess
import datetime
import pickle
import pandas as pd
from django.core.wsgi import get_wsgi_application
import json
from dateutil import parser as dateparser
#import urllib3

#urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# defining argparse
parser = argparse.ArgumentParser(description='Process some arguments')

parser.add_argument('--city',metavar='C',type=str,help='city that you want to scrape e.g. "charlotte" ')
parser.add_argument('--state',metavar='S',type=str,help='two letter abbrv of the state of the city you want to scrape e.g. "NC"')

arg_check = parser.parse_args()
args = vars(parser.parse_args())

def find_latest_csvname(specific_date='<YYYYMMDD>'):
    """Finds the newest csv name in the drive.  Can pull a specific date
       by filling in the specific date field.

    Keyword arguments:
        specific date: [string in YYYYMMDD date format ] This is optional.  Standard it to leave blank and it will 
                        pull the latest.

    Returns:
        returns a csv filename to pull from google storage bucket.
    """
    command = ['gsutil','ls','gs://rooftop-data/properties_data/']
    out = subprocess.check_output(command)
    csv_list = str(out).split('\\n')
    print('csv_list: {}'.format(csv_list))
    parsed_csv_list = [x[x.find('data_')+5:-4] for x in csv_list]
    print('parsed_csv_list:{}'.format(parsed_csv_list))
    date_csv_list = [x for x in parsed_csv_list if len(x)==8]
    print('date_csv_list: {}'.format(date_csv_list))
    dates = [dateparser.parse(x) for x in date_csv_list]
    print('dates: {}'.format(dates))
    now = datetime.datetime.now()
    newest = max(dt for dt in dates if dt < now)
    csv_filename = 'data_{}.csv'.format(newest.strftime('%Y%m%d'))
    return csv_filename

def fetch_from_google_storage(google_storage_bucket, path_to_file, filename, destination_folder):
    """Pulls file from google cloud storage bucket
    
    Keyword arguments:
        google_storage_bucket: [string] name of google storage bucket e.g. django-uploads
        path_to_file: [string] path to the folder of the file you want to pull from
        google storage
        filename: [string] name of the file you want to pull e.g. data_<YYYYMMDD>.csv
        destination_folder: [string] path to the folder you want to save the pulled file in
    
    Returns:
    returns success status if successful
    """
    pull_path = 'gs://{}/{}/{}'.format(google_storage_bucket, path_to_file, filename)
    print('pull path is {}'.format(pull_path))
    destination_path = os.getcwd() + '/{}/{}'.format(destination_folder, filename)
    print('destination path is {}'.format(destination_path))
    gsutil_command = ['gsutil', 'cp', pull_path,destination_path]
    try:
        subprocess.call(gsutil_command)
        print('pulled file {} successfully from the {} google storage bucket'.format(filename,google_storage_bucket))
    except Exception as e:
        print('pull failed. error message: {}'.format(e))


def scrapeRemax(city,state):
    csv_filename = find_latest_csvname()
    fetch_from_google_storage('rooftop-data','properties_data',csv_filename,
                              'csv_data')
    df_old = pd.read_csv('csv_data/'+csv_filename)
    d={}
    for pg in range(1,15):
        print('scraping page %s' % (str(pg)))
        page = createRemaxCityURL(city,state,pg)
        urls = findReMaxURLS(BeautifulSoup(get(page,verify=False).text,'html.parser'))
        for url in urls:
            try:
                print('napping for three seconds')
                time.sleep(1.5)
                home = pullHomeData(url)
                flat = flatten_dict(home)
                slug = flat['address_slug']
                d[slug] = flat
            except:
                pass
    df_new = pd.DataFrame.from_dict(d,orient='index')
    df_combined = pd.concat([df_old, df_new])
    df_combined.to_csv('data_20180129.csv',encoding='utf-8')

if __name__ == '__main__':
    if arg_check.city == 'check_string_for_empty':
        print('you didnt supply a city.  please try again.')
    if arg_check.state == 'check_string_for_empty':
        print('you didnt supply a state.  please try again')
    city=args['city']
    state=args['state']
    print('scraping home data for %s, %s :  time elapsed is...' % (city, state))

    scrapeRemax(city, state)

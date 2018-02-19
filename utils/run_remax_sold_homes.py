from scraping_utils import *
import pandas as pd 
from bs4 import BeautifulSoup
from scraping_utils import fetch_from_google_storage
from scraping_utils import find_latest_csvname
from scraping_utils import find_latest_soldpx_csvname
import time
import random
import urllib3
from remax_scrape import df_filename, implement_arg_parse, find_last_scrape_date, check_date_vs_last_scrape_date
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def check_slug_in_dataframe(slug,df):
    """This checks if a slug is in a dataframe

    Keyword arguments:
        slug: [string] this is the slug you want to check if is already in the dataframe
        df: [pandas dataframe] this is the dataframe you want to check against

    Returns:
        exists_in_df: [boolean] True is slug is already in dataframe, else False
    """
    exists_in_df = df['Unnamed: 0'].str.contains(slug).sum() >= 1
    return exists_in_df


def solddf_filename():
    """This returns csv filename for today

    Keyword arguments:
        None

    Returns:
        df_filename: [string] csv filename data_[todays_date].csv
    """
    now = datetime.now()
    datestr = now.strftime('%Y%m%d')
    df_filename = 'soldhomedata_{}.csv'.format(datestr)
    return df_filename

def scrape_sold_homes():
    """Scrapes remax sold homes

    Featured arguments:
        None

    Returns:
        A csv of all the new sold homes, appended to the old soldataframme

    """
    df_old = pd.read_csv('csv_data/'+csv_filename)
    keep_on_scraping = True
    pg = 0
    d = {}
    while keep_on_scraping:
        pg += 1
        home_number = len(d)
        pageurl = createSoldHomeURLNoFilter(pg)
        pagesoup = BeautifulSoup(get(pageurl,verify=False).text,'html.parser')
        urls = findReMaxURLS(pagesoup)
        for url in urls:
            rand_nap = random.uniform(0,2)
            print('sleeping for a random %f seconds'% (rand_nap))
            time.sleep(rand_nap)
            try:
                soldhome = pullSoldHomeData(url)
                slug = soldhome['Unnamed: 0']
                flat = flatten_dict(soldhome)
                slug = flat['address_slug']
                d[slug] = flat
                keep_on_scraping = check_slug_in_dataframe(slug,df_old)
            except Exception as e:
                print(e)
        df_new = pd.DataFrame.from_dict(d,orient='index')
        df_combined = pd.concat([df_old, df_new])
        new_df_filename = solddf_filename()
        df_combined.to_csv(new_df_filename,encoding='utf-8')

if __name__ == '__main__':
    arg_check, args = implement_arg_parse()
    if arg_check.city == 'check_string_for_empty':
        print('you didnt supply a city.  please try again.')
    if arg_check.state == 'check_string_for_empty':
        print('you didnt supply a state.  please try again')
    city=args['city']
    state=args['state']
    print('scraping home data for %s, %s :  time elapsed is...' % (city, state))
    csv_filename = find_latest_soldpx_csvname()
    fetch_from_google_storage('rooftop-data','sold_home_data',csv_filename,
                              'csv_data')
    scrape_sold_homes()
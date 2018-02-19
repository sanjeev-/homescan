from bs4 import BeautifulSoup
from requests import get
from datetime import datetime, timedelta
import pandas as pd
import time
from dateutil import parser
import json


def get_property_urls_from_eplp(eppraisal_url):
    """This pulls a list of urls from the eppraisal site
    
    """
    BASE_URL = 'https://www.eppraisal.com'
    eppraisal_soup = BeautifulSoup(get(eppraisal_url).text,'html.parser')
    property_urls = []
    for home in eppraisal_soup.find_all('a',class_='proplink'):
        home_url_addon = home['href']
        home_url = BASE_URL + home_url_addon
        property_urls.append(home_url)
    return property_urls

def get_property_soup(property_url):
    """returns a bs4 soup object from a url """
    soup = BeautifulSoup(get(property_url,verify=False).text,'html.parser')
    return soup

def find_sale_history_from_soup(soup):
    """Extracts the sale history from bs4 soup object
    
    Keyword arguments:
        soup: [bs4 soup object] soup obj of property to scrape
    
    Returns:
        sale_hist: [json] json object of dict of sale history
    
    """
    sales_hist_loop = soup.find_all('div',class_='panel-column panel-column-3')
    sales_hist_dict = {}
    for idx, item in enumerate(sales_hist_loop):
        if 'Last Sold' in item.find_all('li')[0].text:
            datestr = item.find_all('li')[0].text
            date = str(datestr[datestr.find('Last Sold: ')+len('Last Sold: '):])
            parsed_date = parser.parse(date).strftime('%Y%m%d')
            salestr = sales_hist_loop[idx+1].text
            sale = salestr[salestr.find('Sold Amt: $')+len('Sold Amt: $'):]
            sale = int(sale.replace(',',''))
            sales_hist_dict[parsed_date] = sale
    sales_hist_json = json.dumps(sales_hist_dict)
    return sales_hist_json
    
def get_address_from_soup(soup,city,state):
    """Pulls the address from the soup, checks with house canary API
    
    Keyword arguments:
        soup: [bs4 soup obj] soup object of property to scrape
        city: [string] city name of property e.g. Charlotte
        state: [string] state (2 name abbr) of property e.g. NC
    
    """
    addr = soup.find_all('h1',class_='hero-title')[0].text.replace('»','').strip()
    address_line_1 = addr[:addr.find(city)].strip()
    state = state
    city = city
    unit = ''
    zipcode = addr[addr.find(state)+len(state):].strip()
    scrape_address = {
        'address_line1': address_line_1,
        'city': city,
        'state': state,
        'zipcode': zipcode,
        'unit': unit, 
    }
    response = canonicalizeAddress(scrape_address)
    return response
    
def canonicalizeAddress(remax_address_dict):
    """
    this takes a dictionary of address data scraped from the remax website and calls the housecanary API
    to make sure that all of the data is standardized
    
    input
    
    remax_address_dict [dict] {
        address_line1: [string] steet number, street
        unit: [int] (optional) unit no
        state: [string] state, two letter abbreviation
        zipcode: [int] - five number zipcode
    }
    
    returns [dict] of street address info from the house canary API 
    
    """
    hc_key = '9SJCA9DISJVUAVAS4QQQ'
    hc_secret = '80vGOq9qYEy46a53XsUReFKpyvPK1owG' 
    if 'unit' in remax_address_dict:
        params = {
        
        'address': remax_address_dict['address_line1'],
        'state': remax_address_dict['state'],
        'zipcode': remax_address_dict['zipcode'],
        'city': remax_address_dict['city'],
        'unit':remax_address_dict['unit']
        }
    else:

        params = {
            
            'address': remax_address_dict['address_line1'],
            'state': remax_address_dict['state'],
            'zipcode': remax_address_dict['zipcode'],
            'city': remax_address_dict['city'],
        }
    geocode_url = 'https://api.housecanary.com/v2/property/geocode'
    response = get(geocode_url, params=params, auth=(hc_key, hc_secret))
    response = response.json()
    return response

def scrape_eppraisal_home_page(home_url,city,state):
    """Runs through a list of URLs, scraping home data into a dict
    
    Keyword arguments:
        home_url: [string] a url associated with a property
        city: [string] city of the property being scraped
        state: [string] state of the property being scraped
    
    Returns:
    """
    
    home = get_property_soup(home_url)
    
    h = {}
    response = get_address_from_soup(home,city,state)[0]
    address={}
    address['address_line1'] = str(response['address_info']['address'])
    address['city'] = str(response['address_info']['city'])
    address['zipcode'] = str(response['address_info']['zipcode'])
    address['state'] = str(response['address_info']['state'])
    address['unit'] = str(response['address_info']['unit'])
    address['lat'] = str(response['address_info']['lat'])
    address['lon'] = str(response['address_info']['lng'])
    address['slug'] = str(response['address_info']['slug'])
    h['address'] = address
    
    l = get_bed_bath_sqft_from_soup(home)
    
    sale_price_history = find_sale_history_from_soup(home)
    h['sold_price_history'] = sale_price_history
    
    h['listing_data'] = l
    
    tax = get_property_taxes_from_soup(home)
    h['prop_taxes'] = tax
    last_sold_date, last_sold_px = get_last_sold_from_history(sale_price_history)
    h['year_built'] = get_year_built_from_soup(home)
    h['last_sold_date'] = last_sold_date
    h['last_sold_price'] = last_sold_px
    return h

def get_bed_bath_sqft_from_soup(soup):
    """This pulls the number of beds, baths, and sq footage from prop
    
    Keyword arguments:
        soup: [bs4 soup object] soup obj of property
        
    Returns:
        listing_dict: dict with beds, baths, sq footage
    
    """
    loop = soup.find_all('div',class_='panel-column panel-column-1 propdesc')[0].find_all('li')
    listing_data = {}
    for line in loop:
        if 'Beds' in line.text:
            beds = int(line.text[line.text.find('Beds: ')+len('Beds: '):])
            listing_data['num_bedrooms'] = beds
        if 'Baths' in line.text:
            baths = int(line.text[line.text.find('Baths: ')+len('Baths: '):])
            listing_data['num_bathrooms'] = baths
        if 'Sqft' in line.text:
            sqft = int(line.text[line.text.find('Sqft: ')+len('Sqft: '):])
            listing_data['building_area_sq_ft'] = sqft
        if 'Lot Area (sq ft): ' in line.text:
            lot_area_sqft = line.text[line.text.find('Lot Area (sq ft): ')+len('Lot Area (sq ft): '):]
            listing_data['lot_area_sqft'] = lot_area_sqft
        if 'Acres: ' in line.text:
            lot_area_acres = float(line.text[line.text.find('Acres: ')+len('Acres: '):])
            listing_data['lot_area_acres'] = lot_area_acres
        if 'Fireplace: ' in line.text:
            fireplace = line.text[line.text.find('Fireplace: ')+len('Fireplace: '):]
            listing_data['fireplace' ] = fireplace
        if 'Heat Type: ' in line.text:
            heat_type = line.text[line.text.find('Heat Type: ')+len('Heat Type: '):]
            listing_data['heat_type' ] = heat_type
        if 'Roof Type: ' in line.text:
            roof_type = line.text[line.text.find('Roof Type: ')+len('Roof Type: '):]
            listing_data['roof_type' ] = roof_type
        if 'Garage/Park sqft: ' in line.text:
            garage_or_park_sqft = line.text[line.text.find('Garage/Park sqft: ')+len('Garage/Park sqft: '):]
            listing_data['garage_or_park_sqft' ] = garage_or_park_sqft
        if 'Basement Area: ' in line.text:
            basement_area = line.text[line.text.find('Basement Area: ')+len('Basement Area: '):]
            listing_data['basement_area' ] = basement_area
        if 'Air Cond: ' in line.text:
            air_conditioning = line.text[line.text.find('Air Cond: ')+len('Air Cond: '):]
            listing_data['air_conditioning' ] = air_conditioning
    return listing_data

def get_year_built_from_soup(soup):
    """Pulls the year the home was built from the bs4 soup obj
    """
    sents = soup.find_all('p',class_="main-page-description")[0].text.split('.')
    year_list = list(range(1900,datetime.now().year))
    year_list = [str(x) for x in year_list]
    for sent in sents:
        if 'Property records' in sent:
            tokens = sent.split(' ')
            for word in tokens:
                if word in year_list:
                    year_built = word
                    return year_built
    return None

def get_last_sold_from_history(sale_hist_json):
    """Reads the sale history json and returns the last sell date
    """
    d = json.loads(sale_hist_json)
    d2 = {parser.parse(k): v for k, v in d.items()}
    last_sold_date, last_sold_px = sorted(d2.items(),key=lambda x:x,reverse=True)[0]
    return last_sold_date.strftime('%Y-%m-%d'), last_sold_px

def get_property_taxes_from_soup(soup):
    """ Pulls last assessed property taxes and appraisal value from bs4
    """
    loops = soup.find_all('div',class_="panel-column panel-column-3")
    for loop in loops:
        if 'Property Taxes:' in loop.text:
            tax = loop.text
            tax_strip = tax[tax.find('Property Taxes: $')+len('Property Taxes: $'):]
            return float(tax_strip.replace(',',''))
            
def get_eppraisal_url_page(pg):
    URL = 'https://www.eppraisal.com/recently-sold/nc/charlotte/?pg={}'.format(pg)
    return URL

def flatten_dict(dd, separator='_', prefix=''):
    return { prefix + separator + k if prefix else k : v
             for kk, vv in dd.items()
             for k, v in flatten_dict(vv, separator, kk).items()
             } if isinstance(dd, dict) else { prefix : dd }

def scrape_eppraisal(max_pages=1000,city='Charlotte',state='NC'):
    """Automatically scrapes thru eppraisals website, collecting recent home info
    """
    d={}
    for pg in range(1,max_pages):
        current_eppraisal_url = get_eppraisal_url_page(pg)
        list_of_home_urls = get_property_urls_from_eplp(current_eppraisal_url)
        for url in list_of_home_urls:
            try:
                print('napping for a bit')
                time.sleep(1)
                home = scrape_eppraisal_home_page(url,city,state)
                flat = flatten_dict(home)
                slug = flat['address_slug']
                d[slug] = flat
            except Exception as e:
                print('ERR: {}'.format(e))
        df_new = pd.DataFrame.from_dict(d,orient='index')
        df_new.to_csv('sold_homes_eppraisal.csv',encoding='utf-8',index=False)

if __name__=='__main__':
    scrape_eppraisal()
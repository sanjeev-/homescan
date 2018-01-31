# COMMAND LINE PROMPT:
# sudo gsutil -m cp -R dir gs://my_bucket
import sys
import os
from bs4 import BeautifulSoup
from requests import get
import requests
from datetime import datetime, timedelta
import time
import argparse
import pandas as pd
import urllib
from image_utils import *

csv_path = '/home/sanjeev87/remax_scrape/data/data_20180123.csv'

df = pd.read_csv(csv_path)

imgdf = df[(df['listing_data_num_bathrooms']>=2) & (df['listing_data_num_bedrooms']>=3) & (df['listing_data_home_type']=='Single Family')& (df['listing_data_list_price']>=150000)& (df['listing_data_list_price']<=500000)& (df['features_year_built']>=1990)]

iterateFilteredDFAndDownloadImages(imgdf,'img')





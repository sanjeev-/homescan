
import os
from bs4 import BeautifulSoup
from requests import get
import requests
from datetime import datetime, timedelta
import time
import argparse
import pandas as pd
import urllib


parser = argparse.ArgumentParser(description='Process some arguments')

parser.add_argument('--csv_path',metavar='C',type=str,help='city that you want to scrape e.g. "charlotte" ')
parser.add_argument('--method',metavar='S',type=str,help='two letter abbrv of the state of the city you want to scrape e.g. "NC"')


def imgStringToList(imgstring):
    return imgstring.split(';')
    

def downloadImages(imglist,name_base,img_folder):
    print('image folder is:%s') % (img_folder)
    if not os.path.exists(img_folder):
        os.makedirs(img_folder)
    base_img_name = name_base
    for idx,imgurl in enumerate(imglist):
        img_type = imgurl[imgurl.rfind('.'):]
        local_filename = base_img_name+str(idx+1)+img_type
        filepath = img_folder + local_filename
        print('downloading {}...').format(local_filename)
        urllib.urlretrieve(imgurl,filepath)
        print('download successful. {}/{} files downloaded. sleeping for 3 secs then dling next').format(idx+1,len(imglist))
        time.sleep(3)
        
def iterateFilteredDFAndDownloadImages(df,folder_path):
    """
    this takes a dataframe that is filtered by createFilterMask or manually,
    it then iterates through every house in the dataframe and downloads the image gallery
    and the header image 
    
    
    """
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    for homeidx in range(len(df)):
        home = df.iloc[homeidx]
        imgstr = home['images_img_gallery']
        imglist = imgStringToList(imgstr)
        folder_name = '/'+home['Unnamed: 0'] + '/'
        folder_name = folder_path + folder_name
        print('DOWNLOADING IMAGES FOR HOME: {}'.format(folder_name))
        downloadImages(imglist,'img','/home/sanjeev87/remax_scrape/images/'+folder_name)      


def createFilterMask(**kwargs):
    """
    input is optional filters defined below.
    
    note all min and max are INCLUSIVE e.g. (min_bath = 2) means 2 or more bathrooms.
    
    min_bath = min bathrooms 
    max_bath = max bathrooms 
    
    min_bed = min bedrooms
    max_bed = max bedrooms
    
    min_px = min listing px
    max_px = max listing px
    
    no_septic = bool. only non-septics
    no_well = bool.  only non-wells
    
    is_subdivision = bool. in a valid subdivision
    has_garage = bool.  has a garage
    
    min_school_score = minimum school score
    
    min_yearbuilt = oldest year built you are willing to consider
    
    home_type = list of hometypes you are willing to consider.  options are single, condo/town, multi, lot
    
    output is a mask used for filtering the image dataframe

    listing_status
    
    """
    return True

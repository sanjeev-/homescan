import os
import sys


# NOTE: run using python csvToDjangoModel.py --csv_path= [ path to csv ] 
# NOTE: filtering csv under '__main__.py' using the normal buy box. 


# Need to change proj_path and DJANGO_SETTINGS_MODULE

proj_path = "C:/Users/Sanjeev/Desktop/ribbon/propertyscraper/src/"
# This is so Django knows where to find stuff.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "property_scraper.settings")
sys.path.append(proj_path)

# This is so my local_settings.py gets loaded.
os.chdir(proj_path)

# This is so models get loaded.
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from remax.models import *
import pandas as pd

parser = argparse.ArgumentParser(description='Process some arguments')

parser.add_argument('--csv_path',metavar='C',type=str,help='path to csv with data')


args = vars(parser.parse_args())



def dfToPropertyModel(df):
    for idx in range(len(df)):
        
        myProperty = Property(

            #Address
            street_address_1 = df.iloc[idx]['address_address_line1'],
            street_address_2 = df.iloc[idx]['address_unit'],
            city = df.iloc[idx]['address_city'],
            state = df.iloc[idx]['address_state'],
            zip_code = df.iloc[idx]['address_zipcode'],
            latitude = df.iloc[idx]['address_lat'],
            longitude = df.iloc[idx]['address_lon'],
            
            
            
            #Address keys
            hc_slug=df.iloc[idx]['Unnamed: 0'],
            lowercase_slug = df.iloc[idx]['Unnamed: 0'].lower(),
            
            #Listing data
            list_price = df.iloc[idx]['listing_data_list_price'],
            num_bedrooms = df.iloc[idx]['listing_data_num_bedrooms'],
            num_bathrooms = df.iloc[idx]['listing_data_num_bathrooms'],
            building_area_sq_ft = df.iloc[idx]['listing_data_building_area_sq_ft'],
            home_type = df.iloc[idx]['listing_data_home_type'],
            
            
            #Features
            num_floors = df.iloc[idx]['features_floors'],
            year_built = df.iloc[idx]['features_year_built'],
            listing_status = df.iloc[idx]['features_listing_status'],
            interior_features = df.iloc[idx]['features_interior_features'],
            flooring = df.iloc[idx]['features_flooring'],
            is_foreclosure = df.iloc[idx]['features_is_foreclosure'],
            school_score = df.iloc[idx]['features_school_score'],
            url = df.iloc[idx]['features_remax_url'],
            num_half_bath = df.iloc[idx]['features_num_half_bath'],
            has_septic = df.iloc[idx]['features_has_septic'],
            has_pool = df.iloc[idx]['features_has_pool'],
            days_on_site = df.iloc[idx]['features_days_on_site'],
            start_date_on_site = df.iloc[idx]['features_start_date_on_site'],
            subdivision = df.iloc[idx]['features_subdivision'],
            has_established_subdivision = df.iloc[idx]['features_has_established_subdivision'],
            has_well = df.iloc[idx]['features_has_well'],
            has_garage = df.iloc[idx]['features_has_garage'],
            no_pool_well_septic = df.iloc[idx]['features_no_pool_well_septic'],
            garage_detail = df.iloc[idx]['features_garage_detail'],
            num_full_bath = df.iloc[idx]['features_num_full_bath'],
            MLS = df.iloc[idx]['features_MLS'],
            description = df.iloc[idx]['features_desc'],

            #Images
            img_path_header = '/img/'+df.iloc[idx]['Unnamed: 0']+'/img0.jpg',
            img_paths_gallery = ';'.join(['/img/'+df.iloc[idx]['Unnamed: 0']+'/img'+str(x)+'.jpg' for x,y in enumerate(df.iloc[idx]['images_img_gallery'].split(';'))])
            

        )
        print(myProperty)
        
        try:
            myProperty.save()
            print('{} has successfully been saved to the database! :)'.format(myProperty))
        except:
            print("saving {} has failed.  something is wrong!").format(myProperty)
    return myProperty


if __name__ == '__main__':
	csv_path = args['csv_path']
	df = pd.read_csv(csv_path)
	df = df.where((pd.notnull(df)), None)
	imgdf = df[(df['listing_data_num_bathrooms']>=2) & (df['listing_data_num_bedrooms']>=3) & (df['listing_data_home_type']=='Single Family')& (df['listing_data_list_price']>=150000)& (df['listing_data_list_price']<=500000)& (df['features_year_built']>=1990)]
	dfToPropertyModel(imgdf)	

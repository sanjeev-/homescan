from scraping_utils import *
import pandas as pd 
from bs4 import BeautifulSoup
import time
import random


# defining argparse



def scrapeSoldHomes(new_csv_interval=10):
	"""
	new csv interval defines after how many homes we save a new csv datasheet

	"""

	d = {}


	for pg in xrange(160,2000):

		home_number = len(d)
                fails = 0
                tried = 0
		pageurl = createSoldHomeURL(pg)
		pagesoup = BeautifulSoup(get(pageurl).text,'html.parser')
		urls = findReMaxURLS(pagesoup)
		for url in urls:
			rand_nap = random.uniform(0,5)
			print('sleeping for a random %f seconds') % (rand_nap)
			time.sleep(rand_nap)
                        tried +=1
                        try:
			    soldhome = pullSoldHomeData(url)
			    flat = flatten_dict(soldhome)
			    slug = flat['address_slug']
			    d[slug] = flat
                        except:
                             fails +=1
                             print('adding home failed!  failure num_fails is {}, fail_rate is: {}'.format(str(fails),float(fails/tried)))
                        print('failure_rate:{}'.format(float(fails)/float(tried)))
		if pg % 20  == 0:
			csv_output_name = 'sold_home_page_{}.csv'.format(str(pg))
			df = pd.DataFrame.from_dict(d,orient='index')
			df.to_csv(csv_output_name,encoding=('utf-8'))


if __name__ == '__main__':
	scrapeSoldHomes()

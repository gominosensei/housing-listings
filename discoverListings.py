#import re
import logging
import time
import random
#from datetime import datetime
import urllib.request, urllib.error

#from django.utils import timezone
from bs4 import BeautifulSoup  # docs at http://www.crummy.com/software/BeautifulSoup/bs4/doc/

from listings.models import Listing, BadListing, FreshListing  
		
def recordExists(listingID, database):
	try:
		listing = database.objects.get(pk=listingID)
		return True
	except database.DoesNotExist:
		return False
		
		
def discoverListing(row, urlbase):
	link = row.find('a')
	url = urlbase + link['href']
	listingID = int(url.split('/')[4].split('.')[0])
	logging.info('listingID: %s', listingID)

	if recordExists(listingID, BadListing):
		logging.info('  ...already discarded')
		return False
		
	if recordExists(listingID, Listing):
		logging.info('  ...already scraped')
		return False
		
	try:
		freshListing = ""
		freshListing = FreshListing.objects.get(pk=listingID)	
		freshListing.save(force_update=True)		
		logging.info('  ...already queued')
		return False
	except:
		freshListing = FreshListing(listingID=listingID)
		freshListing.url = url
		freshListing.save()
		logging.info('  ...queued up')
		
	return True


def discoverPage(listUrl, urlbase, deep):
	logging.info('Scraping listing page %s', listUrl)

	# Get the list of craigslist posts
	try:
		page = urllib.request.urlopen(listUrl)
	except urllib.error.HTTPError as e:
		if e.code == 403:
			logging.warning('403 Forbidden: %s', listUrl)
			time.sleep(66)   
			page = urllib.request.urlopen(listUrl)  # try again; this time, the error will be fatal
		else:
			raise
	hangtime = random.randrange(3,7)
	time.sleep(hangtime)
			
	soup = BeautifulSoup(page)

	# Loop over listings and add each one to the DB
	for row in soup.find_all('p','row'):
		if not discoverListing(row, urlbase):
			if not deep:
				return False
	
	return True
			
		

def discoverCategory(extension, pages, urlbase, deep):
	categoryUrl = urlbase + '/' + extension + '/'
	for pagesback in range(0, pages):
		if pagesback > 0:
			index = 'index' + str(pagesback) + '00.html'
		else:
			index = ''
		listUrl = categoryUrl + index
	
		if not discoverPage(listUrl, urlbase, deep):
			if not deep:
				logging.info('Done with %s after %s pages' % (extension, pagesback))
				return

def startLog(debugMode):
	logfile = 'debug.log'
	if debugMode:
		loglevel = logging.DEBUG
	else:
		loglevel = logging.INFO
	# Setup
	logging.basicConfig(filename=logfile,level=loglevel, filemode='w')

	logging.info('===================================')
	logging.info('Discovering new listings', str(time.ctime()))
	
def discover(debugMode=False, pagesPerCategory = 5, deep = False):
	# Constants
	urlbase = 'http://madison.craigslist.org'
	extension = ['apa', 'roo', 'sub']
	maximumPages = [20, 5, 3]

	start = time.time()
	startLog(debugMode)
	random.seed
	
	# Loop over categories: normal, rooms, sublets
	for category in range(0,3):
		pages = maximumPages[category]
		if pages > pagesPerCategory:
				pages = pagesPerCategory
		
		discoverCategory(extension[category], pages, urlbase, deep)
		
	end = time.time()
	results = 'Discovered %s pages of listing IDs per category in %s seconds' % (pagesPerCategory, end-start)
	logging.info(results)
	return results

import re
import logging
import time
import random
from datetime import datetime
import urllib.request, urllib.error

from django.utils import timezone
from bs4 import BeautifulSoup  # docs at http://www.crummy.com/software/BeautifulSoup/bs4/doc/
from pygeocoder import Geocoder # docs at https://bitbucket.org/xster/pygeocoder/wiki/Home
# Google geocoding API docs at https://developers.google.com/maps/documentation/geocoding/?csw=1#GeocodingRequests

from listings.models import Listing, BadListing  

def formatPhoneNumber(phone):
	try:
		phone = '-'.join(phone.groups())
	except AttributeError:
		logging.debug('Error formatting phone number: %s', phone)
		pass
	return (phone)

def findPhone(text, strict = False):
    # RegEx Patterns
	phonePattern = re.compile(r'''
		(\d{3})     # area code is 3 digits (e.g. '800')
		\D{0,2}     # optional 1 or 2 character separator
		(\d{3})     # prefix is 3 digits (e.g. '555')
		\D?         # optional 1 character separator
		(\d{4})     # rest of number is 4 digits (e.g. '1212')
		''', re.VERBOSE)

	phonePatternNoAreaCode = re.compile(r'''
		(\d{3})     # prefix is 3 digits (e.g. '555')
		-           # require literal dash to avoid false positives
		(\d{4})     # rest of number is 4 digits (e.g. '1212')
		''', re.VERBOSE)

	phonePatternStrict = re.compile(r'''
		(\d{3})     # area code is 3 digits (e.g. '800')
		-     		# literal dash
		(\d{3})     # prefix is 3 digits (e.g. '555')
		-           # literal dash
		(\d{4})     # rest of number is 4 digits (e.g. '1212')
		''', re.VERBOSE)

	# First look for a number with area code separated by dashes
	try:
		phone = phonePatternStrict.search(text)
	except AttributeError:
		pass

	if (phone):
		return(formatPhoneNumber(phone))

	# If matching is strict, give up if that didn't work. 
	if (strict):
		return('')

	# Otherwise search for any number with an area code with looser rules on the dividers
	try:
		phone = phonePattern.search(text)
	except AttributeError:
		try:
			phone = phonePatternNoAreaCode.search(text)
		except AttributeError:
			phone = ''

	return(formatPhoneNumber(phone))

def regionByZip(listing):
	if listing.city != 'Madison':
		return listing.city
		
	zip = listing.zip

	if zip == '53703':
		return 'Central'
	if zip == '53704':
		return 'East or North'
	if zip == '53705':
		return 'West'
	if zip == '53706':
		return 'West'
		
	if zip == '53711':
		return 'South or West'
	if zip == '53713':
		return 'South'
	if zip == '53714':
		return 'East'
	if zip == '53716':
		return 'East'
	if zip == '53717':
		return 'West'
	if zip == '53718':
		return 'East or North'
	if zip == '53719':
		return 'South or West'

	if zip == 53726:
		return 'West'
	if zip == 53728:
		return 'West'

	if zip == 53732:
		return 'North'
	if zip == 53758:
		return 'East'
	if zip == 53762:
		return 'West'
	if zip == 53790:
		return 'North'
	if zip == 53728:
		return 'West'
	
	return ''

def scrapeListing(url, soup=None):
	logging.debug('Scraping %s', url)
	
	extension = url.split('/')[3]
	listingID = int(url.split('/')[4].split('.')[0])

	logging.info('Scraping listing %s', listingID)
	
	newListing = Listing(listingID=listingID)
	logging.debug('newListing %s', newListing)
	
	# Retrieve page and extract contents 
	try:
		if not soup:
			page = urllib.request.urlopen(url)
			soup = BeautifulSoup(page)    
		postingtitle = soup.find('h2','postingtitle').get_text()
		postingbody = soup.find('section',id='postingbody').get_text()
	except AttributeError:
		logging.error('Failed to parse listing %s', url)
		self = None
		return

	newListing.listingBody = postingbody
	newListing.title = postingtitle

	# Price 
	try:
		price = postingtitle.split()[0]
		price = price.split('$')[1]
		newListing.price = int(price)
	except IndexError:
		logging.warning('Non-$ price %s,', newListing.price)
		#newListing.price='' 

	# Type of listing
	newListing.listingType = extension
	if newListing.listingType == 'roo':
		newListing.shared = True;
	elif newListing.listingType == 'sub':
		newListing.sublet = True;
	

	# Address 
	try:
		address = soup.find('div','mapaddress').get_text()
		newListing.address = address.replace(',', ' ')
	except AttributeError:
		pass

	# Contact phone number
	try:
		replylink = url.replace(extension, 'reply').replace('.html','')
		replypage = str(urllib.request.urlopen(replylink).read())
		newListing.phone = findPhone(replypage, True)
	except:
		logging.debug('No phone from reply page')
		try:
			newListing.phone = findPhone(postingbody)
		except AttributeError:
			pass

	if not newListing.phone:
		try:
			contactlink = url.replace(extension,'fb/mad/'+extension).replace('.html','')
			logging.debug('contactlink: ' + contactlink)
			contactpage = str(urllib.request.urlopen(contactlink).read())
			logging.debug('contactpage: ' + contactpage)
			newListing.phone = findPhone(contactpage, False)
			logging.debug('phone: ' + newListing.phone)
		except:
			logging.debug('No phone from contact page')
			newListing.phone = ''
			
	# Posting date
	postinginfos = soup.find('div','postinginfos')
	logging.debug('postinginfos: %s', postinginfos)
	for p in postinginfos.find_all('p','postinginfo'):
		postinginfo = p.get_text()
		if 'posted' in postinginfo:
			newListing.dateListingPosted = p.find('time')['datetime']
		elif 'updated' in postinginfo:
			newListing.dateListingUpdated = p.find('time')['datetime']
	if not newListing.dateListingUpdated:
		newListing.dateListingUpdated = newListing.dateListingPosted
			
	# Go through block of discrete attributes        
	attrgroup = soup.find('p','attrgroup')
	for span in attrgroup.find_all('span'):
		attribute = span.get_text()    
		if 'ft2' in attribute: 
			newListing.area = int(attribute.split('ft2')[0])
		elif 'laundry' in attribute or 'w/d' in attribute:
			newListing.laundry = attribute
		elif 'parking' in attribute or 'garage' in attribute or 'carport' in attribute:
			newListing.parking = attribute
		elif 'purrr' in attribute:
			newListing.catsAllowed = True
		elif 'wooof' in attribute:
			newListing.dogsAllowed = True
		elif 'no smoking' in attribute:
			newListing.noSmoking = True
		elif 'BR' in attribute:
			newListing.bedrooms = int(attribute.split('BR')[0])
		else:
			logging.debug('Mystery attribute: %s', attribute)
	logging.debug('attrgroup: ' + str(attrgroup))
	newListing.attributeGroup = str(attrgroup)

	# URLs
	newListing.listingUrl = url
	try:
		mapaddress = soup.find('p','mapaddress')
		newListing.mapUrl = mapaddress.find('a')['href']
	except AttributeError:
		pass
	
	# Geocode based on the Maps URL
	try:
		mapQueryString = newListing.mapUrl.split('?q=')[1]
		geocode = Geocoder.geocode(mapQueryString)
		newListing.city = geocode.locality
		county = geocode.administrative_area_level_2
		newListing.county = county.split(' ')[0]
		newListing.neighborhood = geocode.neighborhood
		newListing.zip = geocode.postal_code
	except:
		logging.debug('Geocoding error')
		pass
	
	# Region
	newListing.region = regionByZip(newListing)
		
	newListing.dateListingScraped = timezone.now()
		
	logging.debug('newListing (at the end) %s', newListing)
	return newListing

def updateListing(url, listingID, oldListing):
	logging.info('Listing %s exists', listingID)

	if oldListing.updatedBy:
		logging.info('Listing was edited; not updating')
		return
	
	
	scrapeTimeDelta = timezone.now() - oldListing.dateListingScraped
	logging.info('  Time since scrape: %s', scrapeTimeDelta)
	if scrapeTimeDelta.seconds < 21600:		# Don't rescrape within six hours
		logging.info('  Too soon - not rescraping')
		return
	
	logging.debug('oldListing: %s', oldListing)

	page = urllib.request.urlopen(url)
	soup = BeautifulSoup(page)    
	postinginfos = soup.find('div','postinginfos')
	logging.debug('postinginfos: %s', postinginfos)
	dateListingUpdated=''
	for p in postinginfos.find_all('p','postinginfo'):
		postinginfo = p.get_text()
		if 'updated' in postinginfo:
			dateListingUpdated = p.find('time')['datetime']
			
	if not dateListingUpdated:
		logging.info("Listing hasn't been updated")
		return

	dateListingUpdated = datetime.strptime(dateListingUpdated, '%Y-%m-%dT%H:%M:%S%z')
	logging.debug('New date updated: %s', dateListingUpdated)
	logging.debug('Old date updated: %s', oldListing.dateListingUpdated)
	timeDelta = dateListingUpdated - oldListing.dateListingUpdated
	logging.debug('timeDelta: %s', timeDelta)
	

		
	if dateListingUpdated == oldListing.dateListingUpdated:
		logging.info('Listing %s is up to date', listingID)
		return
	
	logging.info('  Updating listing %s', listingID)
	return scrapeListing(url, soup)
	
def validListing(listing, logInvalid):	
	url = 'http://madison.craigslist.org/%s/%s.html' % (listing.listingType, listing.listingID)

	if listing.county != '' and listing.county != 'Dane':
		if logInvalid:
			logging.debug('%s is in another county' % url)
		return False
		
	if not listing.price and not '$' in listing.listingBody:
		if logInvalid:
			logging.debug('%s has no price' % url)
		return False
		
	if not listing.address:
		if 'paste the link' in listing.listingBody or 'Check out our website' in listing.listingBody:
			if logInvalid:
				logging.debug('%s looks like spam' % url)
			return False
		# check for a number in the listing
		hasDigits = re.search('\d', listing.listingBody)
		if hasDigits:
			logging.debug('%s has no address but has numbers in listing' % url)
		else:
			logging.debug('%s has no address an no numbers in listing' % url)

	excluded = ('LITTLE PINE MOBILE HOME PARK', 'Americas Best Value Inn')
	for excludedString in excluded:
		if excludedString in listing.listingBody:
			if logInvalid:
				logging.debug('%s contains string "%s"' % (url, excludedString))
			return False

		
	return True

def fillInDefaults(listing):
	if not listing.neighborhood:
		listing.neighborhood = ''
	if not listing.city:
		listing.city = ''
	if not listing.zip:
		listing.zip = ''
	if not listing.region:
		listing.region = ''

	logging.debug('cleaned up: %s', listing)
	
	return listing
		
def scrapeOrUpdateListing(row, urlbase, rowNumber):
	link = row.find('a')
	logging.debug('link: %s', link)
	url = urlbase + link['href']
	listingID = int(url.split('/')[4].split('.')[0])
	logging.debug('listingID: %s', listingID)

	# Check if we already scraped this and decided it was bad
	try:
		badListing = ""
		badListing = BadListing.objects.get(pk=listingID)
	except:
		pass
		
	if badListing:
		logging.info('Listing %s was already scraped and discarded', listingID)
		return 0

	# See if there's an existing record for it
	try:
		oldListing = ""
		oldListing = Listing.objects.get(pk=listingID)
	except:
		pass

	if oldListing:
		newListing = updateListing(url, listingID, oldListing)
	else:
		newListing = scrapeListing(url)
		
	hangtime = random.randrange(1,6)
	time.sleep(hangtime)
		
	if not newListing:
		return
	
	if validListing(newListing, True):
		newListing = fillInDefaults(newListing)
		newListing.save()
	else:
		badListing = BadListing(listingID=listingID)
		badListing.save()

def scrapePage(listUrl, urlbase, rowNumber, maximumRows):
	logging.info('Scraping lising page %s', listUrl)

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
	hangtime = random.randrange(1,6)
	time.sleep(hangtime)
			
	soup = BeautifulSoup(page)

	# Loop over listings and add each one to the sheet
	rowsOnThisPage = 1
	for row in soup.find_all('p','row'):
		if rowNumber > maximumRows:
			break
		rowNumber += 1
		scrapeOrUpdateListing(row, urlbase, rowNumber)

		rowsOnThisPage += 1
		if rowsOnThisPage > 101:   # for testing
			break

	return rowNumber    

def scrapeCategory(categoryUrl, pages, urlbase, rowNumber, maximumRows):
	for pagesback in range(0, pages):
		if pagesback > 0:
			index = 'index' + str(pagesback) + '00.html'
		else:
			index = ''
		listUrl = categoryUrl + index
	
		rowNumber = scrapePage(listUrl, urlbase, rowNumber, maximumRows)
		if rowNumber > maximumRows:
			break

	return rowNumber       

def startLog(debugMode):
	logfile = 'debug.log'
	if debugMode:
		loglevel = logging.DEBUG
	else:
		loglevel = logging.INFO
	# Setup
	logging.basicConfig(filename=logfile,level=loglevel, filemode='w')

	logging.info('===================================')
	logging.info('HVL started %s', str(time.ctime()))
	
def scraper(debugMode, maximumRows = 3):
	# Constants
	urlbase = 'http://madison.craigslist.org'
	extension = ['apa', 'roo', 'sub']
	maximumPages = [20, 5, 3]

	start = time.time()
	startLog(debugMode)
	rowNumber = 1
	random.seed
	
	# Loop over categories: normal, rooms, sublets
	for category in range(0,3):
		categoryUrl = urlbase + '/' + extension[category] + '/'
		pages = maximumPages[category]
		
		rowNumber = scrapeCategory(categoryUrl, pages, urlbase, rowNumber, maximumRows)

		if rowNumber > maximumRows:
			logging.warning('Stopped after %s rows', maximumRows)
			break

	end = time.time()
	results = 'HVL done - %s rows in %s seconds' % (rowNumber-1, end-start)
	logging.info(results)
	return results

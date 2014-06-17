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

from listings.models import Listing, BadListing, FreshListing

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
			
			
def realisticPause(result = 0, min = 0, max = 300):
	print('realisticPause ', result)
	d6 = random.randrange(1,7)
	print('d6: ', d6)
	result = result + d6
	print('result: ',result)
	
	if d6 == 6:
		result = 2 * realisticPause(result)
	elif d6 > 3:
		result = realisticPause(result)

	if result > max:
		return max
	
	if result < min:
		return min
		
	return result

def retrieveListing(freshListing):
	logging.info('Retrieving listing %s', freshListing.listingID)
	
	newListing = scrapeListing(freshListing.url)
	hangtime = realisticPause(0, 2, 31)
	time.sleep(hangtime)
		
	if newListing:
		if validListing(newListing, True):
			newListing = fillInDefaults(newListing)
			newListing.save()
			logging.info('  ...success')
		else:
			badListing = BadListing(listingID=freshListing.listingID)
			badListing.save()
			logging.info('  ...retrieved but not valid')
		freshListing.delete()
	else:
		logging.warning('  Error retrieving listing %s (at %s)', (freshListing.listingID, freshListing.url))
	
		
	

def startLog(debugMode):
	logfile = 'debug.log'
	if debugMode:
		loglevel = logging.DEBUG
	else:
		loglevel = logging.INFO
	# Setup
	logging.basicConfig(filename=logfile,level=loglevel, filemode='w')

	logging.info('===================================')
	logging.info('Retrieving new listings - %s', str(time.ctime()))
	
def retrieve(debugMode=False, maximumListings = 3):
	start = time.time()
	startLog(debugMode)
	random.seed

	#return 'bar'
	querySet = FreshListing.objects.all()[:maximumListings]
	listingCount = querySet.count()
	
	IDs=''
	for freshListing in querySet:
		retrieveListing(freshListing)

	end = time.time()
	results = 'HVL done - %s listings in %s seconds' % (listingCount, end-start)
	logging.info(results)
	return results

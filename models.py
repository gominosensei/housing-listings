from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils import timezone

class BadListing(models.Model):
	listingID = models.BigIntegerField(primary_key=True, unique=True, editable=False)

class FreshListing(models.Model):
	listingID = models.BigIntegerField(primary_key=True, unique=True, editable=False)
	url = models.CharField(max_length=254, blank=True, default='')
	trouble = models.BooleanField(default=False)
	dateRecordUpdated = models.DateTimeField(auto_now=True)
	claimed = models.DateTimeField(blank=True, null=True)
	
class Listing(models.Model):
	# Core data about listing
	listingID = models.BigIntegerField(primary_key=True, unique=True, editable=False)
	listingBody = models.TextField()	
	listingType = models.CharField(max_length = 3)
	
	# Data scraped from listing
	title = models.CharField(max_length = 255, blank=True, default='')
	attributeGroup = models.TextField(default='')
	price = models.IntegerField(null=True, blank=True)
	bedrooms = models.SmallIntegerField(null=True)
	address = models.CharField(max_length=254, blank=True, default='')
	phone = models.CharField(max_length = 30, blank=True, default='')
	area = models.SmallIntegerField(null=True, blank=True)
	mapUrl = models.URLField(blank=True, default='')
	dateListingPosted = models.DateTimeField()
	dateListingUpdated = models.DateTimeField(null=True, blank=True)
	
	# Computed or added later
	neighborhood = models.CharField(max_length = 100, blank=True, default='')
	city = models.CharField(max_length = 100, blank=True, default='')
	county = models.CharField(max_length = 30, blank=True, default='')
	zip = models.CharField(max_length = 10, blank=True, default='')
	region = models.CharField(max_length = 100, blank=True, default='')
	available = models.CharField(max_length = 100, blank=True, default='')
	sublet = models.BooleanField(default=False)
	shared = models.BooleanField(default=False)

	# Utilities
	gas = models.BooleanField(default=False)
	heat = models.BooleanField(default=False)
	electricity = models.BooleanField(default=False)
	internet = models.BooleanField(default=False)
	cable = models.BooleanField(default=False)
	lawn_care = models.BooleanField(default=False)
	snow_removal = models.BooleanField(default=False)
	trash = models.BooleanField(default=False)
	water = models.BooleanField(default=False)

	# Amenities
	laundry = models.CharField(max_length = 99, blank=True, default='')
	parking = models.CharField(max_length = 99, blank=True, default='')    
	#parkingPrice = models.CharField(max_length = 99, null=True, blank=True, default='')    
	dogsAllowed = models.NullBooleanField()
	catsAllowed = models.NullBooleanField()
	#petPrice = models.CharField(max_length = 99, null=True, blank=True, default='')    
	noSmoking = models.NullBooleanField()
		
	# Metadata about this record
	deleted = models.BooleanField(default=False)
	dateListingScraped = models.DateTimeField()
	dateRecordUpdated = models.DateTimeField(auto_now=True)
	updatedBy = models.ForeignKey(User, null=True)
		
	class Meta:
		ordering = ["-listingID"]
	
	def get_absolute_url(self):
		return reverse('listing_update', kwargs={'pk': self.pk})
		
	# Combined output of several attributes for the description column
	def descriptionField(self):			
		# Make amenities from parking, laundry, pets, and smoking 
		amenities = []
		if self.parking:
			amenities.append(self.parking)
		if self.laundry:
			amenities.append(self.laundry)
		if self.dogsAllowed and self.catsAllowed:
			amenities.append('cats & dogs allowed')
		elif self.dogsAllowed: 
			amenities.append('dogs allowed')
		elif self.catsAllowed:
			amenities.append('cats allowed')
		if self.noSmoking:
			amenities.append('no smoking')

		utilities = []
		if self.electricity:
			utilities.append('electricity')
		if self.heat:
			utilities.append('heat')
		if self.water:
			utilities.append('water')
			
		description = 'Utilities included: '
		if self.electricity == None and self.heat == None and self.water == None:
			description = description + 'unknown'
		elif len(utilities)==0:
			description = description + 'none'
		else:
			description = description + ', '.join(utilities)
			
		if len(amenities)>0:
			description = description + "; Amenities include: " + '; '.join(amenities)
			#description = description.replace(',', ' ')
			
		return description
			
	# Combined output for the bedrooms column with the # of rooms plus the type of rental
	def bedroomsField(self):
		if self.shared:
			return 'Shared(0)'
		if self.sublet:
			return 'Sublet(' + str(self.bedrooms) + ')'
		return self.bedrooms

	def addressWithNeighborhood(self):
		if self.neighborhood == '':
			return self.address
		if self.address == '':
			return self.neighborhood
		return '%s (%s)' % (self.address, self.neighborhood)
		
	def url(self):
		baseUrl = 'madison.craigslist.org'
		return 'http://%s/%s/%s.html' % (baseUrl, self.listingType, self.listingID)
		
	def mapQueryString(self):
		q=''
		try:
			q = self.mapUrl.split('?q=')[1]
		except:
			pass
		return q

	def representation(self):
		return ('Listing(\n     id=%s\n     deleted=%s\n     price=%s\n     listingType=%s\n     address=%s\n     phone=%s\n     bedrooms=%s\n     laundry=%s\n     parking=%s\n     dogsAllowed=%s\n     catsAllowed=%s\n     noSmoking=%s\n     area=%s\n     zip=%s\n     county=%s\n     neighborhood=%s\n     mapUrl=%s\n     )' % (repr(self.listingID), repr(self.deleted), repr(self.price), repr(self.listingType), repr(self.address), repr(self.phone), repr(self.bedrooms), repr(self.laundry), repr(self.parking), repr(self.dogsAllowed), repr(self.catsAllowed), repr(self.noSmoking), repr(self.area), repr(self.zip), repr(self.county), repr(self.neighborhood), repr(self.mapUrl)))
		
	def __str__(self):
		return(self.representation())
		
	def __repr__(self):
		return(self.representation())

from django.contrib import admin
from listings.models import Listing, BadListing

class ListingAdmin(admin.ModelAdmin):
    list_display = ('listingID', 'phone', 'bedrooms', 'price', 'address', 'region', 'dateListingScraped','dateRecordUpdated')
    
    fieldsets = [
    	(None, {'fields': ['phone', 'available']}),
    	('Location',{'fields': ['address', 'neighborhood', 'city', 'county', 'zip', 'region']}),
    	('Traits',{'fields': ['price', 'area', 'listingType', 'parking', 'noSmoking', 'laundry', 'dogsAllowed', 'catsAllowed', 'dateListingPosted', 'dateListingUpdated']}),
		('Computed',{'fields': ['sublet', 'shared','electricity', 'heat', 'water']}),
		('Metadata',{'fields': ['dateListingScraped',  'updatedBy', 'deleted' ]}),
    	(None, {'fields': ['listingBody']})
    	]

class BadListingAdmin(admin.ModelAdmin):
    list_display = ('listingID',)

#list_filter = ['pub_date']
#search_fields = ['question']
	
admin.site.register(Listing, ListingAdmin)
admin.site.register(BadListing, BadListingAdmin)


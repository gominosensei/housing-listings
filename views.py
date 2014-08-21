import csv
import datetime

from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core import validators
from django.core.urlresolvers import reverse, reverse_lazy
from django.db import models
from django.forms import IntegerField
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.views.generic.edit import UpdateView


from listings.models import Listing, FreshListing  
from listings.scrape import scrapeListing, scraper, startLog
from listings.tasks import add, getNewListings

def index(request):
	#currentListings = Listing.objects.all()
	#output = currentListings   #', '.join([listing for listing in currentListings])
	#return HttpResponseRedirect('index.html')
	return TemplateResponse(request, 'listings/index.html')
            
def login_user(request):
	logout(request)
	if request.POST:
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				login(request, user)
				return TemplateResponse(request, 'listings/index.html')
			return HttpResponse('User is inactive')
		return HttpResponse('Not a valid username & password')
	return HttpResponse('Should be a POST not a GET')		
	
def logout_user(request):
	logout(request)
	return TemplateResponse(request, 'listings/index.html')
	
def detail(request, listingID):
	try:
		listing = Listing.objects.get(pk=listingID)
	except Listing.DoesNotExist:
		return HttpResponse('listing does not exist: %s' % listingID)

	bedrooms = listing.bedrooms
	description = 'This is just some fake text to give an idea of how much space this might take up when there is content'
	mapQueryString = listing.mapUrl.split('?q=')[1]
	
	return render_to_response('listings/index.html', 
	{ 'listing' : listing, 'bedrooms' : bedrooms, 'description' : description, 'mapQueryString' : mapQueryString})

def status(request):
	listingsToQuery = FreshListing.objects.filter(trouble=False).count()
	total = Listing.objects.count()
	recent = recentListings().count()
	
	report = []
	report.append('Listings in database: %s' % str(total))
	report.append('Listings included in HVL : %s' % str(recent))
	report.append('Listings to query: %s' % str(listingsToQuery))
	return HttpResponse('<br>'.join(report))
	
def scrape(request):
	return HttpResponse(getNewListings.delay())
	#return HttpResponse(getNewListings.apply_async((), queue='lopri', countdown=1))
	#return HttpResponse(scraper(True))

def scrapenow(request):
	return HttpResponse(getNewListings())
	
def discovernow(request, deep=False):
	from listings.discoverListings import discover
	return HttpResponse(discover(pagesPerCategory = 3))	
		
def discovernowdeep(request):
	from listings.discoverListings import discover
	return HttpResponse(discover(deep=True))	
		
def retrievenow(request, modifier, offset):
	from listings.retrieveListings import retrieve
	return HttpResponse(retrieve(maximumListings=50,debugMode=False,modifier=modifier,slow=False,offset=offset))	

def recentListings():
	weekago = datetime.date.today()-datetime.timedelta(days=7)
	queryset = Listing.objects.filter(deleted=False, dateListingUpdated__gte=weekago)
	return queryset
	
def excelview(request):
	weekago = datetime.date.today()-datetime.timedelta(days=7)
	#queryset = Listing.objects.filter(deleted=False, updatedBy__isnull=False, dateListingUpdated__gte=weekago)
	queryset = Listing.objects.filter(deleted=False, dateListingUpdated__gte=weekago)
	return export_xls(request, queryset)
	
def export_xls(request, queryset):
	import io
	import xlsxwriter

	output = io.BytesIO()
	workbook = xlsxwriter.Workbook(output) #, {'in_memory': True})
	worksheet = workbook.add_worksheet()

	worksheet.freeze_panes(1, 0) # # Freeze the first row.

	# Formatting
	bold = workbook.add_format({'bold': True})
	italics = workbook.add_format({'italic': True})
	top = workbook.add_format()
	top.set_align('top')
	wrap = workbook.add_format()
	wrap.set_text_wrap()
	wrap.set_align('top')
	link = workbook.add_format({'color': 'blue', 'underline': 1})
	link.set_align('top')
	
	# Column widths
	worksheet.set_column('A:A', 9)  # # bedrooms
	worksheet.set_column('B:B', 7)  # price
	worksheet.set_column('C:C', 12) # contact phone #    
	worksheet.set_column('D:D', 48) # description
	worksheet.set_column('E:E', 14) # available 
	worksheet.set_column('F:F', 35) # address
	worksheet.set_column('G:G', 6)  # ZIP code
	worksheet.set_column('H:H', 9)  # county
	worksheet.set_column('I:I', 70) # listing
	# L listing URL

	# Headers
	worksheet.write('A1', '# BR', bold)
	worksheet.write('B1', 'Price', bold)
	worksheet.write('C1', 'Contact', bold)
	worksheet.write('D1', 'Description', bold)
	worksheet.write('E1', 'Available', bold)
	worksheet.write('F1', 'Address', bold)
	worksheet.write('G1', 'ZIP', bold)
	worksheet.write('H1', 'County', italics)
	worksheet.write('I1', 'Listing', italics)
	worksheet.write('J1', 'URL', italics)

	rowNumber = 0
	
	# Listing Rows
	for l in queryset:
		rowNumber = rowNumber + 1
		worksheet.write(rowNumber, 0, l.bedroomsField(), top)
		worksheet.write(rowNumber, 1, '$' + str(l.price), top)
		worksheet.write(rowNumber, 2, l.phone, top)
		worksheet.write(rowNumber, 3, l.descriptionField(), wrap)
		# availability
		worksheet.write(rowNumber, 5, l.addressWithNeighborhood(), top)
		worksheet.write(rowNumber, 6, l.zip, top)
		# If there isn't a county, include the link to Google Maps 
		if l.county == '':
			worksheet.write_url(rowNumber, 7, l.mapUrl, link, 'unknown')
		else:	
			worksheet.write(rowNumber, 7, l.county, top)
		worksheet.write(rowNumber, 8, l.listingBody, wrap)
		worksheet.write_url(rowNumber, 9, l.url(), link)

	workbook.close()

	response = HttpResponse(output.getvalue(), mimetype="application/ms-excel")
	response['Content-Disposition'] = "attachment; filename=hvl.xlsx"
	output.close()
	return response
	
def csvview(request):
	weekago = datetime.date.today()-datetime.timedelta(days=7)
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="HousingVacancyList.csv"'

	writer = csv.writer(response)
	writer.writerow(['#BR','Price','Contact','Description','Available','Address','Region'])

	#for l in Listing.objects.all()[:5]:
	for l in Listing.objects.filter(deleted=False, updatedBy__isnull=False, dateListingUpdated__gte=weekago):
		writer.writerow([l.bedroomsField(), '$' + str(l.price), l.phone, l.descriptionField(), '', l.addressWithNeighborhood(), l.region])

	return response
	
class AllListings(ListView):
	queryset = Listing.objects.filter(deleted=False)

class DeletedListings(ListView):
	queryset = Listing.objects.filter(deleted=True)

class ReadyListings(ListView):
	weekago = datetime.date.today()-datetime.timedelta(days=7)
	queryset = Listing.objects.filter(deleted=False, updatedBy__isnull=False, dateListingUpdated__gte=weekago)
	
class Worklist(ListView):
	weekago = datetime.date.today()-datetime.timedelta(days=7)
	queryset = Listing.objects.filter(deleted=False, updatedBy=None, dateListingUpdated__gte=weekago)

class ListingUpdate(UpdateView):
	model = Listing
	
	# Require some fields that aren't required in the model
	price = IntegerField()

	fields = ['price', 'bedrooms', 'sublet', 'shared', 'phone', 'available', 'electricity', 'heat', 'water','laundry', 'parking', 'address',  'region', 'gas', 'internet', 'cable', 'lawn_care', 'snow_removal', 'trash'] #, 'dogsAllowed', 'catsAllowed', 'noSmoking']
	
	def parentUrl(self):
		if 'worklist' in self.request.path:
			return '/listings/worklist'
		if 'all' in self.request.path:
			return '/listings/all'
		if 'ready' in self.request.path:
			return '/listings/ready'
		if 'deleted' in self.request.path:
			return '/listings/deleted'
			
		return '/listings'
		url = self.request.path.split('/')
		if len(url[-1]) == 0:
			url.pop()
		url.pop()
		url.pop()
		return '/'.join(url)
		
	def listingUrl(self,form):
		return ListingUpdate.parentUrl(self) + '/listing/' + str(form.instance.listingID)
	
	def softDelete(self, form):
		form.instance.deleted = True
		form.instance.save()
		return HttpResponseRedirect(ListingUpdate.parentUrl(self))
		
	def rescrapeListing(self, form):
		startLog(True)
		listing = scrapeListing(form.instance.url())
		listing.save()
		return HttpResponseRedirect(ListingUpdate.listingUrl(self, form))
	
	@method_decorator(login_required)
	def dispatch(self, *args, **kwargs):
		#origin = args[0].path.split('/')[2]
		#self.success_url='/listings/%s' % origin
		return super(ListingUpdate, self).dispatch(*args, **kwargs)
	
	def __init__(self, *args, **kwargs):
		super(ListingUpdate, self).__init__(*args, **kwargs)
		
		#self.fields['price'].required = True
		
	def form_valid(self, form):
		form.instance.updatedBy = self.request.user		
		#return HttpResponse(ListingUpdate.parentUrl(self))
		#return HttpResponse(self.success_url)
		if 'deleteRecord' in self.request.POST:
			return ListingUpdate.softDelete(self, form)
			
		if 'saveClose' in self.request.POST:
			self.success_url=ListingUpdate.parentUrl(self)

		if 'saveStay' in self.request.POST:
			self.success_url=ListingUpdate.listingUrl(self, form)
			#return HttpResponse(self.success_url)

		if 'rescrape' in self.request.POST:
			return ListingUpdate.rescrapeListing(self, form)

		return super(ListingUpdate, self).form_valid(form)

from django import template
from listings.models import Listing  

register = template.Library()

@register.tag(name='checkbox')
def do_checkbox(parser, token):
	tag_name, field_name, field_value = token.split_contents()
	
	return CheckboxNode(field_name, field_value) 
	
class CheckboxNode(template.Node):
	def __init__(self, field_name, field_value):
		self.field_name = field_name 
		self.field_value = template.Variable(field_value )

	def render(self, context):
		field_name = self.field_name
		field_value = self.field_value.resolve(context)

		checkbox_tag = '<div class="fieldWrapper checkbox"><label><input type="checkbox"'
		checkbox_tag = checkbox_tag + ' id="id_' + field_name + '"'
		checkbox_tag = checkbox_tag + ' name="' + field_name + '"'
		
		if field_value:
			checkbox_tag = checkbox_tag + ' checked="on"'
			
		checkbox_tag = checkbox_tag + '/>' + field_name + '</label></div>'

		return checkbox_tag

@register.tag(name='address_display')
def do_address(parser, token):
	tag_name, listing = token.split_contents()
	return AddressNode(listing)
	
class AddressNode(template.Node):
	def __init__(self, listing):
		self.listing = template.Variable(listing)
		
	def render(self,context):
		listing = self.listing.resolve(context)	
	
		address = listing.address
		neighborhood = listing.neighborhood
		city = listing.city
		county = listing.county
		zip = listing.zip
		
		address_tag = '<h4>'
		
		if address and neighborhood:
			line1 = '%s (%s)' % (address, neighborhood)
		elif address:
			line1 = address
		elif neighborhood:
			line1 = neighborhood
		if line1: 
			address_tag = address_tag + line1 + '<br>'
		
		line2components = []
		if city:
			line2components.append(city)
		if county:
			line2components.append(county + ' County')
		if zip:
			line2components.append(zip)
		line2 = ', '.join(line2components)
		if line2:
			address_tag = address_tag + line2 + '<br>'
		
		address_tag = address_tag + '</h4>'

		return address_tag
		
		
@register.tag(name='listing_title')
def do_title(parser, token):
	tag_name, listing = token.split_contents()
	return TitleNode(listing)
	
class TitleNode(template.Node):
	def __init__(self, listing):
		self.listing = template.Variable(listing)
		
	def render(self,context):
		listing = self.listing.resolve(context)	
		
		title_bag = []
		
		if listing.price:
			title_bag.append('$' + str(listing.price))
			
		# location
		if listing.address:
			title_bag.append(listing.address)
		elif listing.neighborhood:
			title_bag.append(listing.neighborhood)
		else: 
			title_bag.append('Unknown Address')
			
		if listing.bedrooms:
			title_bag.append(str(listing.bedrooms) + ' bdr')
			
		if len(title_bag)>0:
			title = ' - '.join(title_bag)
		else:
			title = listing.listingID
			
		return title
			
		
			
	
		
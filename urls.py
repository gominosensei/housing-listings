from django.conf.urls import patterns, url

from listings import views

urlpatterns = patterns('',
	url(r'^$', views.index),
	url(r'^status/$', views.status, name='status'),
	url(r'^login/$', views.login_user, name='login_user'),
	url(r'^logout/$', views.logout_user, name='logout_user'),
	url(r'^all/$', views.AllListings.as_view(), name='all'),
	url(r'^deleted/$', views.DeletedListings.as_view(), name='deleted'),
	url(r'^ready/$', views.ReadyListings.as_view(), name='ready'),
	url(r'^worklist/$', views.Worklist.as_view(), name='worklist'),
	url(r'listing/(?P<pk>\d+)/$', views.ListingUpdate.as_view(), name='listing_update'),
	url(r'^scrape/$', views.scrape, name='scrape'),
	url(r'^scrapenow/$', views.scrapenow, name='scrapenow'),
	url(r'^csv/$', views.csvview, name='csvview'),
	url(r'^excel/$', views.excelview, name='excelview'),
	url(r'^discover/$', views.discovernow, name='discovernow'),
	url(r'^discover/deep/$', views.discovernowdeep, name='discovernowdeep'),
	url(r'^retrieve/(?P<modifier>\w*)/(?P<offset>\d*)$', views.retrievenow, name='retrievenow'),
)



#	url(r'^(?P<listingID>\d+)/$', views.ListingUpdate.as_view(), name='listing_update'),
#	url(r'^edit/(?P<listingID>\d+)/$', views.detail, name='detail'),

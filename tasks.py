#tasks in listings
from __future__ import absolute_import

from trc.celery import app

from listings.scrape import scraper
from listings.discoverListings import discover
from listings.retrieveListings import retrieve

@app.task
def add(x, y):
    return x + y


@app.task
def mul(x, y):
    return x * y


@app.task
def xsum(numbers):
    return sum(numbers)

@app.task
def getNewListings():
	#return scraper(False,100)
	#return discover(True)
	#return 'foo'
	return retrieve(True, 1)
	
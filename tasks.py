#tasks in listings
from __future__ import absolute_import

from trc.celery import app

from listings.scrape import scraper

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
	return scraper(False,100)

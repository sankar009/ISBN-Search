## This will update the review collection against the isbn.

import requests
from pyquery import PyQuery as pq
from lxml import etree
import datetime
from web_setting import *
from celery import Celery

from pymongo import MongoClient

#from pyelasticsearch import ElasticSearch

celery = Celery("tasks", broker="amqp://guest@localhost")

# connect to mongodb database
connection = MongoClient()
db = connection.abhi
Review= db.Review
#es = ElasticSearch("http://localhost:9200")

@celery.task
def update_review(isbn):
	attrs = {}
	d = {}
	old = Review.find_one({'_id':isbn})
	proxy = {'socks4':'127.0.0.1:9050'}	
	for key, value in urlset.items():
		t_url = value + isbn
		key_url = key + '_url'
		attrs[key_url] = t_url
		r = requests.get(t_url, proxies=proxy)	
		if r.status_code == 200:
			d[key] = pq(r.text)	


## for flipkart website
	if (d.get('flipkart') != None):
		fk = d.get('flipkart')
		attrs["flipkart"] = fk("meta[itemprop=\"price\"]").attr("content")
		try:
			attrs["ratingValue"] = float(fk("meta[itemprop=\"ratingValue\"]").attr("content"))
		except (TypeError, ValueError), e:
			attrs["ratingValue"] = 'Not Rated'
		try:
			attrs["ratingCount"] = int(fk("span[itemprop=\"ratingCount\"]").text())
		except (TypeError, ValueError), e:
			attrs["ratingCount"] = 'None'
	
	else:
		attrs['flipkart'] = old['flipkart']
		attrs['ratingValue'] = old['ratingValue']
		attrs['ratingCount'] = old['ratingCount']	
		
	attrs['_id'] = isbn
	attrs['date'] = datetime.datetime.utcnow()
	
## for Infibeam website Price
	if (d.get('Infibeam') != None):
		Ib = d.get('Infibeam')
		attrs['Infibeam'] = Ib("span[class=\"infiPrice amount price\"]").text()
	else:
		attrs['Infibeam'] = old['Infibeam']

## for Crossword website Price
	if (d.get('Crossword') != None):
		try:
			attrs['Crossword'] = d.get('Crossword')("span[class=\"variant-final-price\"]").text().strip('R')
		except AttributeError:
			attrs['Crossword'] = d.get('Crossword')("span[class=\"variant-final-price\"]").text()
	else:
		attrs['Crossword']	= old['Crossword']

## for Homeshop18 website Price
	if (d.get('Homeshop18') != None):
		try:
			attrs['Homeshop18'] = d.get('Homeshop18')("span[class=\"pdp_details_hs18Price\"]").text().strip('Rs.')
		except AttributeError:
			attrs['Homeshop18'] = d.get('Homeshop18')("span[class=\"pdp_details_hs18Price\"]").text()
	else:
		attrs['Homeshop18'] = old['Homeshop18']

## for Bookadda website Price
	if (d.get('Bookadda') != None):
		try:
			attrs['Bookadda'] = d.get('Bookadda')("span[class=\"actlprc\"]").text().strip('Rs.')
		except AttributeError:
			attrs['Bookadda'] = d.get('Bookadda')("span[class=\"actlprc\"]").text()

	else:
		attrs['Bookadda'] = old['Bookadda']
## for rediff book website
	if (d.get('Rediffbook') != None):
		try:
			attrs['Rediffbook'] = d.get('Rediffbook')("div[class=\"proddetailinforight\"]").text().split()[2]
		except (IndexError, AttributeError), e:
			attrs['Rediffbook'] = d.get('Rediffbook')("div[class=\"proddetailinforight\"]").text()
	else:
		attrs['Rediffbook'] = old['Rediffbook']

	Review.save(attrs)


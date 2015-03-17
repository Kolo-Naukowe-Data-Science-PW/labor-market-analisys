# -*- coding: utf-8 -*-
import urllib2
import lxml.html
import sys
import unicodecsv
from peewee import *

#This script downloads work offers from pracuj.pl portal
#TODO: check for timeout errors
#TODO: add some sleep time in order not to flood servers



db = SqliteDatabase("pracuj.db")

class Offer(Model):
	position = CharField()
	url = CharField()
	company_name = CharField()
	company_url = CharField()
	content = TextField()
	class Meta:
		database = db

#extract pure text or html?
def extract_offer_content(page):
	response = urllib2.urlopen(page)
	html = response.read()

	t = lxml.html.fromstring(html)
	t.make_links_absolute(page)
	
	offer = t.xpath("//div[@id='offCont']")
	#print(type(offer[0]))
	
	
	
	if( len(offer) > 0 ):
		#change <br> to newline
		for br in offer[0].xpath("*//br"):
			br.tail = "\n" + br.tail if br.tail else "\n"
		for br in offer[0].xpath("*//p"):
			br.tail = "\n" + br.tail if br.tail else "\n"
		for br in offer[0].xpath("*//li"):
			br.tail = "\n" + br.tail if br.tail else "\n"
			
		for li in offer[0].xpath("*//li"):
			if li.text:
				li.text = "*" + li.text
		#offer_html = lxml.html.tostring(offer[0])
		#return offer_html
		offer_text = lxml.html.HtmlElement.text_content(offer[0])
		return offer_text
	else:
		return ""

if not Offer.table_exists():
	Offer.create_table()


with open("results.csv", "r") as f:
	reader = unicodecsv.reader(f, encoding='utf-8',delimiter='\t',quotechar="\"",
								quoting=unicodecsv.QUOTE_ALL,lineterminator='\n')
	for row in reader:
		print(row)
		content = extract_offer_content(row[1])
		offer = Offer(position=row[0], url=row[1], company_name=row[2], company_url=row[3], content=content)
		offer.save()
		
db.close()






















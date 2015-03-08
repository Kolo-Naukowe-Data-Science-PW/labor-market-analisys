# -*- coding: utf-8 -*-
import urllib2
import lxml.html
#import sys #unused
#import unicodecsv #unused


#This script downloads work offers from pracuj.pl portal
#WARNING: number of work offers pages is hardcoded in num_pages variable
#TODO: check for timeout errors
#TODO: add some sleep time in order not to flood servers


def extract_description(page):
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

h = extract_description("http://www.pracuj.pl/praca/\
inzynier-procesu-przetworstwo-tworzyw-sztucznych-lodzkie,oferta,3811165")
print(h.encode('ascii', 'replace'))























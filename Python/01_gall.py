# -*- coding: utf-8 -*-
import urllib2
import lxml.html
import sys
import unicodecsv


#This script downloads work offers from pracuj.pl portal
#WARNING: number of work offers pages is hardcoded in num_pages variable
#TODO: check for timeout errors
#TODO: add some sleep time in order not to flood servers

def parse_page(page):
	response = urllib2.urlopen(page)
	html = response.read()

	t = lxml.html.fromstring(html)
	t.make_links_absolute(page)
	entries = t.xpath("//ul[@id='mainOfferList']/li")
	
	offers = []
	for entry in entries:
		position = entry.xpath("h2/a/@title")
		position_url = entry.xpath("h2/a/@href")
		
		#niektóre og³osznia nie maj¹ w ogóle w³asnej podstrony
		#wtedy oczywicie nie ma do niej linku
		if( len(position) == 0 ):
			position = entry.xpath("/h2/span/text()")
			position_url = [""]
			
			#w tym przypadku nie jest to w ogóle og³oszenie
			#a element typu "znajd podobne oferty"
			if(len(position) == 0):
				continue
		
		company_name = entry.xpath("//h3/a/@title")
		company_url = entry.xpath("h3/a/@href")
		
		offers.append( [position[0],position_url[0],company_name[0],company_url[0]] )
	
	return offers



page_pattern = "http://www.pracuj.pl/praca?pn="
#num_pages = 396
num_pages = 2

results = []
for p in range(1,num_pages+1):
	url = page_pattern+str(p)
	print("Parsing page {0}".format(url))
	page_results = parse_page(url)
	results.extend(page_results)
	
print(results)

#in Python 2 orginal python module csv can't handle unicode data
#with open("results.csv", "w") as f:
#	writer = csv.writer(f)
#	writer.writerows(results)


with open("Data/results.csv", "w") as f:
	writer = unicodecsv.writer(f, encoding='utf-8',delimiter='\t',quotechar="\"", quoting=unicodecsv.QUOTE_ALL)
	writer.writerows(results)





















# -*- coding: utf-8 -*-
import urllib2
import lxml.html
import sys
import unicodecsv
import time


#This script downloads work offers from pracuj.pl portal
#WARNING: number of work offers pages is hardcoded in num_pages variable
#TODO: check for timeout errors  - DONE!
#TODO: add some sleep time in order not to flood servers



def parse_page(page, attempts=3, timeout=5):
	
	for a in range(attempts):
		try:
			response = urllib2.urlopen(page)
			break #success
		except urllib2.URLError as e:
			print("Attempt {0}. Error occured. {1}".format(a,e))
			time.sleep(5) #also sleep for 5 seconds
			if( a == attempts - 1 ):
				print("Download Fail")
				raise e
	
	
	html = response.read()
		

	t = lxml.html.fromstring(html)
	t.make_links_absolute(page)
	entries = t.xpath("//ul[@id='mainOfferList']/li")
	
	offers = []
	for entry in entries:
		position = entry.xpath("h2/a/@title")
		position_url = entry.xpath("h2/a/@href")
		
		#niektóre ogłosznia nie mają w ogóle własnej podstrony
		#wtedy oczywiście nie ma do niej linku
		if( len(position) == 0 ):
			position = entry.xpath("/h2/span/text()")
			position_url = [""]
			
			#w tym przypadku nie jest to w ogóle ogłoszenie
			#a element typu "znajdź podobne oferty"
			if(len(position) == 0):
				continue
		
		#ugly
		position = position[0]
		position_url = position_url[0]
		company_name = entry.xpath("//h3/a/@title")[0]
		company_url = entry.xpath("h3/a/@href")[0]
		
		#All positions are in form "Praca [Position_Name]", we want to get only [Position_Name]
		position = position.partition(" ")[2]
		#company name same like previous
		company_name = company_name.partition(" ")[2]
		
		offers.append( [position,position_url,company_name,company_url] )
	
	return offers

page_pattern = "http://www.pracuj.pl/praca?pn="

response = urllib2.urlopen("http://www.pracuj.pl/praca")
html = response.read()
t = lxml.html.fromstring(html)
num_pages = int(t.xpath(".//*[@id='returnUrl']/ul[2]/li[5]/a/text()")[0])
print("{0} of offer pages found!".format(num_pages))

#num_pages=2

results = []
for p in range(1,num_pages+1):
	url = page_pattern+str(p)
	print("Parsing page {0}".format(url))
	page_results = parse_page(url)
	results.extend(page_results)
	
#print(results)

#in Python 2 orginal python module csv can't handle unicode data
#with open("results.csv", "w") as f:
#	writer = csv.writer(f)
#	writer.writerows(results)


with open("results.csv", "w") as f:
	writer = unicodecsv.writer(f, encoding='utf-8',delimiter='\t',quotechar="\"",
								quoting=unicodecsv.QUOTE_ALL, lineterminator='\n')
	writer.writerows(results)





















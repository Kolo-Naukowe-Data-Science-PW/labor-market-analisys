# -*- coding: utf-8 -*-
import urllib2
import lxml.html
import sys
import unicodecsv
import datetime
from peewee import *
import time

#This script downloads work offers from pracuj.pl portal

db = SqliteDatabase("pracuj.db")

class Offer(Model):
	id = PrimaryKeyField()
	position = CharField()
	url = CharField()
	company_name = CharField()
	company_url = CharField()
	content = TextField()
	date_posted = DateField()
	employment_type = CharField()
	base_salary = CharField()	
	salary_low = IntegerField()
	salary_high = IntegerField()
	joblocation = CharField()
		
	class Meta:
		database = db

class Tag(Model):
	id = PrimaryKeyField()
	tag = CharField()
	
	class Meta:
		database = db

class OfferTag(Model):
	offer = ForeignKeyField(Offer)
	tag = ForeignKeyField(Tag)
	
	class Meta:
		database = db
		

#
#except socket.timeout issue ?
def extract(page, attempts=3):
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
	
	#Check if offer is still in portal!
	
	#Get data and trim whitespaces 
	#content
	offer = t.xpath("//div[@id='offCont']")
	
	#location:
	#city, voivodeship
	joblocation = t.xpath("//li[@itemprop='joblocation']")[0].text_content().strip()
	
	# specialist,manager, student...
	employment_type = t.xpath("//span[@itemprop='employmentType']")[0].text_content().strip()
	
	#YYYY-MM-DD
	date_posted_str = t.xpath("//span[@itemprop='datePosted']")[0].text_content().strip()
	date_posted = datetime.datetime.strptime(date_posted_str,"%Y-%m-%d").date()
	
	#in string: "do koñca x dni"
	#currently we don't write this to db
	#days_left = t.xpath("//span[@class='offerTop__cnt_main_details_item_text_time']")[0].text_content().strip()
	
	#often salary is not specified in offer
	if(len(t.xpath("//span[@itemprop='baseSalary']")) > 0):
		base_salary = t.xpath("//span[@itemprop='baseSalary']")[0].text_content().strip()
		
		#now process string to get integer values for salary range
		#string looks like: 
		#"powy¿ej 15 tys. z³" (above 15,000 pln)
		#"8 - 10 tys. z³" ( 8,000 - 10,000 pln)
		# so if only one number occures than we may assume that it is top boundary
		
		#is it ok to assign 0 when null?
		salary_range = [int(s) for s in base_salary.split() if s.isdigit()]
		if(len(salary_range) == 2):
			salary_low = salary_range[0]
			salary_high = salary_range[1]
		elif(len(salary_range)==1):
			salary_high = salary_range[0]
			salary_low = 0
		else:
			salary_high = 0
			salary_low = 0
		
	else:
		base_salary = ""
		salary_high = 0
		salary_low = 0
	
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
		content = offer[0].text_content().strip()
	else:
		content = ""
	
	tags = t.xpath("//li[@class='offerMain__left_similar_list_item']//a/text()")	
	
	
	#insert all into dict (except tags)
	summary = {"joblocation":joblocation, "employment_type":employment_type,
		"content":content, "date_posted":date_posted, "base_salary":base_salary,
		"salary_low": salary_low, "salary_high":salary_high}
		
	return (summary,tags)
	
	
	

	



		

## Add here any new tables!
if not Offer.table_exists():
	db.create_tables([Offer,Tag,OfferTag])




#quick and fast code to obtain row to start reading CSV file.
#it is passed as first argument in command line

offers = []
tag_dict = {}
tags = []
offers_tags = []

if(len(sys.argv) > 1):
	start_row = int(sys.argv[1])
	#and prepare tag_dict!
	tags_db = Tag.select()
	for t in tags_db:
		tag_dict[t.tag]=t.id
	
else:
	start_row = 0

	

#load all entries to memory ( list of dictionaries )

with open("results.csv", "r") as f:
	reader = unicodecsv.reader(f, encoding='utf-8',delimiter='\t',quotechar="\"",
								quoting=unicodecsv.QUOTE_ALL,lineterminator='\n')
	for i,row in enumerate(reader):
		if i + 1 >= start_row:
			print(i)
			print(row)
			
			# try to download and process offer
			# don't know if  catching here error is OK
			try:
				entry_info, entry_tags = extract(row[1])
			except urllib2.URLError as e:
				print("Download error")
				print("Writing to database and exit")
				print("You may start downloading from row x by running dd_offer x")
				break
			#dirty way to throw away not valid pages
			except IndexError:
				print("NOT A VALID PAGE")
				continue
			
			#feed offer info with information from CSV file
			entry_info.update(position=row[0], url=row[1], company_name=row[2], company_url=row[3])
			
			#update tag_dict and tags list
			for t in entry_tags:
				if not t in tag_dict:
					tags.append({"id":len(tag_dict)+1,"tag":t})
					tag_dict[t]=len(tag_dict)+1
					
			#many to many relation
			offers_tags.extend( [ {"offer":i+1, "tag":tag_dict[t]} for t in entry_tags] )
			
			offers.append( entry_info )
			
# save them all!
with db.transaction():
	Offer.insert_many(offers).execute()
	Tag.insert_many(tags).execute()
	OfferTag.insert_many(offers_tags).execute()

db.close()






















import sqlite3
import requests
import hashlib
import os
import time

from selenium import webdriver

from lxml import html
from lxml import etree
from lxml.etree import tostring

queries = ["https://www.hasznaltauto.hu/talalatilista/PDNG2VC3V2NTAEG5RNLRAIDJKLT3GUVF7OJS3ICJDGEOGMMONSBW5OGK3Y5QNGTCFZPYZTUZY6MYOAKZ4TZMXSZMS5BEHQGGHICRP3GFTGYUYCR7UBAXUQQX5QEO3JIAJIOS6M36KOXMFAF6Q4FPYIGOK64ZXE7UBQJ3RUVIGYTNSSJB2YGHYLUZQMKNROJSRG5WYEJR5ROZ7K5WICQ3ZAZT3WMEPCTM7QPKK2GAIH5UOAJJX7QZBR2OQFWLXQLRZUVTVJA3A25UDPZ3W676CHXAB2ZSF3VFM2ITZC4PZLHFR5WGCY6S3QL77WYGBB56UPQGGDKWS7W4MYVH6WMH66KXJ4QUYGLQDJFFKROXQJRYUU5UPYZGCKZETIMRNHA5JZDTDRIE6XUPYHLJWUMOZOKTBANSW6ZTZHFFRMCWXUFGSIQWL3Z6LBFAZU5FGQRFVFMG7R2XA7WRHGVUAIIMDQYGOEDHTEC7NK5K64IPJJTJHHKHHOP6YIW2YVSO7I55T7WIGOF73DQATXNQNXIHL3S3T4UZOHRHM7QEKW256LCRQWHV2QIXV7COOFHTYY2CGNMB3ZLH4OR6H4OHQ5SSBQD4KK55TWL2H5UD4OV5YR7URIN4VXK6OEWMDBCUEHM4GXLJO4BFJCBGEDPK7DAFVNME7GUDKKIDFPLYBZQR6USBLRWHQGXFPA5W5WZV64R4E72I7FPY323PMZU5NWJCZPB7Z2A62E35LFN5OAEZITIXD6Q36AV73D56LZ7QDXGONTGQ"]
#"https://www.hasznaltauto.hu/talalatilista/PDNG2VCZR2RTAEF5RNHRBSGS3XHOOSBDZVH25ABKINARYLYV3EDHK2HF5ZOQMJUD5F6FC6VPSZLYWANZFXSVPECFFGCYNCBNPECSP3GFSGYUFCRQUBCXHBZO2IEO3JAASM5Z4ZX4UJ6I2EKDB42YIQI4Z5ZDGJ7JDE3OAK5LLRFLFEKCVQM7QXBSPMU3B42VCZ3XURNEWBTX3LXKYDCOUCW6OZRR4KMK6H5SMRILD3OF6BKGQULQ4ZPKCQGLSFY4246KGR3TYFEC72DH472BXLQRVYYCXYS6DILMTM7YKPJYYFKPNTI5GEX424HQX5QYHIJUHKWB5KFM2WHMPU66MX6BG5JQQUYWXSDEVVLTZSQUZRQH4NKKGMJTWFS6F4BBU2EKQ3S5XCRFTLIFPPXBHYULQU6ZS3DBFRL2WXWFHQIUW2HYNZRNI5U5FGR3EVBMW7RZWA3XQ43K6AGGYCG2EOEC3TFS6NK5264AKJMLZEXJGXKO6Y3NTW6J3YSXWN6ZPNYXZMGBMO4KA26RO77EPHZZS6PSMZ7AGWJ256C6FSWHV2QMA36ES4KPHRRYG5RATXSBPY4T4PY2OZ3FEHBHYUE33GMUEGBUT6OF5YQHFFKKART5F3AYEUJUVCRSOS5BQKZYCLBI2UYB3H4XKNFZQT22DNSWDZI22HPJFHVMYL4DJUHXNLIOJ3X5SLRTSYNYVXCPPZHIIKPNULAL56HXHIF3MOUBV4RNDCNSS6U37YC7YRX7UOH4ON4NO5WGO"]

class change:
	def __init__(self, car, reason):
		self.car = car
		self.reason = reason
		
	def __str__(self):
		return self.reason + "\n" + str(self.car)
		
	def toListItem(self, template):
		filled = template
		filled = filled.replace("%LISTING_ID%", self.car.id)
		filled = filled.replace("%LISTING_PRICE%", self.car.price)
		filled = filled.replace("%LISTING_LINK%", self.car.url)
		filled = filled.replace("%LISTING_TITLE%", self.car.title)
		filled = filled.replace("%LISTING_IMAGE%", self.car.img)
		filled = filled.replace("%LISTING_REASON%", self.reason)
		return filled

class car:
	def __init__(self, id, title, url, price, img):
		self.id = id
		self.title = title
		self.url = url
		self.price = price.replace('\xa0', '&nbsp;')
		self.img = img
		
	def __str__(self):
		return self.id + "\n" + self.title + "\n" + self.price + "\n___________"
	
	def __eq__(self, other):
		if isinstance(other, car):
			return self.id == other.id and self.title == other.title and self.url == other.url and self.price == other.price and self.img == other.img
		return False
		
	def diffFromOld(self, other):
		difference = ""
		if self.title != other.title:
			difference += "title changed\n"
		if self.price != other.price:
			difference += "price changed from " + str(other.price) + "\n"
		if self.img != other.img:
			difference += "image changed"
		return difference
			
		
def page(num, base):
	return base+"/page"+str(num)
	
header = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0',}

car1 = car('a','b','c','d','e')
car2 = car('a','b','c','d','e')

for query in queries:
	hash = hashlib.md5(query.encode('utf-8')).hexdigest()[:6]
	dirpath = os.getcwd() + "/" + hash
	
	if not os.path.exists(dirpath):
		os.makedirs(dirpath)
	
	initReq = requests.get(query, headers=header)
	initTree = html.fromstring(initReq.content)
	num_of_pages = int(initTree.xpath('//link[@rel="last"]/@href')[0].split("page")[1])
	
	if os.path.isfile(dirpath+"/newdata.db"):
		os.remove(dirpath+"/newdata.db")
		
	newdb = sqlite3.connect(dirpath+"/newdata.db")
	
	try:
		newdb.execute("CREATE TABLE cars(id TEXT, title TEXT, url TEXT, price TEXT, img TEXT)")
	except sqlite3.OperationalError:
		print(newdb.execute("SELECT * from cars").fetchall())
		newdb.close()
		quit()
	
	results = []
	
	for pagenum in range(1,num_of_pages+1):
		print("\rProcessing page " + str(pagenum) + " out of " + str(num_of_pages) + " for query " + hash, end='')
		request = requests.get(page(pagenum, query))
		tree = html.fromstring(request.content)
		listings = tree.xpath('.//div[contains(@class, "row talalati-sor")]')
		
		for listing in listings:
			kepsor = listing.find('.//div[@class="talalatisor-kep"]')
			adatsor = listing.find('.//div[@class="talalatisor-adatok"]')
			
			title = kepsor.find('.//a').get("title")
			url = kepsor.find('.//a').get("href")
			
			try:
				img = kepsor.find('.//img[@class="img-responsive lazy"]').get('data-lazyurl')
			except AttributeError:
				img = ""
				
			price = adatsor.find('.//div[@class="vetelar"]').text
			id = listing.find('.//*[@data-hirkod]').get('data-hirkod')
			
			thiscar = car(id, title, url, price, img)
			results.append(thiscar)
			
	for currentCar in results:
		newdb.execute("INSERT INTO cars VALUES (?,?,?,?,?)", (currentCar.id, currentCar.title, currentCar.url, currentCar.price, currentCar.img))
		newdb.commit()
		
	print("... done.")
	
	print("Generating report...")
	
	changes = []
	
	if not os.path.isfile(dirpath+"/data.db"):
		changes = list(map(lambda item: change(item, "new"), results))
	else:
		olddb = sqlite3.connect(dirpath+"/data.db")
		for currentCar in results:
			oldres = olddb.execute("SELECT * from cars WHERE id=?", [currentCar.id]).fetchone()
			if oldres is not None:
				oldcar = car(oldres[0],oldres[1],oldres[2],oldres[3],oldres[4])
				if oldcar != currentCar:
					changes.append(change(currentCar, currentCar.diffFromOld(oldcar)))
			else:
				changes.append(change(currentCar, "new"))
		olddb.close()
			
	
	if len(changes) is not 0:
		templateFile = open(os.getcwd() + "/delta_template")
		listTemplateFile = open(os.getcwd() + "/listing_template")
		listTemplate = listTemplateFile.read()
		deltaFile = open(dirpath + "/" + str(time.time()).replace('.','') + ".html", "w+", encoding='utf-8')
		
		for line in templateFile:
			if not line.startswith("%DELTA%"):
				deltaFile.write(line)
			else:
				for change in changes:
					deltaFile.write(change.toListItem(listTemplate))
					
		templateFile.close()
		deltaFile.close()
	
	newdb.close()
	
	if os.path.isfile(dirpath+"/data.db"):
		os.remove(dirpath+"/data.db")
	os.rename(dirpath+"/newdata.db", dirpath+"/data.db")

	
#generate index page
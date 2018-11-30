import sqlite3
import requests
import hashlib
import os
import time
from datetime import datetime

import urllib

from glob import glob

from lxml import html
from lxml import etree
from lxml.etree import tostring

class query:
	def __init__(self, name, url):
		self.name = name
		self.url = url

query1 = query("Celica", "https://www.hasznaltauto.hu/talalatilista/PDNG2VC3V2NTAEG5RNLRAIDJKLT3GUVF7OJS3ICJDGEOGMMONSBW5OGK3Y5QNGTCFZPYZTUZY6MYOAKZ4TZMXSZMS5BEHQGGHICRP3GFTGYUYCR7UBAXUQQX5QEO3JIAJIOS6M36KOXMFAF6Q4FPYIGOK64ZXE7UBQJ3RUVIGYTNSSJB2YGHYLUZQMKNROJSRG5WYEJR5ROZ7K5WICQ3ZAZT3WMEPCTM7QPKK2GAIH5UOAJJX7QZBR2OQFWLXQLRZUVTVJA3A25UDPZ3W676CHXAB2ZSF3VFM2ITZC4PZLHFR5WGCY6S3QL77WYGBB56UPQGGDKWS7W4MYVH6WMH66KXJ4QUYGLQDJFFKROXQJRYUU5UPYZGCKZETIMRNHA5JZDTDRIE6XUPYHLJWUMOZOKTBANSW6ZTZHFFRMCWXUFGSIQWL3Z6LBFAZU5FGQRFVFMG7R2XA7WRHGVUAIIMDQYGOEDHTEC7NK5K64IPJJTJHHKHHOP6YIW2YVSO7I55T7WIGOF73DQATXNQNXIHL3S3T4UZOHRHM7QEKW256LCRQWHV2QIXV7COOFHTYY2CGNMB3ZLH4OR6H4OHQ5SSBQD4KK55TWL2H5UD4OV5YR7URIN4VXK6OEWMDBCUEHM4GXLJO4BFJCBGEDPK7DAFVNME7GUDKKIDFPLYBZQR6USBLRWHQGXFPA5W5WZV64R4E72I7FPY323PMZU5NWJCZPB7Z2A62E35LFN5OAEZITIXD6Q36AV73D56LZ7QDXGONTGQ")
query2 = query("Tiburon", "https://www.hasznaltauto.hu/talalatilista/PDNG2VCZR2RTAEF5RNHRBSGS3XHOOSBDZVH25ABKINARYLYV3EDHK2HF5ZOQMJUD5F6FC6VPSZLYWANZFXSVPECFFGCYNCBNPECSP3GFSGYUFCRQUBCXHBZO2IEO3JAASM5Z4ZX4UJ6I2EKDB42YIQI4Z5ZDGJ7JDE3OAK5LLRFLFEKCVQM7QXBSPMU3B42VCZ3XURNEWBTX3LXKYDCOUCW6OZRR4KMK6H5SMRILD3OF6BKGQULQ4ZPKCQGLSFY4246KGR3TYFEC72DH472BXLQRVYYCXYS6DILMTM7YKPJYYFKPNTI5GEX424HQX5QYHIJUHKWB5KFM2WHMPU66MX6BG5JQQUYWXSDEVVLTZSQUZRQH4NKKGMJTWFS6F4BBU2EKQ3S5XCRFTLIFPPXBHYULQU6ZS3DBFRL2WXWFHQIUW2HYNZRNI5U5FGR3EVBMW7RZWA3XQ43K6AGGYCG2EOEC3TFS6NK5264AKJMLZEXJGXKO6Y3NTW6J3YSXWN6ZPNYXZMGBMO4KA26RO77EPHZZS6PSMZ7AGWJ256C6FSWHV2QMA36ES4KPHRRYG5RATXSBPY4T4PY2OZ3FEHBHYUE33GMUEGBUT6OF5YQHFFKKART5F3AYEUJUVCRSOS5BQKZYCLBI2UYB3H4XKNFZQT22DNSWDZI22HPJFHVMYL4DJUHXNLIOJ3X5SLRTSYNYVXCPPZHIIKPNULAL56HXHIF3MOUBV4RNDCNSS6U37YC7YRX7UOH4ON4NO5WGO")

queries = [query1, query2]

class change:
	def __init__(self, car, summary, reason):
		self.car = car
		self.summary = summary
		self.reason = reason
		
	def __str__(self):
		return self.reason + "\n" + str(self.car)
		
	def toListItem(self, template):
		filled = template.replace("%LISTING_REASON%", self.summary)
		filled = filled.replace("%LISTING_ID%", self.car.id)
		filled = filled.replace("%LISTING_PRICE%", self.car.price)
		filled = filled.replace("%LISTING_LINK%", self.car.url)
		filled = filled.replace("%LISTING_TITLE%", self.car.title)
		filled = filled.replace("%LISTING_IMAGE%", self.car.img)
		filled = filled.replace("%DETAILED_REASON%", self.reason)
		filled = filled.replace("%LISTING_DATA%", self.car.data)
		return filled

class car:
	def __init__(self, id, title, url, price, img, data):
		self.id = id
		self.title = title
		self.url = url
		self.price = price.replace('\xa0', '&nbsp;')
		self.img = img
		self.data = data
		
	def __str__(self):
		return self.id + "\n" + self.title + "\n" + self.price + "\n___________"
	
	def __eq__(self, other):
		if isinstance(other, car):
			return self.id == other.id and self.title == other.title and self.url == other.url and self.price == other.price and self.img == other.img and self.data == other.data
		return False
		
	def diffFromOld(self, other):
		difference = ""
		if self.title != other.title:
			difference += "title changed<br>\n"
		if self.price != other.price:
			difference += "price changed from " + str(other.price) + "<br>\n"
		if self.img != other.img:
			difference += "image changed<br>\n"
		if self.data != other.data:
			difference += "data changed<br>\n"
		return difference
			
		
def page(num, base):
	return base+"/page"+str(num)
	
def epoch2timestamp(ts):
	return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
	
#non-absolute path is used for html generation, so changing this only would be unwise
cachedir = os.getcwd() + "/cache/"
	
#this really should have its own module
def loadToCache(imgurl):
	if imgurl == "NotFound":
		return "../resources/notfound.png"
	extension = imgurl.split(".")[-1]
	hash = hashlib.md5(imgurl.encode('utf-8')).hexdigest()
	cacheFile = cachedir + hash + "." + extension
	
	if not os.path.isfile(cacheFile):
		try:
			urllib.request.urlretrieve(imgurl, cacheFile)
		except:
			raise
			return "../resources/notfound.png"
			
	return "../cache/" + hash + "." + extension
	
header = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0',}

if not os.path.exists(cachedir):
		os.makedirs(cachedir)

for query in queries:
	hash = hashlib.md5(query.url.encode('utf-8')).hexdigest()[:6]
	dirpath = os.getcwd() + "/data_" + query.name.strip() + "_" + hash
	
	if not os.path.exists(dirpath):
		os.makedirs(dirpath)
	
	initReq = requests.get(query.url, headers=header)
	initTree = html.fromstring(initReq.content)
	
	try:
		num_of_pages = int(initTree.xpath('//link[@rel="last"]/@href')[0].split("page")[1])
	except IndexError:
		num_of_pages = 1
	
	if os.path.isfile(dirpath+"/newdata.db"):
		os.remove(dirpath+"/newdata.db")
		
	newdb = sqlite3.connect(dirpath+"/newdata.db")
	
	try:
		newdb.execute("CREATE TABLE cars(id TEXT, title TEXT, url TEXT, price TEXT, img TEXT, cdata TEXT)")
	except sqlite3.OperationalError:
		print(newdb.execute("SELECT * from cars").fetchall())
		newdb.close()
		quit()
	
	results = []
	
	for pagenum in range(1,num_of_pages+1):
		print("\rProcessing page " + str(pagenum) + " out of " + str(num_of_pages) + " for query " + query.name, end='')
		request = requests.get(page(pagenum, query.url))
		tree = html.fromstring(request.content)
		listings = tree.xpath('.//div[contains(@class, "row talalati-sor")]')
		
		for listing in listings:
			kepsor = listing.find('.//div[@class="talalatisor-kep"]')
			adatsor = listing.find('.//div[@class="talalatisor-adatok"]')
			info = adatsor.find('.//div[@class="talalatisor-info adatok"]')
			
			
			title = kepsor.find('.//a').get("title")
			url = kepsor.find('.//a').get("href")
			
			try:
				img = kepsor.find('.//img[@class="img-responsive lazy"]').get('data-lazyurl')
			except AttributeError:
				img = "NotFound"
				
			img = loadToCache(img)
			price = adatsor.find('.//div[@class="vetelar"]').text
			id = listing.find('.//*[@data-hirkod]').get('data-hirkod')
			databoxes = info.findall('.//span')
			maybeData = list(map(lambda databox: databox.text, databoxes))
			data = " ".join(filter(lambda el: el is not None, maybeData)) + " kilométeróra állása: "
			km = info.find('.//abbr[@title="Kilométeróra állása"]')
			if km is not None:
				data += km.text
			else:
				data += "? km"
			
			thiscar = car(id, title, url, price, img, data)
			results.append(thiscar)
			
	for currentCar in results:
		newdb.execute("INSERT INTO cars VALUES (?,?,?,?,?,?)", (currentCar.id, currentCar.title, currentCar.url, currentCar.price, currentCar.img, currentCar.data))
		newdb.commit()
		
	print("... done.")
	
	newIDs = list(map(lambda newresult: newresult.id, results))	
	changes = []
	
	if not os.path.isfile(dirpath+"/data.db"):
		changes = list(map(lambda item: change(item, "new", ""), results))
	else:
		olddb = sqlite3.connect(dirpath+"/data.db")
		for currentCar in results:
			oldres = olddb.execute("SELECT * from cars WHERE id=?", [currentCar.id]).fetchone()
			if oldres is not None:
				oldcar = car(*oldres)
				if oldcar != currentCar:
					changes.append(change(currentCar, "changed", currentCar.diffFromOld(oldcar)))
			else:
				changes.append(change(currentCar, "new", ""))
				
		oldCarData = olddb.execute("SELECT * from cars").fetchall()
		oldCars = list(map(lambda tuple: car(*tuple), oldCarData))
		for oldCar in oldCars:
			if oldCar.id not in newIDs:
				changes.append(change(oldCar, "deleted", "deleted"))
		
		olddb.close()
			
	
	if len(changes) is not 0:
		templateFile = open(os.getcwd() + "/templates/delta_template")
		listTemplateFile = open(os.getcwd() + "/templates/listing_template")
		listTemplate = listTemplateFile.read()
		dfilename = dirpath + "/" + str(time.time()) + ".html"
		deltaFile = open(dfilename, "w+", encoding='utf-8')
		fullDeltaFile = open(dfilename[:-5] + ".full.html", "w+", encoding='utf-8')
		
		for line in templateFile:
			if not line.startswith("%DELTA%"):
				fullDeltaFile.write(line)
				deltaFile.write(line)
			else:
				for thisChange in changes:
					cli = thisChange.toListItem(listTemplate)
					deltaFile.write(cli)
					fullDeltaFile.write(cli)
					
				resultsAsChanges = list(map(lambda simpleResult: change(simpleResult, "", ""), results))
				changeIDs = list(map(lambda alreadyWrittenChange: alreadyWrittenChange.car.id, changes))
				filteredResults = filter(lambda r: r.car.id not in changeIDs, resultsAsChanges)
				
				for fres in filteredResults:
					fullDeltaFile.write(fres.toListItem(listTemplate))
				
					
		templateFile.close()
		fullDeltaFile.close()
	
	newdb.close()
	
	if os.path.isfile(dirpath+"/data.db"):
		os.remove(dirpath+"/data.db")
	os.rename(dirpath+"/newdata.db", dirpath+"/data.db")


if os.path.isfile(os.getcwd()+"/menu.html"):
	os.remove(os.getcwd()+"/menu.html")
	
indexTemplateFile = open(os.getcwd() + "/templates/menu_template")
indexFile = open(os.getcwd() + "/menu.html", "w+", encoding='utf-8')
dirs = glob(os.getcwd()+"/data_*/")

for line in indexTemplateFile:
	if not line.startswith("%MENUITEMS%"):
		indexFile.write(line)
	else:
		for dir in dirs:
			indexFile.write("<li>" + dir.split("data_")[-1][:-1] + "\n<ul>\n")
			
			allhtmls = glob(dir + "*.html")[::-1]
			htmls = filter(lambda h: not h.endswith("full.html"), allhtmls)
			
			nonAbsolute = list(map(lambda abs: "/".join(abs.split('\\')[-2:]), htmls))
			links = list(map(lambda pth: "<li><a href=\""+pth+"\" target=\"main\">" + epoch2timestamp(float(pth.split("/")[-1][:-5])) + "</a> <a href =\"" + pth[:-5] + ".full.html\" target=\"main\">Δ</a>\n", nonAbsolute)) 
			
			for link in links:
				indexFile.write(link)
			
			indexFile.write("</li>\n</ul>\n")
			
		
		
indexTemplateFile.close()
indexFile.close()
























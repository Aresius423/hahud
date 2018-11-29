import sqlite3
import requests
import hashlib
import os

from lxml import html
from lxml import etree
from lxml.etree import tostring

queries = ["https://www.hasznaltauto.hu/talalatilista/PDNG2VC3V2NTAEG5RNLRAIDJKLT3GUVF7OJS3ICJDGEOGMMONSBW5OGK3Y5QNGTCFZPYZTUZY6MYOAKZ4TZMXSZMS5BEHQGGHICRP3GFTGYUYCR7UBAXUQQX5QEO3JIAJIOS6M36KOXMFAF6Q4FPYIGOK64ZXE7UBQJ3RUVIGYTNSSJB2YGHYLUZQMKNROJSRG5WYEJR5ROZ7K5WICQ3ZAZT3WMEPCTM7QPKK2GAIH5UOAJJX7QZBR2OQFWLXQLRZUVTVJA3A25UDPZ3W676CHXAB2ZSF3VFM2ITZC4PZLHFR5WGCY6S3QL77WYGBB56UPQGGDKWS7W4MYVH6WMH66KXJ4QUYGLQDJFFKROXQJRYUU5UPYZGCKZETIMRNHA5JZDTDRIE6XUPYHLJWUMOZOKTBANSW6ZTZHFFRMCWXUFGSIQWL3Z6LBFAZU5FGQRFVFMG7R2XA7WRHGVUAIIMDQYGOEDHTEC7NK5K64IPJJTJHHKHHOP6YIW2YVSO7I55T7WIGOF73DQATXNQNXIHL3S3T4UZOHRHM7QEKW256LCRQWHV2QIXV7COOFHTYY2CGNMB3ZLH4OR6H4OHQ5SSBQD4KK55TWL2H5UD4OV5YR7URIN4VXK6OEWMDBCUEHM4GXLJO4BFJCBGEDPK7DAFVNME7GUDKKIDFPLYBZQR6USBLRWHQGXFPA5W5WZV64R4E72I7FPY323PMZU5NWJCZPB7Z2A62E35LFN5OAEZITIXD6Q36AV73D56LZ7QDXGONTGQ"]
#"https://www.hasznaltauto.hu/talalatilista/PDNG2VCZR2RTAEF5RNHRBSGS3XHOOSBDZVH25ABKINARYLYV3EDHK2HF5ZOQMJUD5F6FC6VPSZLYWANZFXSVPECFFGCYNCBNPECSP3GFSGYUFCRQUBCXHBZO2IEO3JAASM5Z4ZX4UJ6I2EKDB42YIQI4Z5ZDGJ7JDE3OAK5LLRFLFEKCVQM7QXBSPMU3B42VCZ3XURNEWBTX3LXKYDCOUCW6OZRR4KMK6H5SMRILD3OF6BKGQULQ4ZPKCQGLSFY4246KGR3TYFEC72DH472BXLQRVYYCXYS6DILMTM7YKPJYYFKPNTI5GEX424HQX5QYHIJUHKWB5KFM2WHMPU66MX6BG5JQQUYWXSDEVVLTZSQUZRQH4NKKGMJTWFS6F4BBU2EKQ3S5XCRFTLIFPPXBHYULQU6ZS3DBFRL2WXWFHQIUW2HYNZRNI5U5FGR3EVBMW7RZWA3XQ43K6AGGYCG2EOEC3TFS6NK5264AKJMLZEXJGXKO6Y3NTW6J3YSXWN6ZPNYXZMGBMO4KA26RO77EPHZZS6PSMZ7AGWJ256C6FSWHV2QMA36ES4KPHRRYG5RATXSBPY4T4PY2OZ3FEHBHYUE33GMUEGBUT6OF5YQHFFKKART5F3AYEUJUVCRSOS5BQKZYCLBI2UYB3H4XKNFZQT22DNSWDZI22HPJFHVMYL4DJUHXNLIOJ3X5SLRTSYNYVXCPPZHIIKPNULAL56HXHIF3MOUBV4RNDCNSS6U37YC7YRX7UOH4ON4NO5WGO"]

class car:
	def __init__(self, title, url, img, price):
		self.title = title
		self.url = url
		self.price = price
		self.img = img
		
	def __str__(self):
		return "\n" + self.title + "\n" + self.price + "\n___________"
		
def page(num, base):
	return base+"/page"+str(num)
		
header = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0',}

for query in queries:
	hash = hashlib.md5(query.encode('utf-8')).hexdigest()[:6]
	dirpath = os.getcwd() + "/" + hash
	if not os.path.exists(dirpath):
		os.makedirs(dirpath)
	
	initReq = requests.get(query, headers=header)
	initTree = html.fromstring(initReq.content)
	num_of_pages = int(initTree.xpath('//link[@rel="last"]/@href')[0].split("page")[1])
	conn = sqlite3.connect(dirpath+"/data.db")
	
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
			
			thiscar = car(title, url, img, price)
			results.append(thiscar)
			
	for car in results:
		print(car)
	print("... done.")
	conn.close()
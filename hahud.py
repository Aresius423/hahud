import hashlib
import os

from cache import *
from datamodels import *
from htmlgenerator import *
from hahu_processor import *
from dao import *
from queries import *		
	
for query in queries:
	hash = hashlib.md5(query.url.encode('utf-8')).hexdigest()[:6]
	dirpath = os.getcwd() + "/data_" + query.name.strip() + "_" + hash
	
	results = fetch_results_from_query(query)
			
	newdb = setupNewDB(dirpath)
	insertResults(newdb, results)
		
	print("... ", end="")
	
	changes = findChanges(dirpath, results)
			
	if len(changes) is not 0:
		generateDelta(dirpath, changes, results)
	
	print("done. ", end='')
	if len(changes) is not 0:
		print(str(len(changes)) + " change(s)")
	else:
		print("")
	
	newdb.close()
	archiveDatabase(dirpath)

if os.path.isfile(os.getcwd()+"/menu.html"):
	os.remove(os.getcwd()+"/menu.html")
	
print("Generating main view...", end='')
generateMenu()
print(" all done.\n")
import hashlib
import os

from htmlgenerator import generateMenu, generateDelta
from hahu_processor import fetch_results_from_query
from dao import setupNewDB, insertResults, findChanges, archiveDatabase
from queries import queries

for query in queries:
    query_hash = hashlib.md5(query.url.encode("utf-8")).hexdigest()[:6]
    dirpath = os.getcwd() + "/data_" + query.name.strip() + "_" + query_hash

    results = fetch_results_from_query(query)

    newdb = setupNewDB(dirpath)
    insertResults(newdb, results)

    print("... ", end="")

    changes = findChanges(dirpath, results)

    if not changes:
        generateDelta(dirpath, changes, results)

    print("done. ", end="")
    if not changes:
        print(str(len(changes)) + " change(s)")
    else:
        print("")

    newdb.close()
    archiveDatabase(dirpath)

if os.path.isfile(os.getcwd() + "/menu.html"):
    os.remove(os.getcwd() + "/menu.html")

print("Generating main view...", end="")
generateMenu()
print(" all done.\n")

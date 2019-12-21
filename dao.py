import os
from typing import List

import sqlite3

from datamodels import car


def setupNewDB(dirpath):
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)

    if os.path.isfile(dirpath + "/newdata.db"):
        os.remove(dirpath + "/newdata.db")

    newdb = sqlite3.connect(dirpath + "/newdata.db")

    try:
        newdb.execute(
            "CREATE TABLE cars(id TEXT, title TEXT, url TEXT, price TEXT, img TEXT, cdata TEXT)"
        )
    except sqlite3.OperationalError:
        print("Error setting up the database")
        newdb.close()
        quit()

    return newdb


def insertResults(db, results):
    for res in results:
        db.execute(
            "INSERT INTO cars VALUES (?,?,?,?,?,?)",
            (res.listing_id, res.title, res.url, res.price, res.img, res.data),
        )
        db.commit()


def findChanges(dirpath, results: List[car]) -> List[car]:
    changes = []
    newIDs = list(map(lambda newresult: newresult.listing_id, results))

    if not os.path.isfile(dirpath + "/data.db"):
        changes = list(map(lambda item: item.with_change_reasons("new"), results))
    else:
        olddb = sqlite3.connect(dirpath + "/data.db")
        for currentCar in results:
            oldres = olddb.execute(
                "SELECT * from cars WHERE id=?", [currentCar.listing_id]
            ).fetchone()
            if oldres is not None:
                oldcar = car(*oldres)
                if oldcar != currentCar:
                    changes.append(
                        currentCar.with_change_reasons(
                            'changed',
                            currentCar.diffFromOld(oldcar),
                        )
                    )
            else:
                changes.append(currentCar.with_change_reasons('new'))

        oldCarData = olddb.execute("SELECT * from cars").fetchall()
        oldCars = list(map(lambda tpl: car(*tpl), oldCarData))
        for oldCar in oldCars:
            if oldCar.listing_id not in newIDs:
                changes.append(oldCar.with_change_reasons("deleted"))

        olddb.close()

    return changes


def archiveDatabase(dirpath):
    if os.path.isfile(dirpath + "/data.db"):
        os.remove(dirpath + "/data.db")
    os.rename(dirpath + "/newdata.db", dirpath + "/data.db")

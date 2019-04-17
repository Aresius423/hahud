import os
import time
from datetime import datetime

from datamodels import *
from glob import glob

def epoch2timestamp(ts):
        return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

def generateDelta(dirpath, changes, results):
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
        
def generateMenu():
        menuTemplateFile = open(os.getcwd() + "/templates/menu_template")
        menuFile = open(os.getcwd() + "/menu.html", "w+", encoding='utf-8')
        dirs = glob(os.getcwd()+"/data_*/")

        for line in menuTemplateFile:
                if not line.startswith("%MENUITEMS%"):
                        menuFile.write(line)
                else:
                        for dir in dirs:
                                menuFile.write("<li>" + dir.split("data_")[-1][:-1] + "\n<ul>\n")
                                
                                allhtmls = glob(dir + "*.html")[::-1]
                                htmls = sorted(filter(lambda h: not h.endswith("full.html"), allhtmls))
                                
                                nonAbsolute = list(map(lambda abs: "/".join(abs.split('\\')[-2:]), htmls))
                                links = list(map(lambda pth: "<li><a href=\""+pth[pth.find('data_'):]+"\" target=\"main\">" + epoch2timestamp(float(pth[pth.find('data_'):].split("/")[-1][:-5])) + "</a> <a href =\"" + pth[:-5] + ".full.html\" target=\"main\">Δ</a>\n", nonAbsolute))
                                
                                for link in links:
                                        menuFile.write(link)
                                
                                menuFile.write("</li>\n</ul>\n")
                                
                        
                        
        menuTemplateFile.close()
        menuFile.close()

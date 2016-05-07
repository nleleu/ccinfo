#!/usr/bin/env python
#-*- coding: utf-8 -*-
import dryscrape
import codecs
from lxml import etree
from pykml.factory import KML_ElementMaker as KML
from bs4 import BeautifulSoup
import glob
import os
import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtWebKit import *
from lxml import html

BASE_WEBSITE = "http://www.campingcar-infos.com/Francais/"
BASE_URL = BASE_WEBSITE+"ccip.php?numero="
DESC_FOLDER = "html/"
LOGOS_FOLDER = "html/logos/icones/"
LIMIT = 5

QAPP = QApplication(sys.argv)

class Render(QWebPage):
  def __init__(self, url):
    QWebPage.__init__(self)
    self.loadFinished.connect(self._loadFinished)
    self.mainFrame().load(QUrl(url))
    QAPP.exec_()

  def _loadFinished(self, result):
    self.frame = self.mainFrame()
    QAPP.quit()

def getOfflineIds():
    files = glob.glob(DESC_FOLDER+"*.html")
    res = set()
    for f in files:
        id = os.path.splitext(os.path.basename(f))[0]
        id = int(id)
        res.add(id)
    return res


def generateKML(ids, spotList):
    km = KML.kml()
    doc = KML.Document(KML.name("Aires camping car info"))
    icones = glob.glob(LOGOS_FOLDER+"A*")
    for icone in icones:
        icone = icone.replace(DESC_FOLDER, "")
        type = os.path.basename(icone).replace("40.gif", "")
        style = KML.Style(
          KML.IconStyle(
            KML.scale(1.0),
            KML.Icon(
              KML.href(icone),
            ),
          ),
          id=type.lower()
        )
        doc.append(style)
    for id in ids:
        idStr = str(id)
        with codecs.open(DESC_FOLDER+"/"+idStr+".html",'r',encoding='utf-8') as f:
            place = KML.Placemark(
                    KML.name(spotList[id]["name"]),
                    KML.description(f.read()),
                    KML.styleUrl("#"+spotList[id]["type"].lower()),
                    KML.Point(
                        KML.coordinates(spotList[id]["lat"]+","+spotList[id]["long"])
                        )
                    )
            doc.append(place)
    km.append(doc)
    print(etree.tostring(km))

def readASC(filepath):
    res = {}
    with codecs.open(filepath,'r',encoding='latin1') as f:
        for line in f:
            info = line.split(",")
            lat = info[0]
            long = info[1]
            name = info[2][1:-2]
            id = int(name[name.rindex(' ')+1:])
            type = name.split(" ")[0]
            res[id] = {"lat" : lat, "long" : long, "name" : name, "id" : id, "type" : type}
    return res

def dumpToFile(id, data):
    with codecs.open(DESC_FOLDER+"/"+id+".html",'w',encoding='utf-8') as f:
        f.write("<html><meta charset='utf-8'>")
        f.write(data)
        f.write("</html>")

def getDesc(spotList, alreadyDumped):
    dumped = 0
    for id,spot in spotList.items():
        if dumped >= LIMIT:
            return True
        if id in alreadyDumped:
            print("Spot id "+str(id)+" already dumped")
            continue
        dumped += 1
        #http://stackoverflow.com/questions/8049520/web-scraping-javascript-page-with-python
        url = BASE_URL+str(id)
        #url = "../toto.html"
        print("Dumping "+url)
        r = Render(url)
        resultTmp = unicode(r.frame.toHtml())
        #session = dryscrape.Session()
        #session.visit(BASE_URL+id)
        #response = session.body()
        soup = BeautifulSoup(resultTmp, "lxml")
        fiche = soup.find(id="fiche")
        imgs = fiche.find_all("img")
        for img in imgs:
            img['src'] = BASE_WEBSITE + img.get("src")
        dumpToFile(str(id), fiche.prettify())


if __name__ == "__main__":
  spotList = readASC("ATOTALES_CCI.asc")
  dumpedIds = getOfflineIds()

  #getDesc(spotList, dumpedIds)
  generateKML(dumpedIds, spotList)

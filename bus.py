#!/usr/bin/python

import urllib
import re
import os
import time


#######      Sophia - Nice      #######
#9  	ALBERT 1er VERDUN
#2064  	LES TEMPLIERS
#2155 	SKEMA


#######      Nice - Sophia      #######
#81     LYCEE MASSENA
#43     GUSTAVE V
#32     GAMBETTA / PROMENADE
#84     MAGNAN / PROMENADE
#25     FABRON MUSEE D'ART NAIF
#27 	CARRAS / PROMENADE
#968    FERBER / PROMENADE
#4      AEROPORT / PROMENADE
#2148   SANTOLINE

patternBus = "<div class=\"data\">\s*?<span class=\"txtbold\">Ligne</span> : (?P<line>.+?)\s*?<div>(?P<timesheet>.*?)\s*?</div>\s*?</div>"
patternTime = "(?P<time>.+?)direction <span class=\"txtbold\">(?P<direction>.+?)</span>(?P<isRealtime>.*?)<br />"


def getTime(timeSection):
    #print timeSection
    pattern = re.compile("<span class=\"txtbold\">.+?</span>")
    textBold = re.search(pattern, timeSection)
    if textBold == None:
        time = '0'
    else:
        textBold = textBold.group()
        if 'h' in textBold:
            time = textBold[22:len(textBold)-7]    #<span class="txtbold">11h27</span>
        else: 
            time = textBold[22:len(textBold)-7]    #<span class="txtbold">13</span>
        
    return time
    
def getTimeNow(text):
    patternTimeNow = re.compile("<span>Il est</span>\s*?<span class=\"txtbold\">.+?</span>")
    timeGroup = re.search(patternTimeNow, text)
    timeNow = None
    if timeGroup:
        timeNowSection = timeGroup.group()
        timeNow = re.search(r'\d\d?h\d\d', timeNowSection).group()
    return timeNow

def getAll(content):
    lineNeedToTrack = 500
    now = getTimeNow(content)
    if now:
        print "Now is " + now + "\n"
    else:
        print "No tracking available"
        return
    
    for busMatches in re.finditer(patternBus, content, re.IGNORECASE | re.DOTALL):    #for each line of bus
        line = busMatches.group('line')
        if line != lineNeedToTrack:
            continue
        print "Bus " + line + " is comming"
        for timeMatches in re.finditer(patternTime, busMatches.group('timesheet'), re.IGNORECASE | re.DOTALL):    #for each line in timesheet
            busTime = getTime(timeMatches.group('time'))
            timeMatches.group('direction')
            print (("\tat " if 'h' in busTime else "\tin ") + busTime + " min direction " + 
                  timeMatches.group('direction') +
                  timeMatches.group('isRealtime').strip())
                  
def getInfoByStation(station):
    print "Checking ..."
    content = urllib.urlopen("https://cg06.tsi.cityway.fr/qrcode/" + str(station)).read()
    #print content
    getAll(content)
    
def main():
    stationNumber = raw_input("Station number: ")
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        getInfoByStation(stationNumber)
        time.sleep(20)
        #break
        
if __name__ == "__main__": 
    main()
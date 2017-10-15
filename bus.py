#!/usr/bin/python
from __future__ import print_function
import urllib
import re
import os
import time
import datetime
from collections import OrderedDict

#9      ALBERT 1er VERDUN

mappingStationSophiaNice = OrderedDict()
mappingStationSophiaNice['2155']=   'SKEMA    '
mappingStationSophiaNice['2064']=   'TEMPLIERS'

mappingStationNiceSophia = OrderedDict()
mappingStationNiceSophia['81']=   'MASSENA  '
mappingStationNiceSophia['43']=   'GUSTAVE  '
mappingStationNiceSophia['32']=   'GAMBETTA '
mappingStationNiceSophia['84']=   'MAGNAN   '
mappingStationNiceSophia['25']=   'FABRON   '
mappingStationNiceSophia['27']=   'CARRAS   '
mappingStationNiceSophia['56']=   'VALLIERE '
mappingStationNiceSophia['4']=    'AEROPORT '
mappingStationNiceSophia['2148']= 'SANTOLINE'

timeSheetNiceSophia = OrderedDict()

lineNeedToTrack = '230'
destinationToTrack = 'Sophia'  
timeCheck = 0
    
    
patternBus = "<div class=\"data\">\s*?<span class=\"txtbold\">Ligne</span> : (?P<line>.+?)\s*?<div>(?P<timesheet>.*?)\s*?</div>\s*?</div>"
patternTime = "(?P<time>.+?)direction <span class=\"txtbold\">(?P<direction>.+?)</span>(?P<isRealtime>.*?)<br />"

def setTimeToStandardFormat(elapsedTime):
    return (datetime.datetime.now() + datetime.timedelta(minutes = int(elapsedTime))).strftime("%Hh%M")

def getTimeFrom(timeSection):
    pattern = re.compile("<span class=\"txtbold\">.+?</span>")
    textBold = re.search(pattern, timeSection)
    if textBold == None:
        time = 'now'
    else:
        textBold = textBold.group()
        if 'h' in textBold:
            time = textBold[22:len(textBold)-7]    #<span class="txtbold">11h27</span>
        else: 
            time = textBold[22:len(textBold)-7]    #<span class="txtbold">13</span>
            time = setTimeToStandardFormat(time)
        
    return time
    
def getTimeNow(text):
    patternTimeNow = re.compile("<span>Il est</span>\s*?<span class=\"txtbold\">.+?</span>")
    timeGroup = re.search(patternTimeNow, text)
    timeNow = None
    if timeGroup:
        timeNowSection = timeGroup.group()
        timeNow = re.search(r'\d\d?h\d\d', timeNowSection).group()
    return timeNow

def getAll(content, station):
    now = getTimeNow(content)
    if now:
        timeCheck = datetime.datetime.strptime(now, "%Hh%M")
        #for each line of bus
        for busMatches in re.finditer(patternBus, content, re.IGNORECASE | re.DOTALL):    
            line = busMatches.group('line')
            if line == lineNeedToTrack:
                timeSheetNiceSophia[station] = list()
                #for each line in timesheet
                for timeMatches in re.finditer(patternTime, busMatches.group('timesheet'), re.IGNORECASE | re.DOTALL):    
                    busTime = getTimeFrom(timeMatches.group('time')) + timeMatches.group('isRealtime').strip()
                    direction = timeMatches.group('direction')
                    if destinationToTrack in direction:
                        timeSheetNiceSophia[station].append(busTime)
                  
def getInfoByStation(station):
    content = urllib.urlopen("https://cg06.tsi.cityway.fr/qrcode/" + str(station)).read()
    getAll(content, station)
    
def show():
    os.system('cls' if os.name == 'nt' else 'clear')
    print ("Bus " + lineNeedToTrack + " direction " + destinationToTrack)
    for stationNumber in timeSheetNiceSophia.keys():
        print (mappingStationNiceSophia[stationNumber] , end='\t')
        for time_t in timeSheetNiceSophia[stationNumber]:
            print (time_t, end='\t')
        print ('...')
        
def reorganizeBusTime():
    nextBus = timeSheetNiceSophia[len(timeSheetNiceSophia)-1][0]
    if 'h' in nextBus:
        for stationNumber in reversed(timeSheetNiceSophia.keys()):
            if (nextBus == 'passed' or timeSheetNiceSophia[stationNumber][0] > nextBus):
                timeSheetNiceSophia[stationNumber].insert(0, 'passed')
            nextBus = timeSheetNiceSophia[stationNumber][0]
        
def main():
    while True:
        startTimer = time.time()
        print ("Checking...")
        timeSheetNiceSophia.clear()#clear list hours
        for stationNumber in mappingStationNiceSophia.keys():
            getInfoByStation(stationNumber)
        show()
        elapsedTimer = time.time() - startTimer
        print ("Time execution: " + str(round(elapsedTimer,2)) + "s")
        sleepTime = max(0,20 - elapsedTimer)
        time.sleep(sleepTime)
        
if __name__ == "__main__": 
    main()
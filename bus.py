#!/usr/bin/python
from __future__ import print_function
import urllib.request
import requests
import re
import os
import time
import datetime
from collections import OrderedDict

#9      ALBERT 1er VERDUN

timeSheetNiceSophia = OrderedDict() #time table

lineNeedToTrack = '230'

if datetime.datetime.now().time() < datetime.time(12):
    destinationToTrack = 'Sophia Gare Routière'  
    stationToTrack = '27'
    
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
else:
    destinationToTrack = 'Cathédrale-Vieille Ville' 
    stationToTrack = '2064'
    
    mappingStationNiceSophia = OrderedDict()
    mappingStationNiceSophia['2157']=   'SOPHIA   '
    mappingStationNiceSophia['2037']=   'CARDOULIN'
    mappingStationNiceSophia['1919']=   'GARBEJAIR'
    mappingStationNiceSophia['2117']=   'POMPIDOU '
    mappingStationNiceSophia['2035']=   'BRUSCS   '
    mappingStationNiceSophia['1897']=   'EGANAUDE '
    mappingStationNiceSophia['1942']=   'BOUILLIDE'
    mappingStationNiceSophia['2032']=   'BELUGUES '
    mappingStationNiceSophia['2155']=   'SKEMA    '
    mappingStationNiceSophia['2159']=   'SOPHIE L '
    mappingStationNiceSophia['1852']=   'CAQUOT   '
    mappingStationNiceSophia['1939']=   'INRIA    '
    mappingStationNiceSophia['2064']=   'TEMPLIERS'
    mappingStationNiceSophia['2039']=   'CHAPPES  '
    mappingStationNiceSophia['2414']=   '3 MOULINS'
    
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
    with urllib.request.urlopen("https://cg06.tsi.cityway.fr/qrcode/" + str(station)) as url:
        content = url.read().decode('utf-8')
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
    nextBus = next(reversed(timeSheetNiceSophia))[0]
    if 'h' in nextBus:
        for stationNumber in reversed(timeSheetNiceSophia.keys()):
            print (nextBus)
            if (nextBus == 'passed' or timeSheetNiceSophia[stationNumber][0] > nextBus or nextBus == 'now'):
                timeSheetNiceSophia[stationNumber].insert(0, 'passed')
            nextBus = timeSheetNiceSophia[stationNumber][0]
    time.sleep(10)
    
def addingPassedBus():
    previousStation = 'null'
    for stationNumber in timeSheetNiceSophia.keys():
        isNeedCleanUp = False
        for aTime in reversed(timeSheetNiceSophia[stationNumber]):
            if isNeedCleanUp:
                if '*' in aTime:
                    timeSheetNiceSophia[stationNumber].remove(aTime)
            elif '*' not in aTime:
                isNeedCleanUp = True
                
        if previousStation != 'null'\
           and len(timeSheetNiceSophia[previousStation]) != 0\
           and timeSheetNiceSophia[previousStation][0] != 'now'\
           and len(timeSheetNiceSophia[stationNumber]) != 0\
           and (timeSheetNiceSophia[stationNumber][0] == 'now'\
                or timeSheetNiceSophia[stationNumber][0] < timeSheetNiceSophia[previousStation][0]):
            for stationBefore in timeSheetNiceSophia.keys():
                if stationBefore == stationNumber:
                    break
                else:
                    timeSheetNiceSophia[stationBefore].insert(0,'x')
                    
        previousStation = stationNumber    
        
        
def main():
    while True:
        startTimer = time.time()
        print ("Checking...")
        timeSheetNiceSophia.clear()#clear list hours
        for stationNumber in mappingStationNiceSophia.keys():
            getInfoByStation(stationNumber)
        addingPassedBus()
        show()
        elapsedTimer = time.time() - startTimer
        print ("Time execution: " + str(round(elapsedTimer,2)) + "s")
        sleepTime = max(0,20 - elapsedTimer)
        time.sleep(sleepTime)
        
if __name__ == "__main__": 
    main()

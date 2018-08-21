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

mappingStationSophiaNice = OrderedDict()
mappingStationSophiaNice['2157']=   'SOPHIA   '
mappingStationSophiaNice['2037']=   'CARDOULIN'
mappingStationSophiaNice['1919']=   'GARBEJAIR'
mappingStationSophiaNice['2117']=   'POMPIDOU '
mappingStationSophiaNice['2035']=   'BRUSCS   '
mappingStationSophiaNice['1897']=   'EGANAUDE '
mappingStationSophiaNice['1942']=   'BOUILLIDE'
mappingStationSophiaNice['2159']=   'SOPHIE L '
mappingStationSophiaNice['2155']=   'SKEMA    '
mappingStationSophiaNice['2032']=   'BELUGUES '
mappingStationSophiaNice['1852']=   'CAQUOT   '
mappingStationSophiaNice['1939']=   'INRIA    '
mappingStationSophiaNice['2064']=   'TEMPLIERS'
mappingStationSophiaNice['2039']=   'CHAPPES  '
mappingStationSophiaNice['2414']=   '3 MOULINS'

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
destinationToTrack = 'Sophia Gare Routi'  
timeCheck = 0
notifSentTime = 'timeNotifIsSent'
    
    
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
    
def notif(station):
    if station in timeSheetNiceSophia.keys() and len(timeSheetNiceSophia[station]) != 0:
        i=0
        global notifSentTime
        while '*' in timeSheetNiceSophia[station][i] and i<len(timeSheetNiceSophia[station])-1:
            i=i+1
        if timeSheetNiceSophia[station][i] != notifSentTime and timeSheetNiceSophia[station][i] == setTimeToStandardFormat('7'):
            requests.post("https://maker.ifttt.com/trigger/buscomming/with/key/GrY7zljRcKbwitY4U5lts")
            notifSentTime = timeSheetNiceSophia[station][i]
            print ("NOTIFICATION SENT")
        
def main():
    while True:
        startTimer = time.time()
        print ("Checking...")
        timeSheetNiceSophia.clear()#clear list hours
        getInfoByStation('27')
        notif('27')
        show()
        elapsedTimer = time.time() - startTimer
        print ("Time execution: " + str(round(elapsedTimer,2)) + "s")
        sleepTime = max(0,20 - elapsedTimer)
        time.sleep(sleepTime)
        
if __name__ == "__main__": 
    main()
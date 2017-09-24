import urllib
import re
import os
import time


#27 CARRAS / PROMENADE
#9  ALBERT 1er VERDUN
stationNumber = 9
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
    timeNowSection = re.search(patternTimeNow, text).group()
    timeNow = re.search(r'\d\d?h\d\d', timeNowSection).group()
    return timeNow

def getAll(content):
    print "Now is " + getTimeNow(content) + "\n"
    
    for busMatches in re.finditer(patternBus, content, re.IGNORECASE | re.DOTALL):    #for each line of bus
        print "Bus " + busMatches.group('line') + " is comming"
        for timeMatches in re.finditer(patternTime, busMatches.group('timesheet'), re.IGNORECASE | re.DOTALL):    #for each line in timesheet
            busTime = getTime(timeMatches.group('time'))
            timeMatches.group('direction')
            print (("\tat " if 'h' in busTime else "\tin ") + busTime + " min direction " + 
                  timeMatches.group('direction') +
                  timeMatches.group('isRealtime').strip())
                  
def getInfoByStation(station):
    content = urllib.urlopen("https://cg06.tsi.cityway.fr/qrcode/" + str(station)).read()
    #print content
    getAll(content)
    
def main():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        getInfoByStation(stationNumber)
        time.sleep(20)
        #break
        
if __name__ == "__main__": 
    main()
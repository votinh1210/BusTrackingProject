import urllib
import re
import os
import time

#27 CARRAS / PROMENADE
#9  ALBERT 1er VERDUN
stationNumber = 9
pattern = "<div class=\"data\">\s*<span class=\"txtbold\">Ligne</span> : (?P<line>.+?)\s*<div>(?P<article>.+?) <span class=\"txtbold\">(?P<time>.*?)</span>.+?direction <span class=\"txtbold\">(?P<destination>.*?)</span>"

def getTime():
    content = urllib.urlopen("https://cg06.tsi.cityway.fr/qrcode/" + str(stationNumber)).read()
    #content = url.read().decode('utf-8')
    #print (content)
    os.system('cls' if os.name == 'nt' else 'clear')
    for matches in re.finditer(pattern, content, re.IGNORECASE | re.DOTALL):
        print("Bus " + matches.group('line') + " destination " + 
                       matches.group('destination') + " is comming " + 
                       ('in ' if matches.group('article') == 'dans' else 'at ') + 
                       matches.group('time'))
    time.sleep(5)

def main():
    while True:
        getTime()
        
        
if __name__ == "__main__": 
    main()
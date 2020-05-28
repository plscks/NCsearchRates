#!/usr/bin/python3
# Nexus Clash search rates utility v0.8
# Written by plscks
# Utilizes WikiMedia built in api
# API documentation : https://wiki.nexuscla.sh/wiki/api.php
#
# Requires the requests module
#
################
## TO DO LIST ##
################
# [X] get location page IDs in json format
# [X] sort page IDs into [locations: pageids]
# [X] get wikitext from pages by ID in json format
# [X] clean wiki text of useless information store in pageInfo =  [itemName: findWeight]
# [X] calculate search rate from findWeight totals
# [X] store in dictionary as locationRates = [itemName: searchRate]
# [X] store in dictionary within dictionary masterRates = [itemName: [locationName: searchRate]]
# [x] sort itemName by searchRate descending <= Sorting to be done in javascript
# [x] output as json to be imported in RRFBot
# [X] BUG - some pages with only inside or outside tables break things
#
# Is this a test?
# It has to be.....
import json
import re
import requests
import time

def getRawLocations():
    """Gets json data of all current breath locations wiki page ids"""
    response = requests.get('https://wiki.nexuscla.sh/wiki/api.php?action=query&list=categorymembers&cmtitle=Category:Current%20Locations&cmlimit=max&format=json')
    if response.status_code == 200:
        return json.loads(response.content.decode('utf-8'))
    else:
        return None

def getCleanLocations():
    """Sorts current breath locations into single dictionary {'Tile name': 'pageid'}"""
    locations = getRawLocations()
    masterLocation = {}
    for i in locations['query']['categorymembers']:
        masterLocation[i['title']] = i['pageid']
    return masterLocation

def getItemRates(location, pageid):
    """Gets item find weight from locations pages"""
    time.sleep(15)
    items = {}
    response = requests.get('https://wiki.nexuscla.sh/wiki/api.php?action=parse&format=json&prop=wikitext&pageid=' + str(pageid))
    if response.status_code == 200:
        wikitext = json.loads(response.content.decode('utf-8'))
    else:
        print('Bad page ID, canceling request.')
    wikitext = wikitext['parse']['wikitext']['*']
    oddsText = wikitext[wikitext.find('|FindOut='):]
    if oddsText.startswith('|FindOut=') == False:
        print(f'No search odds listed for {location}')
        inOdds = 1
        outOdds = 1
    else:
        oddsText = oddsText.split('|HideOut=', 1)[0]
        inOdds = oddsParse(oddsText, location)[0]
        outOdds = oddsParse(oddsText, location)[1]
    if 'Items found inside:' in wikitext:
        shortWikitext = wikitext[wikitext.find('|+ Items found inside:'):]
        insideFinds = shortWikitext.split('background-color:#f0f8ff;"', 1)[0]
        if 'Items found outside' in wikitext:
            outsideFinds = wikitext[wikitext.find('|+ Items found outside:'):]
            outsideFinds = outsideFinds.split('|}', 1)[0]
        else:
            insideFinds = insideFinds.split('|}', 1)[0]
            outsideFinds = None
    else:
        shortWikitext = wikitext[wikitext.find('|+ Items found outside:'):]
        outsideFinds = shortWikitext.split('|}', 1)[0]
        if outsideFinds.startswith('|+ Items found outside:') == False:
            outsideFinds = None
        insideFinds = None
    if insideFinds == None:
        if outsideFinds == None:
            print(f'No items to find at {location}')
            return {}
        output = {}
        outsideItemNameList = textParse(outsideFinds, outOdds)[0]
        outsideItemPercentList = textParse(outsideFinds, outOdds)[1]
        number = -1
        for i in outsideItemNameList:
            number += 1
            output[i] = {'Outside ' + location: outsideItemPercentList[number]}
        return output
    else:
        if outsideFinds == None:
            output = {}
            insideItemNameList = textParse(insideFinds, inOdds)[0]
            insideItemPercentList = textParse(insideFinds, inOdds)[1]
            number = -1
            for i in insideItemNameList:
                number += 1
                output[i] = {'Inside ' + location: insideItemPercentList[number]}
            return output
        else:
            totalItemNameList = []
            totalItemPercentList = []
            output = {}
            insideItemNameList = textParse(insideFinds, inOdds)[0]
            insideItemPercentList = textParse(insideFinds, inOdds)[1]
            outsideItemNameList = textParse(outsideFinds, outOdds)[0]
            outsideItemPercentList = textParse(outsideFinds, outOdds)[1]
            number = -1
            for i in insideItemNameList:
                number += 1
                output[i] = {'Inside ' + location: insideItemPercentList[number]}
            number = -1
            for i in outsideItemNameList:
                number += 1
                if i in output:
                    output[i].update({'Outside ' + location: outsideItemPercentList[number]})
                else:
                    output[i] = {'Outside ' + location: outsideItemPercentList[number]}
            return output

def oddsParse(text, location):
    try:
        outOdds = int(re.search(r'(?<=\|FindOut=)\d+', text).group())
    except AttributeError:
        print(f'No listed outside search odds for {location}.')
        outOdds = 1
    try:
        inOdds = int(re.search(r'(?<=\|FindIn=)\d+', text).group())
    except AttributeError:
        print(f'No listed inside search odds for {location}.')
        inOdds = 1
    if inOdds == 0:
        inOdds = 1
    else:
        inOdds = inOdds / 100
    if outOdds == 0:
        outOdds = 1
    else:
        outOdds = outOdds / 100
    return inOdds, outOdds

def textParse(text, baseOdds):
    """Pulls item names and correcsponding weights from input wiki text"""
    itemNames = re.finditer(r'(?<=\[\[).+?(?=\])', text)
    itemNameList = []
    itemRateList = []
    for m in itemNames:
        itemNameList.append(m[0])
    itemRates = re.finditer(r'(?<=\| )\d+', text)
    for m in itemRates:
        itemRateList.append(int(m[0]))
    itemRatePercent = weight2Rate(itemRateList, baseOdds)
    return itemNameList, itemRatePercent

def weight2Rate(inputWeights, baseOdds):
    """converts item find weight to search rates by percentage"""
    weightSum = sum(inputWeights)
    percentRates = []
    for i in inputWeights:
        percentRates.append(((i / weightSum) * baseOdds) * 100)
    return percentRates

def masterOutput():
    masterLocations = getCleanLocations()
    findRates = {}
    locationData = {}
    masterList = {}
    for k, v in masterLocations.items():
        locationData[k] = getItemRates(k, v)
        for key, value in locationData[k].items():
            if key in masterList:
                masterList[key].update(value)
            else:
                masterList[key] = value
    return masterList

if __name__ == "__main__":
    with open('searchRates.json', 'w') as json_file:
        json.dump(masterOutput(), json_file)

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
        outsideItemWeights = textParse(outsideFinds, outOdds)[2]
        number = -1
        for i in outsideItemNameList:
            number += 1
            totalWeight = sum(outsideItemWeights)
            flatPercent = (outsideItemWeights[number] / totalWeight) * 100
            print(f'Outside {location}: [{outsideItemPercentList[number]}, {outsideItemWeights[number]}, {flatPercent}]')
            output[i] = {'Outside ' + location: [outsideItemPercentList[number], outsideItemWeights[number], flatPercent]}
        return output
    else:
        if outsideFinds == None:
            output = {}
            insideItemNameList = textParse(insideFinds, inOdds)[0]
            insideItemPercentList = textParse(insideFinds, inOdds)[1]
            insideItemWeights = textParse(insideFinds, inOdds)[2]
            number = -1
            for i in insideItemNameList:
                number += 1
                totalWeight = sum(insideItemWeights)
                flatPercent = (insideItemWeights[number] / totalWeight) * 100
                print(f'Inside {location}: [{insideItemPercentList[number]}, {insideItemWeights[number]}, {flatPercent}]')
                output[i] = {'Inside ' + location: [insideItemPercentList[number], insideItemWeights[number], flatPercent]}
            return output
        else:
            totalItemNameList = []
            totalItemPercentList = []
            output = {}
            insideItemNameList = textParse(insideFinds, inOdds)[0]
            insideItemPercentList = textParse(insideFinds, inOdds)[1]
            insideItemWeights = textParse(insideFinds, inOdds)[2]
            outsideItemNameList = textParse(outsideFinds, outOdds)[0]
            outsideItemPercentList = textParse(outsideFinds, outOdds)[1]
            outsideItemWeights = textParse(outsideFinds, outOdds)[2]
            number = -1
            for i in insideItemNameList:
                number += 1
                totalWeight = sum(insideItemWeights)
                flatPercent = (insideItemWeights[number] / totalWeight) * 100
                print(f'Inside {location}: [{insideItemPercentList[number]}, {insideItemWeights[number]}, {flatPercent}]')
                output[i] = {'Inside ' + location: [insideItemPercentList[number], insideItemWeights[number], flatPercent]}
            number = -1
            for i in outsideItemNameList:
                number += 1
                #print('i:')
                #print(i)
                if i in output:
                    totalWeight = sum(outsideItemWeights)
                    flatPercent = (outsideItemWeights[number] / totalWeight) * 100
                    print(f'Outside {location}: [{outsideItemPercentList[number]}, {outsideItemWeights[number]}, {flatPercent}]')
                    output[i].update({'Outside ' + location: [outsideItemPercentList[number], outsideItemWeights[number], flatPercent]})
                else:
                    totalWeight = sum(outsideItemWeights)
                    flatPercent = (outsideItemWeights[number] / totalWeight) * 100
                    print(f'Outside {location}: [{outsideItemPercentList[number]}, {outsideItemWeights[number]}, {flatPercent}]')
                    output[i] = {'Outside ' + location: [outsideItemPercentList[number], outsideItemWeights[number], flatPercent]}
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
    return itemNameList, itemRatePercent, itemRateList

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

def wikiOutParse():
    testData = {'Bottle of Whiskey': {'Inside Airport': [7.5, 1, 25.0], 'Inside Bar': [1.7391304347826086, 4, 10.0], 'Outside Colonial Ship Deck': [0.14285714285714285, 1], 'In side Corner Store': [1.111111111111111, 1, 3.8], 'Inside Dark Alehouse': [1.3333333333333335, 3, 6.5], 'Inside Fire Station': [0.9615384615384616, 1, 4.0], 'Inside Hotel': [0.28368794326241137, 2], 'Inside Inn': [4.597701149425287, 20, 23.0], 'Inside Magi Armory': [0.7541899441340782, 9], 'Inside Nightclub': [1.7647058823529416, 3], 'Inside Restaurant': [0.3125, 1], 'Inside Slum': [0.17543859649122806, 1], 'Inside Supermarket': [0.8333333333333334,2], 'Inside Tavern': [4.444444444444445, 20], 'Inside University': [0.625, 1]}, 'Fuel Can': {'Inside Airport': [7.5, 1], 'Outside Bridge': [0.37735849056603776, 2], 'Outside Bridge Column': [0.37735849056603776, 3], 'Inside Fire Station': [0.9615384615384616, 1], 'Inside Forgotten Power Plant': [1.4705882352941175, 2], 'Inside Forgotten Prison': [2.3529411764705883, 2], 'Inside Gas Station': [5.128205128205128, 10], 'Inside Iron Garrison': [1.4657980456026058, 15], 'Inside Magi Armory': [1.9273743016759777, 23], 'Inside Power Plant': [2.5, 2], 'Inside Radiant Armory': [0.5244755244755245, 5], 'Outside Ruined Bridge': [0.37735849056603776, 4], 'Inside Stygian Foundry': [0.8522727272727272, 5]}, 'Newspaper': {'Inside Airport':[7.5, 1], 'Outside Airport': [7.43801652892562, 60], 'Outside Apartment Building': [7.43801652892562, 60], 'Inside Augmentation Clinic': [0.9259259259259258, 2], 'Outside Augmentation Clinic': [7.43801652892562, 60], 'Outside Bakery': [6.8181818181818175, 5], 'Inside Bank': [6.0, 11], 'Outside Bank': [7.43801652892562, 60], 'Outside Bar': [7.43801652892562, 60], 'Outside Bridge': [0.9433962264150945, 4],  'Outside Bridge Column': [0.9433962264150945, 6], 'Outside Chateau': [7.43801652892562, 60], 'Inside Church': [7.6923076923076925, 100], 'Outside Church': [7.43801652892562, 60], 'Inside Corner Store': [3.3333333333333335, 3], 'Outside Corner Store': [7.43801652892562, 60], 'Outside Costume Shop': [6.521739130434782, 10], 'Outside Dark Alehouse': [7.43801652892562, 60], 'Outside Factory': [2.380952380952381, 60], 'Inside Farmhouse': [0.6993006993006994, 5], 'Outside Farmhouse': [3.75, 1], 'Outside Ferry Terminal': [6.25, 1],  'Outside Fire Station': [4.958677685950414, 60], 'Outside Forgotten Prison': [7.43801652892562, 60], 'Inside Gas Station': [2.564102564102564, 5], 'Outside Gas Station': [7.43801652892562, 60], 'Outside Gun Store': [7.43801652892562, 60], 'Outside Hardware Store': [7.43801652892562, 60], 'Outside Hospital': [4.958677685950414, 60], 'Inside Hotel': [2.1276595744680855, 15], 'Outside Hotel': [4.958677685950414, 60], 'Outside Junkyard': 1.1811023622047243, 'Inside Library': [8.980477223427332, 138], 'Outside Library': [7.43801652892562, 60], 'Outside Magi Armory': [7.43801652892562, 60], 'Inside Mall': [0.9554140127388535, 5], 'Outside Mall': [7.43801652892562, 60], 'Outside Mansion': [7.43801652892562, 60], 'Inside Mosque': [10.526315789473683, 120], 'Outside Mosque': [7.43801652892562, 60], 'Inside Mountain Research Center': [4.0, 10], 'Inside Museum': [3.6885245901639343, 30], 'Outside Museum': [7.43801652892562, 60], 'Outside Nightclub': [7.43801652892562, 60], 'Inside Observatory': [6.0, 1], 'Outside Observatory': [7.43801652892562, 60], 'Inside Office Building': [11.249999999999998, 12], 'Outside Office Building': [7.43801652892562, 60], 'Outside Park': 0.8241758241758242, 'Inside Parliament': [8.000000000000002,6], 'Outside Parliament': [6.870229007633586, 60], 'Outside Pharmacy': [7.43801652892562, 60], 'Outside Pier': 0.1923076923076923, 'Outside Police Station': [4.958677685950414, 60], 'Outside Port Facility': 0.19480519480519481, 'Outside Power Plant': [7.43801652892562, 60], 'Outside Restaurant': [7.43801652892562, 60], 'Outside Ruined Bridge': 0.9433962264150945, 'Outside Runway': 2.479338842975207, 'Inside School': [1.3043478260869565, 1], 'Outside School': [12.396694214876034, 60], 'Outside Shoe Shop': [2.0000000000000004, 5], 'Inside Shrine': [11.059907834101384, 120], 'Outside Shrine': [7.43801652892562, 60], 'Inside Skyscraper': [8.035714285714285, 15], 'Outside Skyscraper': [6.870229007633586, 60], 'Inside Slum': [1.4035087719298245, 8], 'Outside Slum': [7.43801652892562, 60], 'Outside Sporting Goods Store': [4.958677685950414, 60], 'Inside Stadium': [0.9230769230769231, 4], 'Outside Stadium': [7.317073170731707, 60], 'Inside Supermarket': [0.4166666666666667, 1], 'Outside Supermarket':[7.43801652892562, 60], 'Inside Synagogue': [11.009174311926607, 120], 'Outside Synagogue': [7.43801652892562, 60], 'Inside University': [0.625,1], 'Outside University': [12.396694214876034, 60], 'Outside Warehouse': [2.479338842975207, 60], 'Inside Zoo': [3.278688524590164, 10], 'Outside Zoo': [11.71875, 60]}}
    for item in pants:
        itemName = item
        insideItemDict = {}
        outsideItemDict = {}
        for k, v in pants[item].items():
            if k.startswith('Inside '):
                insideItemDict[k.split(' ', 1)[1]] = v
            else:
                outsideItemDict[k.split(' ', 1)[1]] = v
        print(f'~~~ {itemName}~~~')
        print('')
        print('{|style="text-align:center; border-collapse:collapse" border="1px" class="sortable"')
        print('|-style="background:#4E387E; color:white"')
        print('|+ Inside')
        print('!style="width:150px"|Location')
        print('!style="width:10px"|Find Weight')
        print('!style="width:10px"|% Chance')
        print('!style="width:10px"|% Chance / AP')


if __name__ == "__main__":
    with open('perItemSearchRates.json', 'w') as json_file:
        json.dump(masterOutput(), json_file)
    #print(masterOutput())
    #testData = wikiOutTest()
    #print(testData)
    #masterOutput()
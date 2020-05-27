import json

masterItemRates = {}
with open('perItemSearchRates.json') as json_file:
     masterItemRates = json.load(json_file)

def wikiOutParse(masterItemRates):
    for item in masterItemRates:
        itemName = item
        insideOutput = []
        outsideOutput = []
        insideItemDict = {}
        outsideItemDict = {}
        for k, v in masterItemRates[item].items():
            if k.startswith('Inside '):
                insideItemDict[k.split(' ', 1)[1]] = v
            else:
                outsideItemDict[k.split(' ', 1)[1]] = v
        if insideItemDict:
            insideOutput.append('{|style="text-align:center; border-collapse:collapse" border="1px" class="sortable"\n')
            insideOutput.append('|-style="background:#4E387E; color:white"\n')
            insideOutput.append('|+ Inside\n')
            insideOutput.append('!style="width:150px"|Location\n')
            insideOutput.append('!style="width:10px"|Find Weight\n')
            insideOutput.append('!style="width:10px"|% Chance\n')
            insideOutput.append('!style="width:10px"|% Chance / AP\n')
            for location in insideItemDict.items():
                insideOutput.append('|-\n')
                insideOutput.append(f'| [[{location[0]}]] || {location[1][1]} || {round(location[1][2], 2)} || {round(location[1][0], 2)}\n')
            insideOutput.append('|}\n')
        if outsideItemDict:
            insideOutput.append('{|style="text-align:center; border-collapse:collapse" border="1px" class="sortable"\n')
            insideOutput.append('|-style="background:#4E387E; color:white"\n')
            insideOutput.append('|+ Outside\n')
            insideOutput.append('!style="width:150px"|Location\n')
            insideOutput.append('!style="width:10px"|Find Weight\n')
            insideOutput.append('!style="width:10px"|% Chance\n')
            insideOutput.append('!style="width:10px"|% Chance / AP\n')
            for location in insideItemDict.items():
                insideOutput.append('|-\n')
                insideOutput.append(f'| [[{location[0]}]] || {location[1][1]} || {round(location[1][2], 2)} || {round(location[1][0], 2)}\n')
            insideOutput.append('|}\n')
        with open('wikiItemTables.txt', 'a') as file:
            file.write(f'~~~ {itemName}~~~\n')
            file.write('\n')
            for line in insideOutput:
                file.write(line)
            file.write('\n')
            for line in outsideOutput:
                file.write(line)

print('Writing item tables to file...')
wikiOutParse(masterItemRates)
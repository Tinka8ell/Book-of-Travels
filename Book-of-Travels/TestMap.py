'''
Created on 28 Dec 2021

@author: Tinka
'''

from Map.BotMap import BotMap
from Map.BotLookup import BotLookup
#from Map.HtmlTemplate import HtmlTemplate

if __name__ == '__main__':
    '''
    Old map:
    botMap = BotMap("BoT Routes.csv")
    print(botMap)

    botMap = BotMap("Map/BoT Routes.csv")
    ### print(botMap)

    mapDir = "/Users/marki/Pictures/Book of Travels/Maps"
    lookup = BotLookup(mapDir)

    for location in botMap.getLocations():
        name = location.name
        key = lookup.Location2Key(location)
        print(location.name, lookup.Location2Key(location), lookup.Location2FileName(location))
        print(name, lookup.Name2Key(name), lookup.Name2FileName(name))
        print(name, key, lookup.Key2FileName(key))
    '''

    botMap = BotMap("Map/BoT Routes.csv", "/Users/marki/Pictures/Book of Travels/Maps")
    key = "crossings"
    key = "batsaha"
    key = "alkenrockcoast"
    '''
    htmlFileName = key + ".html"
    botMap.AddLookup(lookup) # so we can use the names rather than indexes
    name = lookup.Key2Name(key)
    mapName = lookup.Key2FileName(key)
    imageDir = mapDir + "/"

    location = botMap.getLocation(key)
    if isinstance(location, str):
        print("Using key:", key, "Location is", location)
    else:
        template = HtmlTemplate('location')
        directions = location.getDirections()
        direction = []
        top = []
        left = []
        spoiler = []
        url = []
        for key in directions.keys():
            ### print("Processing direction:", key, "-", directions[key])
            destination = location.getDestination(key)
            direction.append(key)
            left.append(f'{directions[key][0] / 1265:.1%}')
            top.append(f'{directions[key][1] / 755:.1%}')
            spoilerText = ""
            if destination is None:
                spoiler.append(spoilerText)
                url.append("#") # just to complete the href
            else:
                if destination.spoiler:
                    spoilerText = "spoiler"
                spoiler.append(spoilerText)
                address = lookup.Name2Key(destination.location.name) # where we go to
                url.append(address + '?Entry=' + destination.direction) # appended the direction
        spoilers = location.spoilers # notes about spoilers if any
        noSpoilers = "hidden"
        if len(spoilers) > 0:
            noSpoilers = "" # don't hide as there are ...
        params = {
            'direction': direction,
            'top': top,
            'left': left,
            'url': url,
            'spoiler': spoiler,
            'spoilers': spoilers,
            'noSpoilers': noSpoilers,
            'name': name,
            'mapName': mapName,
            'imageDir': imageDir
            }
        html = template.generate(**params)
    html = botMap.GenerateHTML(key)
    with open(htmlFileName, "w") as htmlFile:
        print(html, file=htmlFile)
    htmlFileName = botMap.GenerateHtmlFile(key)
    print("Done: ", htmlFileName)
    '''
    botMap.GenerateHtmlFiles()
    print("Done all")
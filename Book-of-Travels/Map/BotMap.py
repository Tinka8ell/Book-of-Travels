'''
Created on 28 Dec 2021

@author: Tinka
'''

from csv import DictReader
from Map.BotLookup import BotLookup
from Map.HtmlTemplate import HtmlTemplate

class Location():

    def __init__(self, name):
        '''
        A location is a named place with routes.
        Routes are destinations keyed on direction
        '''
        self.name = name
        self.routes = dict()
        self.coords = dict()
        self.spoilers = []
        return

    def getDirections(self):
        return self.coords

    def getDestination(self, direction):
        return self.routes.get(direction, None)

    def addRoute(self, direction, coords, destination):
        oldDestination = self.getDestination(direction)
        if oldDestination is None: # good as not there ... (not indexed or no destination)
            self.routes[direction] = destination
            self.coords[direction] = coords
        else:
            if oldDestination != destination:
                message = "For location: " + self.name
                message += ", direction: " + direction
                message += " trying to add another route (" + str(destination)
                message += ") when already has one (" + str(oldDestination) + ")"
                raise Exception(message)
        return

    def __str__(self):
        value = self.name + "("
        destinations = self.routes.keys()
        if len(destinations) > 0:
            for direction in destinations:
                x, y = self.coords[direction]
                value += direction + " ("
                value += str(x) + ", " + str(y) + "): "
                value += str(self.routes[direction]) + ", "
            value = value[:-2] # remove trailing comma
        else:
            value += "no routes"
        return value + ")"

    def GenerateHTML(self, lookup):
        ### print("Location.GenertateHTML()")
        template = HtmlTemplate('location')
        directions = self.getDirections()
        direction = []
        top = []
        left = []
        spoiler = []
        url = []
        for key in directions.keys():
            ### print("Processing direction:", key, "-", directions[key])
            destination = self.getDestination(key)
            direction.append(key)
            left.append(f'{directions[key][0] / 1265:.1%}')
            top.append(f'{directions[key][1] / 755:.1%}')
            spoilerText = ""
            if destination is None:
                url.append("#") # stay where we are link!
                spoilerText = "spoiler" # and treat it as a spoiler
            else:
                if destination.spoiler:
                    spoilerText = "spoiler"
                address = lookup.Name2Key(destination.location.name) # where we go to
                url.append(address + '.html?Entry=' + destination.direction) # appended the direction
            spoiler.append(spoilerText)
        spoilers = self.spoilers # notes about spoilers if any
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
            'name': self.name,
            'mapName': lookup.Name2FileName(self.name),
            'imageDir': lookup.imageDir
            }
        html = template.generate(**params)
        '''
        test = html
        if test is not None:
            test = str(len(test)) + " bytes"
        print("Location.GenertateHTML returns:", test)
        '''
        return html

    def Merge(self, location):
        raise Exception("Not written yet!")
        return


class Destination():

    def __init__(self, location, direction, spoiler=False):
        '''
        A destination is a direction from a location
        '''
        self.location = location
        self.direction = direction
        self.spoiler = spoiler
        return

    def __str__(self):
        value = self.location.name + " - " + self.direction
        if self.spoiler:
            value += " (Spoiler)"
        return value


class BotMap(object):
    '''
    Book of Travels Map.
    The map consists of locations which have:
        a name,
        at least one node
    It also holds routes which
        connect one node to another in a direction.
    In theory the routes should have a reciprocal route back, but it is not guaranteed.
    '''
    def __init__(self, csvFilename=None, lookup=None):
        '''
        Constructor
        Basic constructor takes the filename of a CSV file containing the information.
        Each row:
            id (numeric)
            name
            direction (node id)
            route:
                location id
                location node id
        Where information is the same as the previous row it can be skipped (id and name).
        '''
        self.lookup = None
        self.locations = dict() # location id to location
        routesToAdd = []
        with open(csvFilename) as csvfile:
            csvReader = DictReader(csvfile, restkey="Rest")
            # Number,Name,Direction,To,Entry,Rest
            location = None
            locIndex = 0
            for row in csvReader:
                num = row["Number"]
                loc = row["Name"]
                if num != "": # have new location
                    location = Location(loc)
                    locIndex = num
                    self.locations[locIndex] = location
                direction = row["Direction"]
                x = int(row["X"])
                y = int(row["Y"])
                spoiler = (row["Spoiler"] != "")
                note = row["Note"]
                if spoiler and (note != ""):
                    if note not in location.spoilers:
                        location.spoilers.append(note)
                dest = (row["To"], row["Entry"])
                if row["To"] == "": # if no destination
                    dest = None
                ### print("Adding:", ((locIndex, direction), dest))
                routesToAdd.append(((locIndex, direction, (x,y)), dest, spoiler)) # so we can sort out later
        # here with all locations created to add all routes
        for fromLocation, toLocation, spoiler in routesToAdd:
            index, direction, coords = fromLocation
            location = self.locations.get(index, None) #  find the from location
            if location is None:
                message = "Big error as index: '" + index
                message += "' not found in locations for route to add: " + str(fromLocation)
                message += " - " + str(toLocation)
                raise Exception(message)
            destination = None # default to not there
            if toLocation is not None:
                index, receivingDirection = toLocation
                loc = self.locations.get(index, None) #  find the to location
                if loc is None:
                    message = "Small error as destination index: '" + index
                    message += "' not found in locations for route to add: " + str(fromLocation)
                    message += " - " + str(toLocation)
                    raise Exception(message)
                destination = Destination(loc, receivingDirection, spoiler)
            location.addRoute(direction, coords, destination)
        if (lookup is not None):
            self.AddLookup(lookup)
        return

    def AddLookup(self, lookup):
        # add look up for names etc and replace the dictionary keys with the location keys
        if not isinstance(lookup, BotLookup):
            lookup = BotLookup(lookup)
        self.lookup = lookup
        locations = dict()
        for key in self.locations.keys():
            location = self.locations[key]
            shortName = self.lookup.Name2Key(location.name)
            locations[shortName] = location
            ### print(key, location.name)
        self.locations = locations
        return

    def getLocation(self, key):
        return self.locations.get(key, "Not Found")

    def Merge(self, botmap):
        for key in botmap.keys():
            if key in self.locations.keys():
                self.locations[key].Merge(botmap.locations[key])
            else:
                raise Exception("Need to think this through ... as locations in botmap are not necessarily in us!")
                self.locations[key] = botmap.locations[key]
        return

    def getLocations(self):
        return list(self.locations.values())

    def __str__(self):
        value = "All locations: "
        if len(self.locations.keys()) > 0:
            for location in self.locations.keys():
                value += "\n   " + str(self.locations[location])
        else:
            value += "   none"
        return value

    def GenerateHTML(self, shortName):
        ### print("GenertateHTML(", shortName, ")")
        html = None
        if self.lookup is not None:
            html = self.locations[shortName].GenerateHTML(self.lookup)
        '''
        test = html
        if html is not None:
            test = str(len(test)) + " bytes"
        print("GenertateHTML returns:", test)
        '''
        return html

    def GenerateHtmlFile(self, shortName):
        ### print("GenertateHtmlFiles(", shortName, ")")
        filename = None
        html = self.GenerateHTML(shortName)
        if html is not None:
            filename = shortName + ".html"
            with open(filename, "w") as htmlFile:
                print(html, file=htmlFile)
        '''
            print("GenertateHtmlFiles create file:", filename)
        else:
            print("GenertateHtmlFiles create nothing")
        '''
        return filename

    def GenerateHtmlFiles(self):
        for shortName in self.locations.keys():
            self.GenerateHtmlFile(shortName)
        return


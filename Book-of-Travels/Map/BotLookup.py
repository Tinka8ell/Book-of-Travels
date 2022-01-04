'''
Created on 29 Dec 2021

@author: Tinka
'''

from pathlib import Path
from re import findall


class BotLookup(object):
    '''
    classdocs
    '''


    def __init__(self, mapDirectory):
        '''
        Using a BotMap and a directory of maps create look ups:
            Location -> map file name
            Location -> short name (remove spaces and punctuation)
        '''

        self.fileNames = dict()
        self.pathNames = dict()
        self.names = dict()
        self.shortNames = dict()

        p = Path(mapDirectory)
        ### print("For directory:", p)
        for x in p.iterdir():
            ### print(x)
            filename = x.name
            pos = filename.find(".")
            name = filename[pos+1: ]
            pos = name.find(".")
            name = name[:pos ]
            words = findall("\\w+", name)
            shortName = "".join(words).lower()
            self.shortNames[name] = shortName
            self.names[shortName] = name
            self.pathNames[shortName] = x
            self.fileNames[shortName] = filename
        '''
        for name in self.shortNames.keys():
            key = self.shortNames[name]
            print(name  + ": " + key + " - " + str(self.fileNames[key]) + " - " + str(self.pathNames[key]))
        '''
        self.imageDir = Path(p, "X").as_posix()[:-1] # get a directory prefix
        return

    def Key2Name(self, key):
        return self.names[key]

    def Name2Key(self, name):
        return self.shortNames[name]

    def Location2Key(self, location):
        return self.Name2Key(location.name)

    def Key2FileName(self, key):
        return self.fileNames[key]

    def Key2PathName(self, key):
        return self.pathNames[key]

    def Name2FileName(self, name):
        return self.Key2FileName(self.Name2Key(name))

    def Name2PathName(self, name):
        return self.Key2PathName(self.Name2Key(name))

    def Location2FileName(self, location):
        return self.Key2FileName(self.Location2Key(location))

    def Location2PathName(self, location):
        return self.Key2PathName(self.Location2Key(location))


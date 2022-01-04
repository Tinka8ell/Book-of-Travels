'''
Created on 28 Dec 2021

@author: Tinka
'''

from Map.BotMap import BotMap

if __name__ == '__main__':
    botMap = BotMap("maps/BoT Routes.csv", "maps")
    botMap.GenerateHtmlFiles()
    print("Done all")
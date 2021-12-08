#!/usr/bin/env python3
from psnawp_api import psnawp
from pypresence import Presence
import configparser
import time
import ast
import logging
import os
import datetime


def discordrpc(appid):
    global rpc
    rpc.clear()
    rpc = Presence(appid, pipe=0)
    rpc.connect()

def setupLogging():
    if currentOS == "NT":
        logfile = config["system"]["NTLogFile"]
    else:
        logfile = config["system"]["POSTXLogFile"]
    loglevelint = getattr(logging, config["system"]["LogLevel"].upper(), "INFO")
    print(loglevelint)
    logging.basicConfig(filename=logfile, level=loglevelint)


currentOS = os.name


config = configparser.ConfigParser()
config.read('playstationpresence.ini')
npsso = config['main']['npsso']
PSNID = config['main']['PSNID']
gameart = config['main']['gameArt']

PS4OnPS5 = config['tokens']['PS4OnPS5']
PS5 = config['tokens']['PS5']
PS4 = config['tokens']['PS4']


psnawp = psnawp.PSNAWP(npsso)
start_time = int(time.time())
oldpresence = ""
#Initial usage, used to clear status if user is offline
rpc = Presence(PS4,pipe=0)
rpc.connect()
setupLogging()
logging.info(f'Starting up at {datetime.datetime.now()}')
while True:
    user_online_id = psnawp.user(online_id=PSNID)
    print(type(user_online_id.get_presence()))
    mainpresence = user_online_id.get_presence()
    print(mainpresence) #Uncomment this to get info about games inc. artwork/gameid links
    start_time = int(time.time())
    if 'offline' in mainpresence:
        logging.info("User is offline, clearing status")
        print("User is offline, clearing status")
        rpc.clear()
    else: 
        if (oldpresence == mainpresence):
            pass
        else:
            #Best way to work with backwards compatability is a seprate rpclient named Playstation 5 with PS4 game assets
            if 'PS5' in mainpresence:
                system = "ps5"
                if 'CUSA' in mainpresence:
                    discordrpc(PS4OnPS5) #PS4 games on PS5
                else:
                    discordrpc(PS5) #PS5 games
            else:
                system = "ps4"
                discordrpc(PS4)
            current = str(mainpresence).split("'")
            print(current)
            if (len(current) == 19): #Length of this is 19 if user is not in a game
                rpc.update(state="Idling", start=start_time, small_image=system, small_text=PSNID, large_image=system, large_text="Homescreen")
                logging.info(f'Idleing')
                print("Idling")
            else:
                if 'gameStatus' in mainpresence: #Not every game supports gameStatus
                    gametext = current[39]
                else:
                    gametext = current[27]
                if gameart == "yes":
                    if 'conceptIconUrl' in mainpresence['gameTitleInfoList'][0]:
                        gameid = mainpresence['gameTitleInfoList'][0]["conceptIconUrl"]
                    elif "npTitleIconUrl" in mainpresence['gameTitleInfoList'][0]:
                        gameid = mainpresence['gameTitleInfoList'][0]["npTitleIconUrl"]
                        print()
                else:
                    gameid = system
                gamename = current[27]
                #gamestatus = current[]
                rpc.update(state=gamename, start=start_time, small_image=system, small_text=PSNID, large_image=gameid, large_text=gametext)
                logging.info(f"Playing {gamename}")
                print(f"Playing {gamename}")
    time.sleep(20) #Adjust this to be higher if you get ratelimited

    oldpresence = mainpresence


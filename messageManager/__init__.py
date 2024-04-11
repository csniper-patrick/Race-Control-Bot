from discordwebhook import Discord
import json
import re
import copy

from .utils import *

class messageManager:
    
    from .RaceControlMessages import liveRaceControlMessagesHandler
    from .TimingDataF1 import liveTimingDataF1Handler
    from .TyreStintSeries import liveTyreStintSeriesHandler
    from .PitLaneTimeCollection import livePitLaneTimeCollectionHandler
     
    def __init__(self, webhook, raceDirector="Race Director", tag=None, msgStyle={}):
        self.discord = Discord(url=webhook)
        if tag is not None:
            self.tag=f" [{tag}]"
        else:
            self.tag=""
        self.streamHandlers={
            "TrackStatus": self.liveTrackStatusHandler,
            "RaceControlMessages": self.liveRaceControlMessagesHandler,
            "TimingAppData": self.liveTimingAppDataHandler,
            "TimingStats": self.liveTimingStatsHandler,
            "DriverList": self.liveDriverListHandler,
            "SessionInfo": self.liveSessionInfoHandler,
            "TyreStintSeries": self.liveTyreStintSeriesHandler,
            "TimingDataF1" : self.liveTimingDataF1Handler,
            "PitLaneTimeCollection": self.livePitLaneTimeCollectionHandler, 
        }
        self.raceDirector=raceDirector
        self.msgStyle={
            "flagColor": {
				"GREEN": 5763719,
				"CLEAR": 5763719,
				"YELLOW": 16776960,
				"DOUBLE YELLOW": 16776960, 
				"CHEQUERED": 16777215,
				"BLUE": 3447003,
				"RED": 15548997	,
				"BLACK AND WHITE": 16777215,
				"BLACK AND ORANGE": 15105570,
				"BLACK": 2303786
        	},
            "flagSymbol":{ 
				"CHEQUERED": ":checkered_flag:",
				"BLACK": ":flag_black:"
			},
        	"modeColor": {
				"SAFETY CAR": 15844367,
				"VIRTUAL SAFETY CAR": 15844367
        	},
            "compoundColor": {
				"SOFT": 15548997, # RED
				"MEDIUM": 16776960, # YELLOW
				"HARD": 16777215, # WHITE
				"INTERMEDIATE": 2067276, # GREEN
				"WET": 2123412, # BLUE
        	},
            "compoundSymbol": {}
		}
        self.msgStyle = updateDictDelta(self.msgStyle, msgStyle)
        return
    
    def updateReference(self, msg):
        if "DriverList" in msg:
            self.driverList=msg["DriverList"]
        if "SessionInfo" in msg:
            self.sessionInfo=msg["SessionInfo"]
        if "TimingStats" in msg:
            self.timingStats=msg["TimingStats"]
        if "TimingAppData" in msg:
            self.timingAppData=msg["TimingAppData"]
        if "TyreStintSeries" in msg:
            self.tyreStintSeries=msg["TyreStintSeries"]
        if "TimingDataF1" in msg:
            self.timingDataF1=msg["TimingDataF1"]
    
    def pushDriverList(self):
        for number, info in self.driverList.items():
            if type(info) is not dict: 
                continue 
            self.discord.post(
                username=f"{info['Tla']} - {info['RacingNumber']}",
                embeds=[
                    {
                        "fields": [
                            {"name": key, "value": info[key], "inline": True}
                            for key in ["FullName", "TeamName", "CountryCode"]
                        ],
                        "color": int(info['TeamColour'], 16),
                    }
                ],
                avatar_url=info["HeadshotUrl"] if "HeadshotUrl" in info else None
            )
            
        return

    def liveDriverListHandler(self, msg):
        driverList = msg["A"][1]
        self.driverList=updateDictDelta(self.driverList, driverList)
        return
    
    def liveSessionInfoHandler(self, msg):
        sessionInfo = msg["A"][1]
        self.sessionInfo=updateDictDelta(self.sessionInfo, sessionInfo)
        return

    def liveTrackStatusHandler(self, msg):
        return
    
    def liveTimingStatsHandler(self, msg):
        self.timingStats = updateDictDelta(self.timingStats, msg["A"][1])
        return

    def liveTimingAppDataHandler(self, msg):
        compoundColor=self.msgStyle["compoundColor"]
        self.timingAppData = updateDictDelta(self.timingAppData, msg["A"][1])
        return
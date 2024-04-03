from discordwebhook import Discord
import json
import re
import copy
class messageManager:
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

    def liveRaceControlMessagesHandler(self, msg):
        flagColor=self.msgStyle["flagColor"]
        flagSymbol=self.msgStyle["flagSymbol"]
        modeColor=self.msgStyle["modeColor"]
        RCMessages=msg["A"][1]["Messages"]
        if type(RCMessages) == dict :
            RCMessages=[
                value
                for key, value in RCMessages.items()
            ]
        
        # skip messaging if session is archived
        if self.sessionInfo["ArchiveStatus"]["Status"] == "Complete":
            return
        
        for content in RCMessages:
            if "Flag" in content and content["Flag"] == "BLUE":
                continue;
            if "Flag" in content and content["Flag"] in flagSymbol:
                content["Message"] = f"{flagSymbol[content['Flag']]}{content['Message']}"
            self.discord.post(
                username=f"{self.raceDirector}{self.tag}",
                embeds=[
                    {
                        "title": content["Message"],
                        "fields": [
                            { "name": key, "value": value, "inline": True }
                            for key, value in content.items() if key in ["Mode", "Status"]
                        ],
                        "color": flagColor[content["Flag"]] if "Flag" in content and content["Flag"] in flagColor else
                         modeColor[content["Mode"]] if "Mode" in content and content["Mode"] else None,
                    }
                ]
            )
    
    def livePitLaneTimeCollectionHandler(self, msg):
        if not self.sessionInfo["Type"] in ["Race", "Sprint"]:
            return
        pitLaneTimeCollection = msg["A"][1]["PitTimes"]
        
        # skip messaging if session is archived
        if self.sessionInfo["ArchiveStatus"]["Status"] == "Complete":
            return
        
        for RacingNumber, pitLaneTime in pitLaneTimeCollection.items():
            if not RacingNumber in self.driverList:
                continue
            durationSec=reversed([ float(i) for i in re.split(':', pitLaneTime["Duration"]) ])
            durationSec=sum([ val * scaler for val, scaler in zip( durationSec, [1, 60] ) ])
            if durationSec >= 30.0:
                info = self.driverList[RacingNumber]
                self.discord.post(
                    username=f"{info['TeamName']}{self.tag}",
                    embeds=[
                        {
                            "title": f"Slow Pit Stop - {pitLaneTime['Duration']} in pit lane",
                            "fields": [
                                {"name": "Driver", "value": info['FullName'], "inline": True},
                            ],
                            "color": int(info['TeamColour'], 16),
                        }
                    ],
                )
    
    def liveTimingStatsHandler(self, msg):
        self.timingStats = updateDictDelta(self.timingStats, msg["A"][1])
        return

    def liveTimingAppDataHandler(self, msg):
        compoundColor=self.msgStyle["compoundColor"]
        self.timingAppData = updateDictDelta(self.timingAppData, msg["A"][1])
        return
    
    def liveTimingDataF1Handler(self, msg):
        compoundSymbol=self.msgStyle["compoundSymbol"]
        self.timingDataF1 = updateDictDelta(self.timingDataF1, msg["A"][1])
        
        # skip messaging if session is archived
        if self.sessionInfo["ArchiveStatus"]["Status"] == "Complete":
            return
        
        for RacingNumber, stat in msg["A"][1]["Lines"].items():
            info = self.driverList[RacingNumber]
            if (
                "BestLapTime" in stat
                and "LastLapTime" in stat
                and "PersonalFastest" in stat["LastLapTime"]
                and stat["LastLapTime"]["PersonalFastest"] == True
			):
                # Get current tyre compound
                currentStint=self.tyreStintSeries['Stints'][RacingNumber][-1]
                if currentStint['Compound'] in compoundSymbol:
                    currentCompound = f"{compoundSymbol[currentStint['Compound']]}{currentStint['Compound']}"
                else:
                    currentCompound = currentStint['Compound']
                
				# Get personal best lap time 
                if type( self.timingDataF1["Lines"][RacingNumber]["BestLapTime"] ) == dict:
                    # Not qualifying
                    BestLapTime = self.timingDataF1["Lines"][RacingNumber]["BestLapTime"]["Value"]
                elif type( self.timingDataF1["Lines"][RacingNumber]["BestLapTime"] ) == list:
                    # qualifying
                    BestLapTime = self.timingDataF1["Lines"][RacingNumber]["BestLapTime"][self.timingDataF1["SessionPart"] - 1]["Value"]
                
				# skip if time is empty
                if BestLapTime == "":
                    continue
                
                if (
                    "OverallFastest" in stat["LastLapTime"]
					and stat["LastLapTime"]["OverallFastest"] == True
				):
                    # Quickest Overall
                    self.discord.post(
                        username=f"{info['Tla']} - {info['RacingNumber']}{self.tag}",
                        embeds=[
                            {
                                "title": f"Quickest Overall - {BestLapTime}",
                                "fields": [
                                    {
                                        "name": "Sectors",
                                        "value": "".join([
                                            "\U0001F7EA" if sector["OverallFastest"] else # purple square emoji
                                            "\U0001F7E9" if sector["PersonalFastest"] else # green square emoji
                                            "\U0001F7E8" # yellow square emoji
                                            for sector in self.timingDataF1["Lines"][RacingNumber]["Sectors"]
                                        ]),
                                        "inline": True
                                    },
                                    {
                                        "name": "Tyre",
                                        "value": f"{currentCompound} (age: {currentStint['TotalLaps']})",
                                        "inline": True
                                    },
                                ],
                                "color": 10181046 #Purple
                            }
                        ],
                        avatar_url=info["HeadshotUrl"] if "HeadshotUrl" in info else None
                    )
                elif (
                    self.sessionInfo["Type"] in ["Qualifying", "Sprint Shootout"]
				):
                    # Personal Best
                    self.discord.post(
                        username=f"{info['Tla']} - {info['RacingNumber']}{self.tag}",
                        embeds=[
                            {
                                "title": f"Personal Best - {BestLapTime}",
                                "fields": [
                                    {
                                        "name": "Sectors",
                                        "value": "".join([
                                            "\U0001F7EA" if sector["OverallFastest"] else
                                            "\U0001F7E9" if sector["PersonalFastest"] else
                                            "\U0001F7E8"
                                            for sector in self.timingDataF1["Lines"][RacingNumber]["Sectors"]
                                        ]),
                                        "inline": True
                                    },
                                    {
                                        "name": "Tyre",
                                        "value": f"{currentCompound} (age: {currentStint['TotalLaps']})",
                                        "inline": True
                                    },
                                ],
                                "color": 5763719 #Green
                            }
                        ],
                        avatar_url=info["HeadshotUrl"] if "HeadshotUrl" in info else None
                    )
            
            # Knocked Out of Qualifying
            if (
                self.sessionInfo["Type"] in ["Qualifying", "Sprint Shootout"] and
                "KnockedOut" in stat and 
                stat["KnockedOut"] == True
            ):
                self.discord.post(
                    username=f"{info['Tla']} - {info['RacingNumber']}{self.tag}",
                    embeds=[
                        {
                            "title": f"Knocked Out - P{self.timingDataF1['Lines'][RacingNumber]['Position']}",
                            "color": int(info['TeamColour'], 16),
                        }
                    ],
                    avatar_url=info["HeadshotUrl"] if "HeadshotUrl" in info else None
                )
            
            # Retired
            if (
                "Retired" in stat and 
                stat["Retired"] == True
            ):
                self.discord.post(
                    username=f"{info['Tla']} - {info['RacingNumber']}{self.tag}",
                    embeds=[
                        {
                            # "title": f"Retired - Lap {self.timingDataF1['Lines'][RacingNumber]['NumberOfLaps'] + 1}",
                            "title": f"Retired{ (' - Lap ' + str(self.timingDataF1['Lines'][RacingNumber]['NumberOfLaps'] + 1) )if 'NumberOfLaps' in self.timingDataF1['Lines'][RacingNumber] else '' }",
                            "color": int(info['TeamColour'], 16),
                        }
                    ],
                    avatar_url=info["HeadshotUrl"] if "HeadshotUrl" in info else None
                )
            
            # Race Leader
            if (
                self.sessionInfo["Type"] in ["Race", "Sprint"] and
                "Position" in stat and 
                stat["Position"] == "1"
            ):
                self.discord.post(
                    username=f"{info['Tla']} - {info['RacingNumber']}{self.tag}",
                    embeds=[
                        {
                            "title": f"Race Leader - {info['FullName']}",
                            "fields": [
                                {"name": "TeamName", "value": info["TeamName"], "inline": True},
                            ],
                            "color": int(info['TeamColour'], 16),
                        }
                    ],
                    avatar_url=info["HeadshotUrl"] if "HeadshotUrl" in info else None
                )
            
        return
    
    def liveTyreStintSeriesHandler(self, msg):
        compoundColor=self.msgStyle["compoundColor"]
        compoundSymbol=self.msgStyle["compoundSymbol"]
        prevFrame = copy.deepcopy(self.tyreStintSeries)
        self.tyreStintSeries = updateDictDelta(self.tyreStintSeries, msg["A"][1])
        
        # skip messaging if session is archived
        if self.sessionInfo["ArchiveStatus"]["Status"] == "Complete":
            return
        
        if self.sessionInfo["Type"] not in ["Race", "Sprint"]:
            return
        for RacingNumber, driverStints in self.tyreStintSeries["Stints"].items():
            if ( RacingNumber not in self.driverList or len(driverStints) == 0 ):
                continue
            info = self.driverList[RacingNumber]
            currentStint = driverStints[-1]
            if currentStint['Compound'] in compoundSymbol:
                currentCompound = f"{compoundSymbol[currentStint['Compound']]}{currentStint['Compound']}"
            else:
                currentCompound = currentStint['Compound']
            # announce tyre change if necessary
            if ( len(driverStints) > len(prevFrame['Stints'][RacingNumber]) ):
                # case 1 new stints
                self.discord.post(
					username=f"{info['Tla']} - {info['RacingNumber']}{self.tag}",
					embeds=[
						{
							"title": f"Tyre Change - { currentCompound }",
							"fields": [
								{"name": "Stint", "value": len(driverStints), "inline": True},
								{"name": "Age", "value": currentStint["StartLaps"], "inline": True},
							],
							"color": compoundColor[currentStint["Compound"]] if "Compound" in currentStint and currentStint["Compound"] in compoundColor else None,
						}
					],
					avatar_url=info["HeadshotUrl"] if "HeadshotUrl" in info else None
				)
            elif( len(driverStints) == len(prevFrame['Stints'][RacingNumber]) and currentStint['Compound'] != prevFrame['Stints'][RacingNumber][-1]['Compound'] ):
            	# case 2 compound update
                self.discord.post(
					username=f"{info['Tla']} - {info['RacingNumber']}{self.tag}",
					embeds=[
						{
							"title": f"Compound - { currentCompound } (Updated)",
							"fields": [
								{"name": "Stint", "value": len(driverStints), "inline": True},
								{"name": "Age", "value": currentStint["StartLaps"], "inline": True},
							],
							"color": compoundColor[currentStint["Compound"]] if "Compound" in currentStint and currentStint["Compound"] in compoundColor else None,
						}
					],
					avatar_url=info["HeadshotUrl"] if "HeadshotUrl" in info else None
				)
        return

def updateDictDelta(obj, delta):
    for key, value in delta.items():
        if key not in obj:
            obj[key] = value
        elif type(value) == dict and type(obj[key]) == dict:
            obj[key] = updateDictDelta(obj[key], value)
        elif (
            type(value) == dict and type(obj[key]) == list
            and all([ k.isnumeric() for k in value.keys()])
        ):
            tempDict = dict(
                [
                    (str(idx), value)
                    for idx, value in enumerate(obj[key])
                ]
            )
            tempDict = updateDictDelta(tempDict, value)
            obj[key] = [
                value
                for _, value in tempDict.items()
            ]
        else:
            obj[key] = value
    return obj

def timeStr2msec(timeStr: str):
    return sum([ val * scaler for val, scaler in zip( reversed([ float(i) for i in re.split(':', timeStr) ]), [1, 60] ) ]) * 1000

def msec2timeStr(msec: int, signed: bool = False):
    val = int(abs(msec))
    if signed:
        timeStr = "+" if msec >= 0 else "-"
    else:
        timeStr = "" if msec >= 0 else "-"
    if val >= 60000:
        timeStr += str( val // 60000 ) + ":"
        val %= 60000
    timeStr+= str(val // 1000)
    timeStr+= "." + str(val % 1000).zfill(3)
    return timeStr
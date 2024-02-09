from discordwebhook import Discord
import json
class messageManager:
    def __init__(self, webhook, tag=None):
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
        flagColor={
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
        }
        modeColor={
            "SAFETY CAR": 15844367,
            "VIRTUAL SAFETY CAR": 15844367
        }
        RCMessages=msg["A"][1]["Messages"]
        if type(RCMessages) == dict :
            RCMessages=[
                value
                for key, value in RCMessages.items()
            ]
        for content in RCMessages:
            if "Flag" in content and content["Flag"] == "BLUE":
                continue;
            if "Flag" in content and content["Flag"] == "CHEQUERED":
                content["Message"] = f"{content['Message']}\U0001F3C1"
            self.discord.post(
                username=f"Mikey Masi{self.tag}",
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
        pitLaneTimeCollection = msg["A"][1]["PitTimes"]
        for RacingNumber, pitLaneTime in pitLaneTimeCollection.items():
            if RacingNumber in self.driverList:
                info = self.driverList[RacingNumber]
                self.discord.post(
                    username=f"{info['TeamName']}{self.tag}",
                    embeds=[
                        {
                            "title": f"Pit Stop - {info["FullName"]}",
                            "fields": [
                                {"name": "Duration", "value": pitLaneTime["Duration"], "inline": True},
                                {"name": "Lap",   "value": pitLaneTime['Lap'], "inline": True}
                            ],
                            "color": int(info['TeamColour'], 16),
                        }
                    ],
                )
    
    def liveTimingStatsHandler(self, msg):
        self.timingStats = updateDictDelta(self.timingStats, msg["A"][1])
        return

    def liveTimingAppDataHandler(self, msg):
        compoundColor={
            "SOFT": 15548997, # RED
            "MEDIUM": 16776960, # YELLOW
            "HARD": 16777215, # WHITE
            "INTERMEDIATE": 2067276, # GREEN
            "WET": 2123412, # BLUE
        }
        self.timingAppData = updateDictDelta(self.timingAppData, msg["A"][1])
        return
    
    def liveTimingDataF1Handler(self, msg):
        self.timingDataF1 = updateDictDelta(self.timingDataF1, msg["A"][1])
        for RacingNumber, stat in msg["A"][1]["Lines"].items():
            info = self.driverList[RacingNumber]
            if(
                "LastLapTime" in stat and 
                "Value" in stat["LastLapTime"] and stat["LastLapTime"]["Value"] != ""
            ):
                # Lap time
                if ("OverallFastest" in stat["LastLapTime"] and 
                    stat["LastLapTime"]["OverallFastest"] == True
                ) :
                    # Quickest Overall
                    self.discord.post(
                        username=f"{info['Tla']} - {info['RacingNumber']}{self.tag}",
                        embeds=[
                            {
                                "title": f"Ouickest Overall - {stat['LastLapTime']['Value']}",
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
                                        "value": f"{self.tyreStintSeries["Stints"][RacingNumber][-1]['Compound']} (age: {self.tyreStintSeries["Stints"][RacingNumber][-1]['TotalLaps']})",
                                        "inline": True
                                    },
                                ],
                                "color": 10181046 #Purple
                            }
                        ],
                        avatar_url=info["HeadshotUrl"] if "HeadshotUrl" in info else None
                    )
                elif (
                    self.sessionInfo["Type"] in ["Qualifying", "Sprint Shootout"] and
                    "PersonalFastest" in stat["LastLapTime"] and 
                    stat["LastLapTime"]["PersonalFastest"] == True
                ):
                    # Personal Best
                    self.discord.post(
                        username=f"{info['Tla']} - {info['RacingNumber']}{self.tag}",
                        embeds=[
                            {
                                "title": f"Personal Best - {stat['LastLapTime']['Value']}",
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
                                        "value": f"{self.tyreStintSeries["Stints"][RacingNumber][-1]['Compound']} (age: {self.tyreStintSeries["Stints"][RacingNumber][-1]['TotalLaps']})",
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
                            "title": f"Knocked Out - P{self.timingDataF1["Lines"][RacingNumber]['Position']}",
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
                            "title": f"Retired - Lap {self.timingDataF1["Lines"][RacingNumber]['NumberOfLaps'] + 1}",
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
        compoundColor={
            "SOFT": 15548997, # RED
            "MEDIUM": 16776960, # YELLOW
            "HARD": 16777215, # WHITE
            "INTERMEDIATE": 2067276, # GREEN
            "WET": 2123412, # BLUE
        }
        lineStats = msg["A"][1]["Stints"]
        for RacingNumber, driverStints in lineStats.items():
            info = self.driverList[RacingNumber]
            if type(driverStints) == dict:
                stintsDict = dict(
                        [ (str(idx), stint) for idx, stint in enumerate( self.tyreStintSeries["Stints"][RacingNumber] ) ]
                    )
                stintsDict = updateDictDelta(stintsDict, driverStints)
                stintsList = [ stint for _, stint in stintsDict.items() ]
                currentStint = stintsList[-1]
                # announce tyre change if necessary
                if (
                    self.sessionInfo["Type"] in ["Race", "Sprint"] and
                    (
                        len(stintsList) > len(self.tyreStintSeries["Stints"][RacingNumber]) or
                        currentStint["Compound"] != self.tyreStintSeries["Stints"][RacingNumber][len(stintsList)-1]["Compound"]
                    ) and
                    currentStint["TyresNotChanged"] == "0"
                ):
                    self.discord.post(
                        username=f"{info['Tla']} - {info['RacingNumber']}{self.tag}",
                        embeds=[
                            {
                                "title": f"Tyre Change - {currentStint['Compound']}",
                                "fields": [
                                    {"name": "Stint", "value": len(stintsList), "inline": True},
                                    {"name": "Age", "value": currentStint["StartLaps"], "inline": True},
                                ],
                                "color": compoundColor[currentStint["Compound"]] if "Compound" in currentStint and currentStint["Compound"] in compoundColor else None,
                            }
                        ],
                        avatar_url=info["HeadshotUrl"] if "HeadshotUrl" in info else None
                    )
                self.tyreStintSeries["Stints"][RacingNumber] = stintsList
            elif type(driverStints) == list:
                # direct merge
                self.tyreStintSeries["Stints"][RacingNumber] = driverStints
        
        return

def updateDictDelta(obj, delta):
    for key, value in delta.items():
        if key not in obj:
            obj[key] = value
        elif type(value) == dict and type(obj[key]) == dict:
            obj[key] = updateDictDelta(obj[key], value)
        elif type(value) == list and type(obj[key]) == list:
            # obj[key] = updateListDelta(obj[key], value)
            obj[key] = value
        elif type(value) == dict and type(obj[key]) == list:
            tempDict=dict(
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

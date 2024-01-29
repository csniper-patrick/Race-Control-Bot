from discordwebhook import Discord
class messageManager:
    def __init__(self, webhook, tag=None):
        self.discord = Discord(url=webhook)
        if tag is not None:
            self.tag=f" [{tag}]"
        else:
            self.tag=""
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
        # Clear TimingStats
        timingStatsTemplate={
            "Line": 99,
            "PersonalBestLapTime": {
                "Lap": 99,
                "Position": 99,
                "Value": "9:59.999"
            },
            "BestSectors": [
                {
                    "Position": 99,
                    "Value": "59.999"
                },
                {
                    "Position": 99,
                    "Value": "59.999"
                },
                {
                    "Position": 99,
                    "Value": "59.999"
                }
            ],
            "BestSpeeds": {
                "I1": {
                    "Position": 99,
                    "Value": "999"
                },
                "I2": {
                    "Position": 99,
                    "Value": "999"
                },
                "FL": {
                    "Position": 99,
                    "Value": "999"
                },
                "ST": {
                    "Position": 99,
                    "Value": "999"
                }
            }
        }
        for RacingNumber, Stats in self.timingStats["Lines"].items():
            self.timingStats["Lines"][RacingNumber]=updateDictDelta(self.timingStats["Lines"][RacingNumber], timingStatsTemplate)
        return

    def liveTrackStatusHandler(self, msg):
        return

    def liveRaceControlMessagesHandler(self, msg):
        RCMessages=msg["A"][1]["Messages"]
        if type(RCMessages) == dict :
            RCMessages=[
                value
                for key, value in RCMessages.items()
            ]
        [
            self.discord.post(
                username=f"Mikey Masi{self.tag}",
                embeds=[
                    {
                        "title": content["Message"],
                        "fields": [
                            { "name": key, "value": value, "inline": True }
                            for key, value in content.items() if key in ["Sector", "RacingNumber", "Flag", "Mode", "Lap", "Status"]
                        ]
                    }
                ]
            ) 
            for content in RCMessages
        ]
    
    def liveTimingStatsHandler(self, msg):
        # Post personal best when not in race / sprint
        # Post overall best in any session.
        timingStats = msg["A"][1]["Lines"]

        for RacingNumber, stat in timingStats.items():
            info = self.driverList[RacingNumber]
            if ( # Check lap time improved
                "PersonalBestLapTime" in stat and
                "Value" in stat["PersonalBestLapTime"] and
                stat["PersonalBestLapTime"]["Value"] != "" and
                (
                    stat["PersonalBestLapTime"]["Value"] < self.timingStats["Lines"][RacingNumber]["PersonalBestLapTime"]["Value"] or
                    self.timingStats["Lines"][RacingNumber]["PersonalBestLapTime"]["Value"]==""
                )
            ):
                # Quickest Overall
                if(
                    (
                        "Position" in stat["PersonalBestLapTime"] and
                        stat["PersonalBestLapTime"]["Position"]==1
                    ) or
                    (
                        not "Position" in stat["PersonalBestLapTime"] and
                        self.timingStats["Lines"][RacingNumber]["PersonalBestLapTime"]["Position"] == 1
                    )
                ):
                    self.discord.post(
                        username=f"{info['Tla']} - {info['RacingNumber']}{self.tag}",
                        embeds=[
                            {
                                "title": "Ouickest Overall",
                                "fields": [
                                    {"name": "Lap Time", "value": stat["PersonalBestLapTime"]["Value"], "inline": True },
                                    {
                                        "name": "Tyre",
                                        "value": f"{self.timingAppData['Lines'][RacingNumber]['Stints'][-1]['Compound']} (age: {self.timingAppData['Lines'][RacingNumber]['Stints'][-1]['TotalLaps']})",
                                        "inline": True
                                    },
                                ],
                                "color": 10181046 #Purple
                            }
                        ],
                        avatar_url=info["HeadshotUrl"] if "HeadshotUrl" in info else None
                    )
                elif ( self.sessionInfo["Type"] in ["Qualifying", "Sprint Shootout"] ):
                    self.discord.post(
                        username=f"{info['Tla']} - {info['RacingNumber']}{self.tag}",
                        embeds=[
                            {
                                "title": "Personal Best",
                                "fields": [
                                    {"name": "Lap Time", "value": stat["PersonalBestLapTime"]["Value"], "inline": True },
                                    {
                                        "name": "Tyre",
                                        "value": f"{self.timingAppData['Lines'][RacingNumber]['Stints'][-1]['Compound']} (age: {self.timingAppData['Lines'][RacingNumber]['Stints'][-1]['TotalLaps']})",
                                        "inline": True
                                    },
                                ],
                                "color": 5763719 #Green
                            }
                        ],
                        avatar_url=info["HeadshotUrl"] if "HeadshotUrl" in info else None
                    )
        # update object anyway
        self.timingStats["Lines"] = updateDictDelta(self.timingStats["Lines"], timingStats)
            

    
    def liveTimingAppDataHandler(self, msg):
        compoundColor={
            "SOFT": 15548997, # RED
            "MEDIUM": 16776960, # YELLOW
            "HARD": 16777215, # WHITE
            "INTER": 2067276, # GREEN
            "WET": 2123412, # BLUE
        }
        lineStats = msg["A"][1]["Lines"]

        for RacingNumber, stat in lineStats.items():
            info = self.driverList[RacingNumber]
            # Rank change
            if "Line" in stat:
                if stat["Line"] == 1 and self.sessionInfo["Type"] in ["Race", "Sprint"] :
                    self.discord.post(
                    username=f"{info['Tla']} - {info['RacingNumber']}{self.tag}",
                    embeds=[
                        {
                            "title": f"Race Leader: {info['FullName']}",
                            "fields": [
                                {"name": "TeamName", "value": info["TeamName"], "inline": True},
                            ],
                            "color": int(info['TeamColour'], 16),
                        }
                    ],
                    avatar_url=info["HeadshotUrl"] if "HeadshotUrl" in info else None
                )
                # merge data
                self.timingAppData["Lines"][RacingNumber]["Line"] = stat["Line"]
            
            # Stints
            if "Stints" in stat:
                if type(stat["Stints"]) == dict:
                    stintsDict = dict(
                        [ (str(idx), stint) for idx, stint in enumerate( self.timingAppData["Lines"][RacingNumber]["Stints"] ) ]
                    )
                    stintsDict = updateDictDelta(stintsDict, stat["Stints"])
                    stintsList = [ stint for _, stint in stintsDict.items() ]
                    currentStint = stintsList[-1]
                    # announce tyre change if necessary
                    if (
                        self.sessionInfo["Type"] in ["Race", "Sprint"] and
                        (
                            len(stintsList) > len(self.timingAppData["Lines"][RacingNumber]["Stints"]) or
                            currentStint["Compound"] != self.timingAppData["Lines"][RacingNumber]["Stints"][len(stintsList)-1]["Compound"]
                        ) and
                        currentStint["TyresNotChanged"] == "0"
                    ):
                        self.discord.post(
                            username=f"{info['Tla']} - {info['RacingNumber']}{self.tag}",
                            embeds=[
                                {
                                    "title": "Tyre Change",
                                    "fields": [
                                        {"name": "Stint", "value": len(stintsList), "inline": True},
                                        {"name": "Compound", "value": currentStint["Compound"], "inline": True},
                                        {"name": "Age", "value": currentStint["StartLaps"], "inline": True},
                                    ],
                                    "color": compoundColor[currentStint["Compound"]] if "Compound" in currentStint and currentStint["Compound"] in compoundColor else None,
                                }
                            ],
                            avatar_url=info["HeadshotUrl"] if "HeadshotUrl" in info else None
                        )
                    self.timingAppData["Lines"][RacingNumber]["Stints"] = stintsList
                elif type(stat["Stints"]) == list:

                    # merge data
                    self.timingAppData["Lines"][RacingNumber]["Stints"] = stat["Stints"]

def updateDictDelta(obj, delta):
    for key, value in delta.items():
        if key not in obj:
            obj[key] = value
        elif type(value) == dict and type(obj[key]) == dict:
            obj[key] = updateDictDelta(obj[key], value)
        elif type(value) == list and type(obj[key]) == list:
            obj[key] = updateListDelta(obj[key], value)
        elif type(value) == dict and type(obj[key]) == list:
            obj[key] = updateListDelta(obj[key], [
                a_value
                for _, a_value in value.items()
            ])
        else:
            obj[key] = value
    return obj

def updateListDelta(obj, delta):
    for key, value in enumerate(delta):
        if key >= len(obj):
            obj.append(value)
        elif type(value) == dict and type(obj[key]) == dict:
            obj[key] = updateDictDelta(obj[key], value)
        elif type(value) == list and type(obj[key]) == list:
            obj[key] = updateListDelta(obj[key], value)
        elif type(value) == dict and type(obj[key]) == list:
            obj[key] = updateListDelta(obj[key], [
                a_value
                for _, a_value in value.items()
            ])
        else:
            obj[key] = value
            
    return obj
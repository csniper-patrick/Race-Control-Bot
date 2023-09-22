from discordwebhook import Discord
class messageManager:
    def __init__(self, webhook):
        self.discord = Discord(url=webhook)
        return
    
    def updateReference(self, msg):
        if "DriverList" in msg:
            self.driverList=msg["DriverList"]
        if "SessionInfo" in msg:
            self.sessionInfo=msg["SessionInfo"]
    
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

    def liveTrackStatusHandler(self, msg):
        self.discord.post(
            username="賽道狀況 (Alpha)",
            embeds=[
                {
                    "title": msg["A"][1]['Message']
                }
            ]
        )

    def liveRaceControlMessagesHandler(self, msg):
        RCMessages=msg["A"][1]["Messages"]
        if type(RCMessages) == dict :
            RCMessages=[
                value
                for key, value in RCMessages.items()
            ]
        [
            self.discord.post(
                username="Mikey Masi (Alpha)",
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
            if (
                "PersonalBestLapTime" in stat and
                "Value" in stat["PersonalBestLapTime"] and
                stat["PersonalBestLapTime"]["Value"] != "" and 
                stat["PersonalBestLapTime"]["Position"] == 1
            ):
                self.discord.post(
                    username=f"{info['Tla']} - {info['RacingNumber']}",
                    embeds=[
                        {
                            "title": "Ouickest Overall",
                            "fields": [
                                {"name": "Lap Time", "value": stat["PersonalBestLapTime"]["Value"], "inline": True },
                            ],
                            "color": 10181046 #Purple
                        }
                    ],
                    avatar_url=info["HeadshotUrl"] if "HeadshotUrl" in info else None
                )
            elif (
                "PersonalBestLapTime" in stat and
                "Value" in stat["PersonalBestLapTime"] and
                stat["PersonalBestLapTime"]["Value"] != "" and 
                self.sessionInfo["Type"] in ["Qualifying", "Sprint Shootout"]
            ):
                self.discord.post(
                    username=f"{info['Tla']} - {info['RacingNumber']}",
                    embeds=[
                        {
                            "title": "Personal Best",
                            "fields": [
                                {"name": "Lap Time", "value": stat["PersonalBestLapTime"]["Value"], "inline": True },
                                {"name": "Position", "value": stat["PersonalBestLapTime"]["Position"], "inline": True }
                            ],
                            "color": 5763719 #Green
                        }
                    ],
                    avatar_url=info["HeadshotUrl"] if "HeadshotUrl" in info else None
                )
    
    def liveTimingAppDataHandler(self, msg):
        lineStats = msg["A"][1]["Lines"]
        # Announce Race leader change 
        # Announce Tyre change always
        for RacingNumber, stat in lineStats: 
            info = self.driverList[RacingNumber]
            if stat["Line"] == 1 and self.sessionInfo["Type"] in ["Race", "Sprint"] and lineStats:
                self.discord.post(
                    username=f"{info['Tla']} - {info['RacingNumber']}",
                    embeds=[
                        {
                            "title": "Race Leader",
                            "fields": [
                                {"name": key, "value": info[key], "inline": True}
                                for key in ["FullName", "TeamName", "CountryCode"]
                            ],
                            "color": int(info['TeamColour'], 16),
                        }
                    ],
                    avatar_url=info["HeadshotUrl"] if "HeadshotUrl" in info else None
                )
            if "Stints" in stat:
                for stint, stintInfo in stat["Stints"]:
                    if "New" in stintInfo:
                        self.discord.post(
                            username=f"{info['Tla']} - {info['RacingNumber']}",
                            embeds=[
                                {
                                    "title": "Tyre Change",
                                    "fields": [
                                        {"name": key, "value": stintInfo[key], "inline": True}
                                        for key in ["Compound", "New"]
                                    ],
                                    # SOFT  : 15548997 (RED)
                                    # MEDIUM: 16776960 (YELLOW)
                                    # HARD  : 16777215 (WHITE)
                                    # INTER : 2067276  (GREEN)
                                    # WET   : 2123412  (BLUE)
                                    # TEST_UNKNOWN: None
                                    "color": int(info['TeamColour'], 16),
                                }
                            ],
                            avatar_url=info["HeadshotUrl"] if "HeadshotUrl" in info else None
                        )

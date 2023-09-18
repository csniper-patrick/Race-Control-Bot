from discordwebhook import Discord
import json
class messageManager:
    def __init__(self, webhook):
        self.discord = Discord(url=webhook)
        return
    
    def updateReference(self, msg):
        if "DriverList" in msg:
            self.driverList=msg["DriverList"]
            # print(json.dumps(self.driverList, indent=4))
            # self.pushDriverList()
        if "SessionInfo" in msg:
            self.sessionInfo=msg["SessionInfo"]
    
    def pushDriverList(self):
        for number, info in self.driverList.items():
            if type(info) is not dict: 
                continue 
            self.discord.post(
                # username=f"{info['FullName']} ({info['Tla']}) - {info['RacingNumber']}",
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
        if self.sessionInfo["Type"] in ["Practice", "Qualifying", "Sprint Shootout"]:
            for RacingNumber, stat in timingStats.items():
                if ( "PersonalBestLapTime" in stat and
                     "Value" in stat["PersonalBestLapTime"] and
                     stat["PersonalBestLapTime"]["Value"] != "" ):
                    info = self.driverList[RacingNumber]
                    self.discord.post(
                        username=f"{info['Tla']} - {info['RacingNumber']}",
                        embeds=[
                            {
                                "title": "Overall Best" if stat["PersonalBestLapTime"]["Position"] == 1 else "Personal Best Lap",
                                "fields": [
                                    {"name": "Lap Time", "value": stat["PersonalBestLapTime"]["Value"]}
                                ],
                                # purple: 10181046
                                # green: 5763719
                                "color": 10181046 if stat["PersonalBestLapTime"]["Position"] == 1 else 5763719
                            }
                        ],
                        avatar_url=info["HeadshotUrl"] if "HeadshotUrl" in info else None
                    )
        elif self.sessionInfo["Type"] in ["Race", "Sprint"]:
            for RacingNumber, stat in timingStats.items():
                if ( "PersonalBestLapTime" in stat and
                     "Value" in stat["PersonalBestLapTime"] and
                     stat["PersonalBestLapTime"]["Value"] != "" and 
                     stat["PersonalBestLapTime"]["Position"] == 1 ):
                    info = self.driverList[RacingNumber]
                    self.discord.post(
                        username=f"{info['Tla']} - {info['RacingNumber']}",
                        embeds=[
                            {
                                "title": "Fastest Lap",
                                "fields": [
                                    {"name": "Lap Time", "value": stat["PersonalBestLapTime"]["Value"]}
                                ],
                                # purple: 10181046
                                "color": 10181046
                            }
                        ],
                        avatar_url=info["HeadshotUrl"] if "HeadshotUrl" in info else None
                    )

    def liveTimingAppDataHandler(self, msg):
        lineStats = msg["A"][1]["Lines"] if "Lines" in msg["A"][1] else None
        # Announce when race leader change
        if self.sessionInfo["Type"] in ["Race", "Sprint"] and lineStats :
            for RacingNumber, stat in lineStats : 
                if stat["Line"] == 1 :
                    info = self.driverList[RacingNumber]
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

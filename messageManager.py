from discordwebhook import Discord
class messageManager:
    def __init__(self, webhook):
        self.discord = Discord(url=webhook)
        return
    
    def referenceUpdate(self, msg):
        if "DriverList" in msg:
            self.driverList=msg["DriverList"]
        if "SessionInfo" in msg:
            self.sessionInfo=msg["SessionInfo"]

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
        if type(RCMessages) == 'dict' :
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
                            for key, value in content.items() if key in ["Utc", "Sector", "RacingNumber", "Flag"]
                        ]
                    }
                ]
            ) 
            for content in RCMessages
        ]
from .utils import *


def liveRaceControlMessagesHandler(self, msg):
    flagColor = self.msgStyle["flagColor"]
    flagSymbol = self.msgStyle["flagSymbol"]
    modeColor = self.msgStyle["modeColor"]
    RCMessages = msg["A"][1]["Messages"]
    if type(RCMessages) == dict:
        RCMessages = [value for key, value in RCMessages.items()]
    for content in RCMessages:
        if "Flag" in content and content["Flag"] == "BLUE":
            continue
        if "Flag" in content and content["Flag"] in flagSymbol:
            content["Message"] = f"{flagSymbol[content['Flag']]}{content['Message']}"
        self.discord.post(
            username=f"{self.raceDirector}{self.tag}",
            embeds=[
                {
                    "title": content["Message"],
                    "fields": [
                        {"name": key, "value": value, "inline": True}
                        for key, value in content.items()
                        if key in ["Mode", "Status"]
                    ],
                    "color": (
                        flagColor[content["Flag"]]
                        if "Flag" in content and content["Flag"] in flagColor
                        else (
                            modeColor[content["Mode"]]
                            if "Mode" in content and content["Mode"]
                            else None
                        )
                    ),
                }
            ],
        )

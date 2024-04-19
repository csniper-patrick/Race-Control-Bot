from .utils import *


def livePitLaneTimeCollectionHandler(self, msg):
    if not self.sessionInfo["Type"] in ["Race", "Sprint"]:
        return
    pitLaneTimeCollection = msg["A"][1]["PitTimes"]
    for RacingNumber, pitLaneTime in pitLaneTimeCollection.items():
        if not RacingNumber in self.driverList:
            continue
        durationSec = reversed(
            [float(i) for i in re.split(":", pitLaneTime["Duration"])]
        )
        durationSec = sum([val * scaler for val, scaler in zip(durationSec, [1, 60])])
        if durationSec >= 30.0 and durationSec <= 600.0:
            info = self.driverList[RacingNumber]
            self.discord.post(
                username=f"{info['TeamName']}{self.tag}",
                embeds=[
                    {
                        "title": f"Slow Pit Stop - {pitLaneTime['Duration']} in pit lane",
                        "fields": [
                            {
                                "name": "Driver",
                                "value": info["FullName"],
                                "inline": True,
                            },
                        ],
                        "color": int(info["TeamColour"], 16),
                    }
                ],
            )

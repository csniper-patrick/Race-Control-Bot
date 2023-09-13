import requests
import json
import asyncio
import websockets
import urllib.parse
import os
from dotenv import load_dotenv
from discordwebhook import Discord

livetimingUrl = "https://livetiming.formula1.com/signalr"
websocketUrl = "wss://livetiming.formula1.com/signalr"
clientProtocol= 1.5

def negotiate():
    connectionData=[{"name": "Streaming"}]
    try:
        res = requests.get(
            f'{livetimingUrl}/negotiate',
            params={
                "connectionData": json.dumps(connectionData),
                "clientProtocol": clientProtocol
            }
        )
        return res.json(), res.headers
    except:
        print("error")

async def connectRaceControl():

    discord = Discord(
        url=os.getenv("DISCORD_WEBHOOK")
    )

    data, headers = negotiate()
    params = urllib.parse.urlencode({
        "clientProtocol": 1.5,
        "transport": "webSockets",
        "connectionToken": data["ConnectionToken"],
        "connectionData": json.dumps([{"name": "Streaming"}])
    })
    extra_headers={
        "User-Agent": "BestHTTP",
        "Accept-Encoding": "gzip,identity",
        "Cookie": headers["Set-Cookie"]
    }
    async with websockets.connect(f'{websocketUrl}/connect?{params}', extra_headers=extra_headers) as sock:
        try:
            initMsg = await sock.recv()
            print(f"Received: {initMsg}")
            await sock.send(
                json.dumps(
                    {
                        "H": "Streaming",
                        "M": "Subscribe",
                        # "A": [["Heartbeat", "CarData.z", "Position.z", "ExtrapolatedClock", "TopThree", "RcmSeries","TimingStats", "TimingAppData","WeatherData", "TrackStatus", "DriverList", "RaceControlMessages", "SessionInfo", "SessionData", "LapCount", "TimingData"]],
                        "A": [["RaceControlMessages", "TrackStatus", "WeatherData" ]],
                        "I": 1
                    }
                )
            )

            skipRaceControlMessages = (os.getenv('BURST_MSG') != "True") 

            while message := await sock.recv() :
                message = json.loads(message)
                print(json.dumps(message,indent=4))

                # post TrackStatus
                if "R" in message and "TrackStatus" in message["R"] :
                    discord.post(
                        username="Track Condition",
                        embeds=[
                            {
                                "title": message['R']['TrackStatus']['Message'],
                                "fields": [
                                    { "name": key, "value": value , "inline": True }
                                    for key, value in message['R']['TrackStatus'].items() if not key in ["Message", "_kf"]
                                ]
                            }
                        ]
                    )

                # post weather data
                if "R" in message and "WeatherData" in message["R"] :
                    discord.post(
                        username="Mr. Weather",
                        embeds=[
                            {
                                "title": "Weather Report",
                                "fields": [
                                    { "name": key, "value": value , "inline": True }
                                    for key, value in message["R"]["WeatherData"].items() if key != "_kf"
                                ]
                            }
                        ]
                    )
                
                # post Race Control Message
                if "R" in message and "RaceControlMessages" in message["R"] :
                    # [ discord.post(content=item["Message"], username="Mikey") for item in message["R"]["RaceControlMessages"]["Messages"] if not skipRaceControlMessages ]
                    [
                        discord.post(
                            username="Mikey",
                            embeds=[
                                {
                                    "title": RCMessage["Message"],
                                    "fields": [
                                        { "name": key, "value": value, "inline": True }
                                        for key, value in RCMessage.items() if not key in ["Message", "Utc"]
                                    ]
                                }
                            ]
                        )
                        for RCMessage in message["R"]["RaceControlMessages"]["Messages"] if not skipRaceControlMessages
                    ]
                    skipRaceControlMessages=False

        except Exception as error:
            print(error)
            return

def main():
    load_dotenv()
    asyncio.get_event_loop().run_until_complete(connectRaceControl())

if __name__ == "__main__":
    main()
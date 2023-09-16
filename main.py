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
                        "A": [["RaceControlMessages", "TrackStatus"]],
                        "I": 1
                    }
                )
            )

            skipRaceControlMessages = (os.getenv('BURST_MSG') != "True") 
            skipTrackStatus = (os.getenv('BURST_MSG') != "True") 
            skipWeatherData = (os.getenv('BURST_MSG') != "True")
            verbose = (os.getenv('VERBOSE') == "True") 

            while messages := await sock.recv() :
                messages = json.loads(messages)
                if verbose and bool(messages): 
                    print(json.dumps(messages,indent=4))

                # process live data
                if "M" in messages:
                    for msg in messages["M"] :
                        if msg["H"] == "Streaming":
                            # Post Track Status
                            if msg["A"][0] == "TrackStatus":
                                discord.post(
                                    username="賽道狀況 (Alpha)",
                                    embeds=[
                                        {
                                            "title": msg["A"][1]['Message'],
                                            "fields": [
                                            { "name": key, "value": value , "inline": True }
                                            for key, value in msg["A"][1].items() if not key in ["Message", "_kf"]
                                            ]
                                        }
                                    ]
                                )
                            # Post Race Control Message
                            if msg["A"][0] == "RaceControlMessages":
                                [
                                    discord.post(
                                        username="Mikey Masi (Alpha)",
                                        embeds=[
                                            {
                                                "title": content["Message"],
                                                "fields": [
                                                    { "name": key, "value": value, "inline": True }
                                                    for key, value in content.items() if not key in ["Message"]
                                                ]
                                            }
                                        ]
                                    ) 
                                    for content in msg["A"][1]["Messages"].items()
                                ]
        except Exception as error:
            print(error)
            return

def main():
    load_dotenv()
    asyncio.get_event_loop().run_until_complete(connectRaceControl())

if __name__ == "__main__":
    main()
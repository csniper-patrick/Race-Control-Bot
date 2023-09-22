import requests
import json
import asyncio
import websockets
import urllib.parse
import os
from dotenv import load_dotenv
from messageManager import *

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
            await sock.send(
                json.dumps(
                    {
                        "H": "Streaming",
                        "M": "Subscribe",
                        # "A": [["Heartbeat", "CarData.z", "Position.z", "ExtrapolatedClock", "TopThree", "RcmSeries","TimingStats", "TimingAppData","WeatherData", "TrackStatus", "DriverList", "RaceControlMessages", "SessionInfo", "SessionData", "LapCount", "TimingData"]],
                        "A": [["RaceControlMessages", "TrackStatus", "DriverList", "TimingStats", "TimingAppData", "SessionInfo"]],
                        "I": 1
                    }
                )
            )
            verbose = (os.getenv('VERBOSE') == "True")

            manager = messageManager(os.getenv("DISCORD_WEBHOOK"))

            while messages := await sock.recv() :
                messages = json.loads(messages)
                if verbose and bool(messages): 
                    print(json.dumps(messages,indent=4))

                # process reference data (R type)
                if "R" in messages:
                    manager.updateReference(messages["R"])
                # process live data (M type)
                if "M" in messages:
                    for msg in messages["M"] :
                        if msg["H"] == "Streaming" and msg["A"][0] == "TrackStatus":
                            manager.liveTrackStatusHandler( msg = msg )
                        if msg["H"] == "Streaming" and msg["A"][0] == "RaceControlMessages":
                            manager.liveRaceControlMessagesHandler( msg = msg )
                        if msg["H"] == "Streaming" and msg["A"][0] == "TimingStats":
                            manager.liveTimingStatsHandler( msg = msg )
                        # if msg["H"] == "Streaming" and msg["A"][0] == "TimingAppData":
                        #     manager.liveTimingAppDataHandler( msg = msg )
                        
        except Exception as error:
            print(error)
            return

def main():
    load_dotenv()
    asyncio.get_event_loop().run_until_complete(connectRaceControl())

if __name__ == "__main__":
    main()
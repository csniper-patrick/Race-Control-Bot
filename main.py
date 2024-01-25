import requests
import json
import asyncio
import websockets
import urllib.parse
import os
from dotenv import load_dotenv
from messageManager import *

load_dotenv()

use_ssl = (os.getenv("USE_SSL", default="True")) == "True"
api_host = os.getenv("API_HOST", default="livetiming.formula1.com")
retry = (os.getenv("RETRY", default="True")) == "True"

# livetimingUrl = f"https://{api_host}/signalr" if use_ssl == "true" else f"http://{api_host}/signalr"
livetimingUrl = urllib.parse.urljoin(f"https://{api_host}"if use_ssl else f"http://{api_host}", "/signalr")

# websocketUrl  = f"wss://{api_host}/signalr"   if use_ssl == "true" else f"ws://{api_host}/signalr"
websocketUrl  = urllib.parse.urljoin(f"wss://{api_host}"if use_ssl else f"ws://{api_host}", "/signalr")

# staticUrl     = f"https://{api_host}/static"  if use_ssl == "true" else f"http://{api_host}/static"
staticUrl     = urllib.parse.urljoin(f"https://{api_host}"if use_ssl else f"http://{api_host}", "/static")

print(livetimingUrl, websocketUrl, staticUrl)

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
        print(res.json(), res.headers)
        return res.json(), res.headers
    except:
        print("error")

async def connectRaceControl():
    while True:
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

        async with websockets.connect(f'{websocketUrl}/connect?{params}', extra_headers=extra_headers, ping_interval=None) as sock:
            try:
                await sock.send(
                    json.dumps(
                        {
                            "H": "Streaming",
                            "M": "Subscribe",
                            # "A": [["Heartbeat", "CarData.z", "Position.z", "ExtrapolatedClock", "TopThree", "RcmSeries","TimingStats", "TimingAppData","WeatherData", "TrackStatus", "DriverList", "RaceControlMessages", "SessionInfo", "SessionData", "LapCount", "TimingData"]],
                            "A": [["Heartbeat", "RaceControlMessages", "TrackStatus", "DriverList", "WeatherData", "TimingStats", "TimingAppData", "SessionInfo"]],
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
                            if msg["H"] == "Streaming" and msg["A"][0] == "DriverList":
                                manager.liveDriverListHandler( msg = msg )
                            if msg["H"] == "Streaming" and msg["A"][0] == "SessionInfo":
                                manager.liveSessionInfoHandler( msg = msg )
                            
            except Exception as error:
                print(error)
                if retry:
                    continue
                else:
                    break

def main():
    asyncio.get_event_loop().run_until_complete(connectRaceControl())

if __name__ == "__main__":
    main()
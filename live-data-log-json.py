import requests
import json
import asyncio
import websockets
import urllib.parse
import os
from dotenv import load_dotenv
from datetime import datetime

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
    msg_cnt=0
    while True:
        async with websockets.connect(f'{websocketUrl}/connect?{params}', extra_headers=extra_headers) as sock:
            try:
                await sock.send(
                    json.dumps(
                        {
                            "H": "Streaming",
                            "M": "Subscribe",
                            "A": [["Heartbeat", "CarData.z", "Position.z", "ExtrapolatedClock", "TopThree", "RcmSeries","TimingStats", "TimingAppData","WeatherData", "TrackStatus", "DriverList", "RaceControlMessages", "SessionInfo", "SessionData", "LapCount", "TimingData"]],
                            "I": 1
                        }
                    )
                ) 
                log_dir = os.path.join( os.path.abspath("."), f"live-racectl-msg-{datetime.now().strftime('%FT%T')}")
                if not os.path.exists(log_dir):
                    # Create a new directory because it does not exist
                    os.makedirs(log_dir)

                while messages := await sock.recv() :
                    messages = json.loads(messages)
                    if bool(messages):
                        with open(os.path.join( log_dir, f"{datetime.now().strftime('%FT%T.%f')}.json" ), "w") as output_json:
                            json.dump(messages, output_json, indent=4)
            except Exception as error:
                print(error)
                continue

def main():
    load_dotenv()
    asyncio.get_event_loop().run_until_complete(connectRaceControl())

if __name__ == "__main__":
    main()
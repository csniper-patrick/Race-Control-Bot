import requests
import json
import asyncio
import websockets
import urllib.parse

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
            initMsg = await sock.recv()
            print(f"Received: {initMsg}")
            await sock.send(
                json.dumps(
                    {
                        "H": "Streaming",
                        "M": "Subscribe",
                        # "A": [["RaceControlMessages", "TrackStatus", "ExtrapolatedClock", "DriverList", "SessionInfo", "LapCount"]],,
                        "A": [["RaceControlMessages", "TrackStatus"]],
                        "I": 1
                    }
                )
            )
        except:
            print("subscription failed!");
            return

        while True:
            try:
                message = await sock.recv()
                print(json.dumps(
                    json.loads(message),
                    indent=4
                ))
            except websockets.exceptions.ConnectionClosed:
                print("WebSocket connection closed.")
                break

def main():
    asyncio.get_event_loop().run_until_complete(connectRaceControl())

if __name__ == "__main__":
    main()
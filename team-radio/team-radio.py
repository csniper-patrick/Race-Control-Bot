import requests
import json
import asyncio
import websockets
import os
import urllib.parse
from urllib.parse import urljoin
from functools import reduce
import os
from transformers import pipeline
import wget
from dotenv import load_dotenv
from discordwebhook import Discord

load_dotenv()

use_ssl = (os.getenv("USE_SSL", default="True")) == "True"
api_host = os.getenv("API_HOST", default="livetiming.formula1.com")
retry = (os.getenv("RETRY", default="True")) == "True"

# livetimingUrl = f"https://{api_host}/signalr" if use_ssl == "true" else f"http://{api_host}/signalr"
livetimingUrl = urljoin(
    f"https://{api_host}"if use_ssl else f"http://{api_host}", "/signalr")

# websocketUrl  = f"wss://{api_host}/signalr"   if use_ssl == "true" else f"ws://{api_host}/signalr"
websocketUrl = urljoin(
    f"wss://{api_host}"if use_ssl else f"ws://{api_host}", "/signalr")

# staticUrl     = f"https://{api_host}/static"  if use_ssl == "true" else f"http://{api_host}/static"
# staticUrl     = urljoin(f"https://{api_host}"if use_ssl else f"http://{api_host}", "/static")
staticUrl = "https://livetiming.formula1.com/static"

# suffix
tag = os.getenv("VER_TAG")

clientProtocol = 1.5


def negotiate():
    connectionData = [{"name": "Streaming"}]
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
    print(staticUrl)
    # Initialize model
    model = os.getenv("WHISPERS_MODEL",
                      default="distil-whisper/distil-small.en")
    transcriber = pipeline("automatic-speech-recognition", model=model)

    while True:
        data, headers = negotiate()
        params = urllib.parse.urlencode({
            "clientProtocol": 1.5,
            "transport": "webSockets",
            "connectionToken": data["ConnectionToken"],
            "connectionData": json.dumps([{"name": "Streaming"}])
        })
        extra_headers = {
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
                            "A": [["Heartbeat", "SessionInfo", "DriverList", "TeamRadio"]],
                            "I": 1
                        }
                    )
                )
                verbose = (os.getenv('VERBOSE') == "True")

                discord = Discord(url=os.getenv("DISCORD_WEBHOOK"))

                SessionInfo = {}
                DriverList = {}

                while messages := await sock.recv():
                    messages = json.loads(messages)
                    if verbose and bool(messages):
                        print(json.dumps(messages, indent=4))

                    # process reference data (R type)
                    if "R" in messages:
                        if "SessionInfo" in messages["R"]:
                            SessionInfo = messages["R"]["SessionInfo"]
                        if "DriverList" in messages["R"]:
                            DriverList = messages["R"]["DriverList"]

                    # process live data (M type)
                    if "M" in messages:
                        for msg in messages["M"]:
                            if msg["H"] == "Streaming" and msg["A"][0] == "DriverList":
                                # update driver information
                                DriverList = msg["A"][1]
                            elif msg["H"] == "Streaming" and msg["A"][0] == "SessionInfo":
                                # update driver information
                                SessionInfo = msg["A"][1]

                        for msg in messages["M"]:
                            if msg["H"] == "Streaming" and msg["A"][0] == "TeamRadio" and "Captures" in msg["A"][1]:
                                captures = msg["A"][1]["Captures"]
                                # list
                                if type(captures) == dict:
                                    captures = [capture for _,
                                                capture in captures.items()]
                                if type(captures) == list:
                                    for capture in captures:
                                        if capture["RacingNumber"] not in DriverList:
                                            continue
                                        info = DriverList[capture["RacingNumber"]]
                                        radioURL = reduce(
                                            urljoin, [staticUrl, SessionInfo['Path'], capture['Path']])
                                        print(radioURL)
                                        radioFile = wget.download(radioURL)
                                        transcribe = transcriber(radioFile)
                                        discord.post(
                                            username=f"{info['Tla']} - {info['RacingNumber']}",
                                            avatar_url=info["HeadshotUrl"] if "HeadshotUrl" in info else None,
                                            content=transcribe["text"]
                                        )
                                        os.remove(radioFile)

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

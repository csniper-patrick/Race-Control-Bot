# Race Control Bot (F1)

This is a Discord bot that connects to livetiming.formula1.com signalr endpoint using WebSocket, then processes and pushes some of the live messages into the Discord channel of your choice. 

## Installation
Because of some of the syntax I use, at least python3.8 should be used. a requirements.txt is provided so that you can pip install everything you need from that easily. The app is configured using environment variables, you can define them in a `.env` file. 

### Clone project and install packages
```bash
git clone https://gitlab.com/CSniper/live-race-control-messages.git
cd live-race-control-messages
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Configuration
You can configure the app using the following environment variables.

| Variable | Description |
|----------|-------------|
| DISCORD_WEBHOOK | `(String, Required)` Webhook URL of the Discord Channel of your choice |
| USE_SSL | `([True]/False, Optional)` Use https or not when connect data source |
| API_HOST | `(String, Optional)` mock api URL (if you have one) for test purpose |
| RETRY | `([True]/False, Optional)` Reconnect or not when disconnect from the endpoint |
| VER_TAG | `(String, Optional)` A suffix to the display name of the bot |

example `.env` file:
```
DISCORD_WEBHOOK=https://discord.com/api/webhooks/1234567890123456789/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
VER_TAG="No Mikey No"
```

### Starting the bot
Now you can start the bot. Make sure you have activated the environment
```
python main.py
```

### automated deployment
Under the playbook directory are playbooks and templates for the automated deployment of this project.

## Testing
The testing setup is very premature, hopefully, I can improve the performance and then publish it as well.

## Acknowledgment

This project would not be possible without referencing [Philipp Schaefer (theOehrly)](https://github.com/theOehrly)'s work [FastF1](https://github.com/theOehrly/Fast-F1). If you want to know more about how to use the live timing endpoint, definitely check out his code. 

Big thanks to Daniel Chan and everyone in his Discord F1 channel for your feedback. Your feedback improved this project a lot, and your support makes this project meaningful.

## Disclaimer
This is an unofficial project and is not associated in any way with the Formula 1 company, teams, drivers, organizers, organizations, management or governing bodies. F1, FORMULA ONE, FORMULA 1, FIA FORMULA ONE WORLD CHAMPIONSHIP, GRAND PRIX and related marks are trademarks of Formula One Licensing B.V.

The source code of this project is released under the MIT license, please refer to the LICENSE file for details. 
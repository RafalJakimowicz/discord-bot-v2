# Discord logging and administration bot

Discord bot for advance logging on server and more

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)

## Installation

To install bot run:

```bash
git clone https://github.com/RafalJakimowicz/discord-bot-v2
cd discord-bot-v2
```

make virtual enviroment for this bot by and change source:

```bash
python -m venv venv
source venv/bin/activate

```

and install libraries:
```bash
pip install -r requirements.txt 
```

After python packages instalation in bot directory make .env file

```bash
touch .env
```

make file with this template

```env
DISCORD_TOKEN=you discord token
AI_API_KEY=your ai api token from open router
DATABASE_HOST_NAME=host of database
DATABASE_NAME=name of database
DATABASE_USER=database login
DATABASE_PASSWORD=database password
```

after this see your config file at name config.json in project main directory shuld be like this 
and change features to your preference leave "logging" section as it is bot will update this on his own
```json
{
    "logging": {
        "logging-channel-group-id": 0,
        "members-joins-channel-id": 0,
        "members-leaves-channel-id": 0,
        "messages-stats-channel-id": 0,
        "commands-channel-id": 0,
        "admin-voice-channel": 0
    },
    "features": {
        "logging": true,
        "ai-chat": true
    },
    "roles": {
        "mod-role-id": 0,
        "admin-role-id": 0,
        "owner-role-id": 0
    }
}
```

import discord
from src.bot.bot import DiscordBot
import os
from dotenv import load_dotenv
import json

config_path = 'config.json'

with open(config_path, 'r', encoding='utf-8') as file:
    config = json.load(file)

print(config)

load_dotenv("./.env")
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True

bot = DiscordBot(command_prefix='!', intents=intents, config=config, config_path=config_path)

bot.run(DISCORD_TOKEN)
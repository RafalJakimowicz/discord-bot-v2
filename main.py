import discord
from src.bot.bot import DiscordBot
import os
from dotenv import load_dotenv

load_dotenv("./.env")
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
print(DISCORD_TOKEN)

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True

bot = DiscordBot(command_prefix='!', intents=intents)

bot.run(DISCORD_TOKEN)
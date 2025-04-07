import discord
from discord.ext import commands
from datetime import datetime

class AdminCog(commands.Cog):
    def __init__(self, bot, config: dict, config_path: str):
        self.bot = bot
        self.config = config
        self.path = config_path
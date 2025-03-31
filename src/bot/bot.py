import discord
from discord.ext import commands
from discord import app_commands
from ..database.postgres_database import Database
from datetime import datetime

class DiscordBot(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.__sql_database = Database()
        pass

    async def on_ready(self):
        print(f'Logged as {self.user.name} (ID: {self.user.id})')

    def setup_commands(self):
        return [
            app_commands.Command(
                name='ask'
            )
        ]
    
    async def on_message(self, message):
        await self.__sql_database.add_message_to_database(
            message.id,
            message.author.id,
            str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            message.guild.name,
            message.channel.name,
            message.content)
        return await super().on_message(message)
    
import discord
from discord.ext import commands
from discord import app_commands

class DiscordBot(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix=command_prefix, intents=intents)
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
        return await super().on_message(message)
    
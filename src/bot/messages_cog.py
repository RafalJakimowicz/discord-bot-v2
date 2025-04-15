import discord
from discord.ext import commands
from datetime import datetime
from discord import app_commands
from ..database.logging_database import Logging_Database


class MessagesCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.__sql = Logging_Database()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        if message.author == self.bot.user:
            return

        await self.__sql.add_message_to_database(message=message,
            timestamp=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        
        await self.bot.process_commands(message)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):

        if message.author == self.bot.user:
            return
        
        await self.__sql.add_deleted_message(message=message)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):

        if before.author == self.bot.user:
            return
        
        await self.__sql.add_edited_message_to_database(before=before, after=after)

    @app_commands.command(name="message-stats", description="gets messages stats")
    async def get_messages_stats(self, interaction: discord.Interaction):
        pass
        

        

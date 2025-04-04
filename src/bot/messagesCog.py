import discord
from discord.ext import commands
from datetime import datetime
from ..database.postgres_database import Database


class MessagesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.__sql = Database()

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
import discord
from discord.ext import commands
from datetime import datetime
from ..database.postgres_database import Database

class MembersCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.__sql = Database()

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member == self.bot.user:
            return
        
        await self.__sql.add_member_to_database(member=member)
        await self.__sql.track_member_joins_and_leaves(member, True, False, str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        if member == self.bot.user:
            return
        
        await self.__sql.track_member_joins_and_leaves(member, False, True, str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if before == self.bot.user:
            return
        
        await self.__sql.update_user(before=before, after=after)
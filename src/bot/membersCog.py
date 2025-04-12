import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
from ..database.logging_database import Database

class MembersCog(commands.Cog):
    def __init__(self, bot, config: dict):
        self.config = config
        self.bot = bot
        self.__sql = Database()

        for user in self.bot.guilds[0].members:
            self.__sql.add_member_to_database(user)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member == self.bot.user:
            return
        
        for channel in member.guild.channels:
            if channel.id == self.config["logging"]["members-joins-channel-id"]:
                embed = discord.Embed(
                    title=f"Przyleciał {member.global_name}",
                    color=discord.Color.green()
                )
                embed.add_field(name="Id", value=str(member.id), inline=False)
                embed.add_field(name="Data",value=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), inline=False)
                embed.set_thumbnail(url=member.display_avatar.url)
                channel.send(embed=embed)
        
        await self.__sql.add_member_to_database(member=member)
        await self.__sql.track_member_joins_and_leaves(member, True, False, str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        if member == self.bot.user:
            return
        
        for channel in member.guild.channels:
            if channel.id == self.config["logging"]["members-leaves-channel-id"]:
                embed = discord.Embed(
                    title=f"Odleciał {member.global_name}",
                    color=discord.Color.red()
                )
                embed.add_field(name="Id", value=str(member.id), inline=False)
                embed.add_field(name="Data",value=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), inline=False)
                embed.set_thumbnail(url=member.display_avatar.url)
                channel.send(embed=embed)
        
        await self.__sql.track_member_joins_and_leaves(member, False, True, str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if before == self.bot.user:
            return
        
        await self.__sql.update_user(before=before, after=after)

    @app_commands.command(name="members-stat", description="sends stats to channel")
    @app_commands.default_permissions(administrator=True)
    async def send_stats(self, interaction: discord.Interaction):
        pass

    
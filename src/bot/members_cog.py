import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
from ..database.logging_database import Logging_Database

class MembersCog(commands.Cog):
    def __init__(self, bot: commands.bot, config: dict):
        self.config = config
        self.bot = bot
        self.__sql = Logging_Database()

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
        await interaction.response.defer(thinking=True)
        leaves = []
        joins = []
        members = []

        members = self.__sql.get_all_members()
        statuses_result = self.__sql.get_all_statuses()

        for status in statuses_result:
            if status[3] == True: #join
                joins.append(status)
            if status[4] == True: #leaves
                leaves.append(status)

        last_join = await self.bot.fetch_user(joins[-1])
        last_leave = await self.bot.fetch_user(leaves[-1])


        #Embed z statystykami 
        embed_stats = discord.Embed(
            title="Statystyki",
            color=discord.Color.blue()
        )
        embed_stats.add_field(
            name="Ilość członków",
            value=len(members)
        )
        embed_stats.add_field(
            name="Wszystkie Przyloty",
            value=len(joins)
        )
        embed_stats.add_field(
            name="Wszystkie Odloty",
            value=len(leaves)
        )

        #Embed z ostatnim odlotem
        embed_leave = discord.Embed(
            title=f"Ostatni odlot gracza {last_leave.global_name}",
            color=discord.Color.red()
        )
        embed_leave.add_field(
            name="Id",
            value=last_leave.id
        )
        embed_leave.add_field(
            name='Data',
            value=leaves[-1][2]
        )
        embed_leave.set_thumbnail(url=last_leave.display_avatar.url)
        

        #Embed z osttanim przylotem
        embed_join = discord.Embed(
            title=f"Ostatni przylot gracza {last_join.global_name}",
            color=discord.Color.red()
        )
        embed_join.add_field(
            name="Id",
            value=last_join.id
        )
        embed_join.add_field(
            name='Data',
            value=joins[-1][2]
        )
        embed_join.set_thumbnail(url=last_join.display_avatar.url)

        await interaction.followup.send(
            embeds=[
                embed_stats,
                embed_leave,
                embed_join
            ]
        )





    
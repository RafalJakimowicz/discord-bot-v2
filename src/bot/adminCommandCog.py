import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
from ..database.postgres_database import Database

class AdminCog(commands.Cog):
    def __init__(self, bot, config: dict, config_path: str):
        self.bot = bot
        self.config = config
        self.path = config_path
        self.commands_list = []
        self.__sql = Database()

    def get_commands(self) -> list:
        """
        Gets admin commands to bot parent object 

        :return: commands list
        :rtype: list
        """
        self.commands_list.append(
            app_commands.Command(
                name="member-logs",
                description="get logs by member username",
                callback=self.get_logs_by_name
            )
        )
        return self.commands_list
    
    async def make_mod_role(self, guild: discord.Guild) -> discord.Role:
        """
        Makes mod rule for moderators to use it has limited permissions

        :param guild: interaction guild
        :type guild: discord.Guild
        :return: mod role
        :rtype: discord.Role
        """
        moderator = discord.Role
        stage_mod = discord.Permissions.stage_moderator()
        membership = discord.Permissions.membership()
        mod = stage_mod | membership | discord.Permissions.DEFAULT_VALUE
        moderator.name = "Moderator"
        moderator.color = discord.Color.green()
        moderator.mentionable = True
        moderator.permissions = mod
        return await guild.create_role(moderator)
    
    async def make_admin_role(self, guild: discord.Guild) -> discord.Role:
        """
        Makes amdin rule for admins to use it has admin permissons

        :param guild: interaction guild
        :type guild: discord.Guild
        :return: admin role
        :rtype: discord.Role
        """
        admin = discord.Role
        admin.permissions = discord.Permissions.administrator
        admin.name = "Admin"
        admin.color = discord.Color.red()
        admin.mentionable = False
        admin.position = 98
        return await guild.create_role(admin)
    
    async def make_owner_role(self, guild: discord.Guild) -> discord.Role:
        """
        Makes owner rule with all permisions

        :param guild: interaction guild
        :type guild: discord.Guild
        :return: owner role
        :rtype: discord.Role
        """
        owner = discord.Role
        owner.permissions = discord.Permissions.all()
        owner.name = "Owner"
        owner.color = discord.Color.yellow()
        owner.mentionable = False
        owner.position = 99
        return await guild.create_role(owner)

    
    async def quick_setup(self, interaction: discord.Interaction):
        """
        Makes default quick setup for logging channels and basic roles

        :param interaction: interaction object 
        :type interaction: discord.Interaction
        """
        mod_role = await self.make_mod_role(interaction.guild)
        admin_role = await self.make_admin_role(interaction.guild)
        owner_role = await self.make_owner_role(interaction.guild)
        



    async def get_logs_by_name(self, interaction: discord.Interaction, username: str):
        await interaction.response.defer(thinking=True)

        response_str = ""
        response_list = await self.__sql.get_messages_by_username(username=username)
        for row in response_list:
            response_str = response_str + str(row) + "\n"

        embeded_messege = discord.Embed(
            title="Database response",
            description=f"logs for: {username} \n {response_str}",
            color=discord.Color.from_rgb(46, 255, 137)
        )

        await interaction.followup.send(embed=embeded_messege)
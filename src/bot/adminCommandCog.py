import discord
import json
from discord.ext import commands
from discord import app_commands
from datetime import datetime
from ..database.postgres_database import Database
import textwrap

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
            ),
            app_commands.Command(
                name="quick-setup",
                description="makes quick setup for basic logging channels and roles",
                callback=self.quick_setup
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
        owner.name = "Właściciel"
        owner.color = discord.Color.yellow()
        owner.mentionable = False
        owner.position = 99
        return await guild.create_role(owner)
    
    async def create_private_category(self, guild: discord.Guild, roles: list, *, category_name: str = "Logi"):

        overwrite = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False)
        }

        for role in roles:
            overwrite[role] = discord.PermissionOverwrite(view_channel=True)

        category = await guild.create_category(name=category_name, overwrites=overwrite)

        return category

    async def create_channels_in_category(self, guild: discord.Guild, category: discord.CategoryChannel) -> tuple:
        name_of_stats_channel = "Statystyki"
        name_of_commands_channel = "Komendy"
        name_of_joins_channel = "Przyloty"
        name_of_leaves_channel = "Odloty"

        name_of_mods_voice = "Głosowy"

        stats_channel = await guild.create_text_channel(
            name=name_of_stats_channel,
            category=category
        )

        commands_channel = await guild.create_text_channel(
            name=name_of_commands_channel,
            category=category
        )

        joins_channel = await guild.create_text_channel(
            name=name_of_joins_channel,
            category=category
        )

        leaves_channel = await guild.create_text_channel(
            name=name_of_leaves_channel,
            category=category
        )

        voice_channel = await guild.create_voice_channel(
            name=name_of_mods_voice,
            category=category
        )

        return ([stats_channel,commands_channel,joins_channel, leaves_channel],[voice_channel])



    
    async def quick_setup(self, interaction: discord.Interaction):
        """
        Makes default quick setup for logging channels and basic roles

        :param interaction: interaction object 
        :type interaction: discord.Interaction
        """
        mod_role = await self.make_mod_role(interaction.guild)
        admin_role = await self.make_admin_role(interaction.guild)
        owner_role = await self.make_owner_role(interaction.guild)

        category = await self.create_private_category(
            guild=interaction.guild,
            roles=[mod_role, admin_role, owner_role],
            category_name="Logi serwera"
        )

        channels = await self.create_channels_in_category(
            guild=interaction.guild,
            category=category
        )

        text_channels = channels[0]
        voice_channels = channels[1]

        stats_channel_id = text_channels[0].id
        commands_channel_id = text_channels[1].id
        joins_channel_id = text_channels[2].id
        leaves_channel_id = text_channels[3].id
        voice_channel_id = voice_channels[0].id

        category_id = category.id

        with open(self.path, "r+", encoding='utf-8') as config_file:
            config = json.load(config_file)
            #setup variables in config file for logging
            config["logging"]["logging-channel-group-id"] = category_id
            config["logging"]["commands-channel-id"] = commands_channel_id
            config["logging"]["messages-stats-channel-id"] = stats_channel_id
            config["logging"]["members-leaves-channel-id"] = leaves_channel_id
            config["logging"]["members-joins-channel-id"] = joins_channel_id
            config["logging"]["admin-voice-channel"] = voice_channel_id

            #and for roles
            config["roles"]["mod-role-id"] = mod_role.id
            config["roles"]["admin-role-id"] = admin_role.id
            config["roles"]["owner-role-id"] = owner_role.id
            json.dump(config, config_file, indent=4)

        response_str = textwrap.dedent(f"""
            Created channels in category {category.name}:
            \t{text_channels[0].name}
            \t{text_channels[1].name}
            \t{text_channels[2].name}
            \t{text_channels[3].name}
            \t{voice_channels[0].name}
            And roles for mods, owner, admins:
            \t{admin_role.name}
            \t{mod_role.name}
            \t{owner_role.name}
            And saved configuration fo config file
        """)

        embed = discord.Embed(
            title="Cofig succesfull",
            description=response_str,
            color=discord.Color.green()
        )

        interaction.response.send_message(embed=embed, ephemeral=True)



    async def get_logs_by_name(self, interaction: discord.Interaction, username: str):
        await interaction.response.defer(thinking=True)

        response_str = ""
        response_list = await self.__sql.get_messages_by_username(username=username)
        for row in response_list:
            response_str = response_str + str(row) + "\n"

        embeded_messege = discord.Embed(
            title="Logi z bazy danych",
            description=f"Logi dla: {username} \n {response_str}",
            color=discord.Color.from_rgb(46, 255, 137)
        )

        await interaction.followup.send(embed=embeded_messege)
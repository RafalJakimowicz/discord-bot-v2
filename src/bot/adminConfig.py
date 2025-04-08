import discord
import json
from discord.ext import commands
from discord import app_commands
from datetime import datetime
from ..database.postgres_database import Database
import textwrap

class AdminConfig():
    """
    Admin commands class to handle admin inteactions
    """
    def __init__(self, bot: commands.Bot ,config: dict, config_path: str):
        self.bot = bot
        self.config = config
        self.path = config_path
        self.config = {}
        self.load_config()
        self.commands_list = []
        self.__sql = Database()

    def load_config(self):
        """
        Loads config from file to memory
        """
        with open(self.path, 'r', encoding="UTF-8") as config_file:
            self.config = json.load(config_file)

        print(str(self.config))

    def get_commands(self) -> list:
        """
        Gets admin commands to bot parent object 

        :return: commands list
        :rtype: list
        """
        self.commands_list = [
            app_commands.Command(
                name="member-logs",
                description="get logs by member username",
                callback=self.get_logs_by_name
            ),
            app_commands.Command(
                name="quick-setup",
                description="makes quick setup for basic logging channels and roles",
                callback=self.quick_setup
            ),
            app_commands.Command(
                name="remove-logging",
                description="remove logging channels and role creted by bot",
                callback=self.remove_setup_channels
            )
        ]
        return self.commands_list
    
    async def make_mod_role(self, guild: discord.Guild) -> discord.Role:
        """
        Makes mod rule for moderators to use it has limited permissions

        :param guild: interaction guild
        :type guild: discord.Guild
        :return: mod role
        :rtype: discord.Role
        """
        stage_mod = discord.Permissions.stage_moderator()
        membership = discord.Permissions.membership()
        mod = stage_mod.value | membership.value | discord.Permissions.DEFAULT_VALUE
        mod_perm = discord.Permissions(mod)
        return await guild.create_role(
            name="Moderator",
            permissions=mod_perm,
            colour=discord.Color.green(),
            hoist=True,
            mentionable=False,
        )
    
    async def make_admin_role(self, guild: discord.Guild) -> discord.Role:
        """
        Makes amdin rule for admins to use it has admin permissons

        :param guild: interaction guild
        :type guild: discord.Guild
        :return: admin role
        :rtype: discord.Role
        """

        return await guild.create_role(
            name="Admin",
            permissions=discord.Permissions.all(),
            colour=discord.Color.red(),
            hoist=True,
            mentionable=False,
        )

    
    async def make_owner_role(self, guild: discord.Guild) -> discord.Role:
        """
        Makes owner rule with all permisions

        :param guild: interaction guild
        :type guild: discord.Guild
        :return: owner role
        :rtype: discord.Role
        """

        return await guild.create_role(
            name="Właściciel",
            permissions=discord.Permissions.all(),
            colour=discord.Color.yellow(),
            hoist=True,
            mentionable=False,
        )
    
    async def create_private_category(self, guild: discord.Guild, roles: list, *, category_name: str = "Logi"):
        """
        Creates private category for logging

        :param guild: guild of category to be added
        :type guild: discord.Guild
        :param roles: roles to have access to this category
        :type roles: list
        :param category_name: category name default='Logi'
        :type category_name: str
        """
        overwrite = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False)
        }

        for role in roles:
            overwrite[role] = discord.PermissionOverwrite(view_channel=True)

        category = await guild.create_category(name=category_name, overwrites=overwrite)

        return category

    async def create_channels_in_category(self, guild: discord.Guild, category: discord.CategoryChannel) -> tuple:
        """
        Creates channels in category 

        :param guild: guild for channels to be made
        :type guild: discord.Guild
        :param category: category to channels be added to
        :type category: discord.CategoryChannel
        :return: data in format ([text channels],[voice channels])
        :rtype: tuple
        """
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


    async def remove_setup_channels(self, interaction: discord.Interaction):
        """
        Removes all channels and roles created by bot

        :param interaction: inteaction object with member
        :type interaction: discord.Interaction
        """
        await interaction.response.defer(thinking=True)

        #check if user is admin
        if any(member_role.id == self.config["roles"]["owner-role-id"] for member_role in interaction.user.roles):

            #deletes channels
            for channel_key in self.config["logging"]:
                for channel in interaction.guild.channels:
                    if channel.id == self.config["logging"][channel_key]:
                        self.config["logging"][channel_key] = 0
                        await channel.delete()

            #deletes roles
            for role_key in self.config["roles"]:
                for role in interaction.guild.roles:
                    if self.config["roles"][role_key] == role.id:
                        self.config["roles"][role_key] = 0
                        await role.delete()
            
            #updates config file
            with open(self.path, 'w', encoding="UTF-8") as c_file:
                json.dump(self.config, c_file, indent=4)

            await interaction.followup.send("Done")

        else:
            await interaction.followup.send("Incorect role")
            return


                

            

    
    async def quick_setup(self, interaction: discord.Interaction):
        """
        Makes default quick setup for logging channels and basic roles and sends return message to user

        :param interaction: interaction object 
        :type interaction: discord.Interaction
        """

        await interaction.response.defer(thinking=True)

        nonzero = True
        print(str(self.config))
        for key in self.config["logging"]:
            if self.config["logging"][key] == 0:
                nonzero = False
        
        for key in self.config["roles"]:
            if self.config["roles"][key] == 0:
                nonzero = False

        if nonzero:
            await interaction.response.send_message("All variables are already configured")
            return
            
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

        self.load_config()
        with open(self.path, "w+", encoding='utf-8') as config_file:
            #setup variables in config file for logging
            self.config["logging"]["logging-channel-group-id"] = category_id
            self.config["logging"]["commands-channel-id"] = commands_channel_id
            self.config["logging"]["messages-stats-channel-id"] = stats_channel_id
            self.config["logging"]["members-leaves-channel-id"] = leaves_channel_id
            self.config["logging"]["members-joins-channel-id"] = joins_channel_id
            self.config["logging"]["admin-voice-channel"] = voice_channel_id

            #and for roles
            self.config["roles"]["mod-role-id"] = mod_role.id
            self.config["roles"]["admin-role-id"] = admin_role.id
            self.config["roles"]["owner-role-id"] = owner_role.id
            json.dump(self.config, config_file, indent=4)

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

        await interaction.followup.send(embed=embed)



    async def get_logs_by_name(self, interaction: discord.Interaction, username: str):
        """
        Send response message with logs to user

        :param interaction: interaction object with member
        :type interaction: discord.Interaction
        :param username: member username to get logs
        :type username: str
        """
        await interaction.response.defer(thinking=True)

        if interaction.channel.id != self.config["logging"]["commands-channel-id"]:
            await interaction.followup.send("Invalid channel")
            return

        response_str = ""
        response_list = await self.__sql.get_messages_by_username(username=username)
        for row in response_list:
            tmp = ""
            for column in row:
                tmp = tmp + str(column) + " "
            response_str = response_str + tmp + "\n"

        embeded_messege = discord.Embed(
            title="Logi z bazy danych",
            description=f"Logi dla: {username} \n {response_str}",
            color=discord.Color.from_rgb(46, 255, 137)
        )

        await interaction.followup.send(embed=embeded_messege)
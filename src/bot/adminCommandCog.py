import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime

class AdminCog(commands.Cog):
    def __init__(self, bot, config: dict, config_path: str):
        self.bot = bot
        self.config = config
        self.path = config_path
        self.commands_list = []

    def get_commands(self):
        self.commands_list.append(
            app_commands.Command(
                name="member-logs",
                description="get logs by member username",
                callback=self.get_logs_by_name
            )
        )
        return self.commands_list

    async def get_logs_by_name(self, interaction: discord.Interaction, username: str):
        await interaction.response.defer(thinking=True)

        response_str = ""
        response_list = await self.__sql_database.get_messages_by_username(username=username)
        for row in response_list:
            response_str = response_str + str(row) + "\n"

        embeded_messege = discord.Embed(
            title="Database response",
            description=f"logs for: {username} \n {response_str}",
            color=discord.Color.from_rgb(46, 255, 137)
        )

        await interaction.followup.send(embed=embeded_messege)
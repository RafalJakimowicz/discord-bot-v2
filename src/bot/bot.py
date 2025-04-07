import discord
from discord.ext import commands
from discord import app_commands
from ..database.postgres_database import Database
from ..aichat.chatbot import AiChat
from .messagesCog import MessagesCog
from .membersCog import MembersCog

class DiscordBot(commands.Bot):
    def __init__(self, command_prefix, intents, config: dict):
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.config = config
        self.__sql_database = Database()
        self.__ai_chat = AiChat()
        self.commands_list = []
        self.setup_commands()

    async def on_ready(self):
        print(f'Logged as {self.user.name} (ID: {self.user.id})') 

        if(self.config["features"]["messages-logging"] == True):
            await self.add_cog(MessagesCog(self))

        if(self.config["features"]["members-logging"] == True):
            await self.add_cog(MembersCog(self))

        #init database
        self.__sql_database.init_table()
        for user in self.guilds[0].members:
            await self.__sql_database.add_member_to_database(user)

    async def setup_hook(self):
        for command in self.commands_list:
            self.tree.add_command(command)
        await self.tree.sync()

    def setup_commands(self):
        if(self.config["features"]["ai-chat"] == True):
            self.commands_list.append(
                app_commands.Command(
                    name="user-logs",
                    description="gives logs from user",
                    callback=self.get_logs_by_name
                )
            )

        if(self.config["features"]["messages-logging"] == True):
            self.commands_list.append(
                app_commands.Command(
                    name='ask',
                    description="give response from ai chatbot",
                    callback=self.ask_ai,
                )
            )

    
    async def ask_ai(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer(thinking=True)

        response_from_chat = await self.__ai_chat.get_response(query=query)
        embeded_message = discord.Embed(
            title="Deepseek says",
            description=f"{query}: \n {response_from_chat}",
            color=discord.Color.from_rgb(46, 255, 137)
        )

        await interaction.followup.send(embed=embeded_message)

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
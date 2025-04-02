import discord
from discord.ext import commands
from discord import app_commands
from ..database.postgres_database import Database
from ..aichat.chatbot import AiChat
from datetime import datetime

class DiscordBot(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.__sql_database = Database()
        self.__ai_chat = AiChat()
        self.commands_list = []
        self.setup_commands()
        pass

    async def on_ready(self):
        print(f'Logged as {self.user.name} (ID: {self.user.id})') 
        for g in self.guilds:
            #create table for every guild bot is in
            self.__sql_database.init_table(g.name)
            for m in g.members:
                await self.__sql_database.add_member_to_database(m.id, m.global_name, True, False, g.name)

    async def setup_hook(self):
        for command in self.commands_list:
            self.tree.add_command(command)
        await self.tree.sync()

    def setup_commands(self):
        self.commands_list = [
            app_commands.Command(
                name='ask',
                description="give response from ai chatbot",
                callback=self.ask_ai,
            ),
            app_commands.Command(
                name="user-logs",
                description="gives logs from user",
                callback=self.get_logs_by_name
            )
        ]

    
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
            response_str = response_str + row[0] + "\n"

        embeded_messege = discord.Embed(
            title="Database response",
            description=f"logs for: {username} \n {response_str}",
            color=discord.Color.from_rgb(46, 255, 137)
        )

        await interaction.followup.send(embed=embeded_messege)


    
    async def on_message(self, message: discord.Message):

        if message.author == self.user:
            return

        await self.__sql_database.add_message_to_database(
            message.id,
            message.author.id,
            str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            message.guild.name,
            message.channel.name,
            message.content)
        
        await self.process_commands(message)
        return await super().on_message(message)
    
    async def on_member_join(self, member: discord.Member):
        
        if member == self.user:
            return
        
        await self.__sql_database.add_member_to_database(member.id, member.global_name, True, False, member.guild.name)

        return super().on_member_join(member)
    
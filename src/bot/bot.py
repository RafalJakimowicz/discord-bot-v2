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
        
        await self.__sql_database.add_member_to_database(member.id, member.global_name, True, False)

        return super().on_member_join(member)
    
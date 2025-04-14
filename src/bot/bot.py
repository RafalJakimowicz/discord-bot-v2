import discord
from discord.ext import commands
from discord import app_commands
from ..aichat.chatbot import AiChat
from .messages_cog import MessagesCog
from .members_cog import MembersCog
from .admin_config import AdminConfig
from .notes_cog import NotesCog

class DiscordBot(commands.Bot):
    

    def __init__(self, command_prefix, intents, config: dict, config_path: str):
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.config = config
        self.path = config_path
        self.__admin = AdminConfig(
            bot=self,
            config=self.config,
            config_path=self.path
        )
        self.commands_list = []
        self.setup_commands()

    async def on_ready(self):
        print(f'Logged as {self.user.name} (ID: {self.user.id})') 

        if(self.config["features"]["logging"] == True):
            await self.add_cog(MessagesCog(self))
            await self.add_cog(MembersCog(self, self.config))
            await self.add_cog(AdminConfig(self, self.config, self.path))

        if(self.config["features"]["notes"] == True):
            await self.add_cog(NotesCog(self))

        await self.tree.sync()

    async def setup_hook(self):
        for command in self.commands_list:
            self.tree.add_command(command)
        await self.tree.sync()

    def setup_commands(self):
        if(self.config["features"]["ai-chat"] == True):
            self.__ai_chat = AiChat()
            self.commands_list.append(
                app_commands.Command(
                    name="ask",
                    description="give response from ai chatbot",
                    callback=self.ask_ai
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
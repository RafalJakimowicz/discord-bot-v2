import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import random
from ..database.notes_database import Note, Notes_Database

class NotesCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.__sql = Notes_Database()

    @app_commands.command(name="add-note", description="Tworzy nową notatke")
    async def add_note(self, interaction: discord.Interaction, title: str, content: str, 
                       member_1: discord.Member = None, 
                       member_2: discord.Member = None,
                       member_3: discord.Member = None):
        note_id = random.randint(100000, 999999)
        note = Note(
            note_id=note_id,
            author_id=interaction.user.id,
            content=content,
            title=title,
            creation_date=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            members_ids=[member_1,member_2,member_3]
        )
        await self.__sql.add_note(note)
        await interaction.response.send_message("Zapisano")

    @app_commands.command(name="my-notes", description="gets user notes")
    async def get_user_notes(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        notes = await self.__sql.get_all_member_notes(interaction.user)
        embed = discord.Embed(
            title="Twoje notatki",
            color=discord.Color.blue()
        )
        for note in notes:
            embed.add_field(
                name=f"Notatka: {note.note_id}",
                value=note.title,
                inline=True
            )

        await interaction.followup.send(embed=embed)

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
        """
        gets all user notes and displays only their title and id in embeded message

        :param interaction: discord interaction with user
        :type interaction: discord.Interaction

        """
        await interaction.response.defer(thinking=True)
        notes = await self.__sql.get_all_member_notes(interaction.user)
        embed = discord.Embed(
            title="Twoje notatki",
            color=discord.Color.blue()
        )
        for note in notes:
            embed.add_field(
                name=f"Notatka: {note.note_id}",
                value=f"Tytuł: {note.title}",
                inline=False
            )

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="get-note", description="gets note by id")
    async def get_user_note(self, interaction: discord.Interaction, note_id: int):
        """
        command to get note from database by its 6 digit id,
        and send embeded message to user with note data

        :param interaction: discord interaction
        :type interaction: discord.Interaction
        :param note_id: id of note
        :type note_id: int
        """
        await interaction.response.defer(thinking=True)
        note = await self.__sql.get_note_by_id(note_id)
        embed = discord.Embed(
            title=f"Notatka: {note.note_id}",
            color=discord.Color.dark_gold()
        )
        embed.add_field(
            name=note.title,
            value=note.content,
            inline=False
        )
        embed.add_field(
            name="Data",
            value=note.creation_date,
            inline=False
        )
        await interaction.followup.send(embed=embed)

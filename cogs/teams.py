import discord
from discord import app_commands
from discord.ext import commands
from typing import Literal, Optional
import random

def generate_teams(team_size: int, participants: list[discord.Member]) -> list[list[discord.Member]]:
    random.shuffle(participants)
    num_participants = len(participants)
    teams = []

    if num_participants % team_size == 0:
        for i in range(0, len(participants), team_size):
            teams.append(participants[i:i + team_size])

    else:
        for i in range(0, len(participants), team_size):
            teams.append(participants[i:i + team_size])
        passes = 0
        while len(teams[-1]) < team_size - 1:
            print(teams)
            move_player = teams[passes].pop()
            teams[-1].append(move_player)
            passes += 1
            if len(teams) == 2:
                break

    return teams

        

class TeamView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=60)  # Buttons will be active for 60 seconds
        self.bot = bot

    @discord.ui.button(label="Duo", style=discord.ButtonStyle.primary)
    async def duo_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Duo selected!", ephemeral=True)
        print(self.bot.lobby_channel.members)

    @discord.ui.button(label="Squads", style=discord.ButtonStyle.primary)
    async def squads_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Squads selected!", ephemeral=True)
        
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Action cancelled!", ephemeral=True)
        self.stop()


class Teams(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="teams", description="Start a team selection event")
    async def teams(self, interaction: discord.Interaction):
        view = TeamView(self.bot)
        await interaction.response.send_message("Choose an option:", view=view, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Teams(bot))

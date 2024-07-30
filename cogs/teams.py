import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Select
import random
import os


def create_games_if_not_exists():
    if not os.path.exists("games.txt"):
        with open("games.txt", "a") as f:
            f.write("0")

def increase_num_games():
    with open("games.txt", mode="r+") as f:
        num_games = int(f.read())
        f.seek(0)
        f.write(str(num_games + 1))
        f.truncate()

def get_num_games():
    with open("games.txt", mode="r") as f:
        num_games = f.read()
    return int(num_games)

def generate_teams(team_size: int, participants: list[discord.Member]) -> list[list[discord.Member]]:
    random.shuffle(participants)
    num_participants = len(participants)
    teams = []

    if num_participants % team_size == 0:
        for i in range(0, len(participants), team_size):
            teams.append(participants[i : i + team_size])
    else:
        for i in range(0, len(participants), team_size):
            teams.append(participants[i : i + team_size])

        while len(teams[-1]) < team_size - 1 and len(teams) > 1:
            for i in range(len(teams) - 2, -1, -1):
                if len(teams[i]) > 1:
                    move_player = teams[i].pop()
                    teams[-1].append(move_player)
                    break

    return teams


async def create_voice_channel(guild: discord.Guild, category_name: str, channel_name: str) -> discord.VoiceChannel:
    category = discord.utils.get(guild.categories, name=category_name)
    channel = discord.utils.get(category.voice_channels, name=channel_name)
    if not channel:
        channel = await category.create_voice_channel(channel_name)
    return channel


class IgnoreMemberMenu(Select):
    def __init__(self, members):
        if not members:
            options = [discord.SelectOption(label="No members available", value="none")]
        else:
            options = [discord.SelectOption(label=member.name, value=str(member.id)) for member in members]

        super().__init__(placeholder="Ignore Member", options=options, min_values=0, max_values=len(options))

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.name != self.original_user:
            await interaction.response.send_message("You didn't start this team selection!", ephemeral=True)
            return
        
        selected_ids = [int(value) for value in self.values]
        self.ignored_members = set(selected_ids)
        selected_labels = [option.label for option in self.options if int(option.value) in self.ignored_members]
        await interaction.response.edit_message(content=f"Ignoring: {', '.join(selected_labels)}", view=self.view)


async def delete_voice_channels(bot):
    category = discord.utils.get(bot.guilds[0].categories, name=bot.CATEGORY_NAME)
    if not category:
        print("Category not found")
        return

    channels_to_delete = [channel for channel in category.voice_channels if channel.name != bot.LOBBY_CHANNEL_NAME]
    for channel in channels_to_delete:
        try:
            await channel.delete()
            print(f"Deleted channel {channel.name}")
        except discord.Forbidden:
            print(f"Missing permissions to delete channel {channel.name}")
        except discord.HTTPException as e:
            print(f"Failed to delete channel {channel.name}: {e}")


class InitialView(View):
    def __init__(self, bot, user_name: str):
        super().__init__(timeout=60)
        self.bot = bot
        self.original_user = user_name
    @discord.ui.button(label="Duo", style=discord.ButtonStyle.primary, custom_id="duo_button")
    async def duo_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.name != self.original_user:
            await interaction.response.send_message("You didn't start this team selection!", ephemeral=True)
            return
        await self.show_secondary_view(interaction, "duo")

    @discord.ui.button(label="Squads", style=discord.ButtonStyle.primary, custom_id="squads_button")
    async def squads_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.name != self.original_user:
            await interaction.response.send_message("You didn't start this team selection!", ephemeral=True)
            return
        await self.show_secondary_view(interaction, "squads")

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger, custom_id="initial_cancel_button")
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.name != self.original_user:
            await interaction.response.send_message("You didn't start this team selection!", ephemeral=True)
            return
        await interaction.response.send_message("Action cancelled!", ephemeral=True)
        self.stop()

    async def show_secondary_view(self, interaction: discord.Interaction, state: str):
        view = SecondaryView(self.bot, state,  self.original_user)
        await interaction.response.edit_message(content="Select options:", view=view)


class SecondaryView(View):
    def __init__(self, bot, state, user_name: str):
        super().__init__(timeout=60)
        self.bot = bot
        self.state = state
        self.ignore_menu = IgnoreMemberMenu(self.bot.lobby_channel.members)
        self.add_item(self.ignore_menu)
        self.original_user = user_name


    @discord.ui.button(label="Generate Teams", style=discord.ButtonStyle.success, custom_id="generate_teams_button")
    async def gen_teams_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.name != self.original_user:
            await interaction.response.send_message("You didn't start this team selection!", ephemeral=True)
            return
        
        ignored_members = getattr(self.ignore_menu, "ignored_members", set())
        members = [member for member in self.bot.lobby_channel.members if member.id not in ignored_members]
        
        if not members:
            await interaction.response.send_message("No valid members to form teams!", ephemeral=True)
            return

        if self.state == "duo":
            team_size = 2
        elif self.state == "squads":
            team_size = 4
        else:
            await interaction.response.send_message("Invalid state!", ephemeral=True)
            return

        teams = generate_teams(team_size, members)
        await self.show_final_view(interaction, teams)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger, custom_id="secondary_cancel_button")
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.name != self.original_user:
            await interaction.response.send_message("You didn't start this team selection!", ephemeral=True)
            return
        await interaction.response.send_message("Action cancelled!", ephemeral=True)
        
        self.stop()

    async def show_final_view(self, interaction: discord.Interaction, teams):
        view = FinalView(self.bot, teams, self.original_user)
        embed = discord.Embed(title=f"Game Number {get_num_games()}", color=discord.Color.blurple())

        for i, team in enumerate(teams):

            embed.add_field(name=f"Team {i + 1}", value="\n".join([member.mention for member in team]), inline=False)

        await interaction.response.edit_message(content="Teams", embed=embed, view=view)


class FinalView(View):
    def __init__(self, bot, teams, user_name: str):
        super().__init__(timeout=60)
        self.bot = bot
        self.teams = teams
        self.original_user = user_name

    @discord.ui.button(label="Move Members", style=discord.ButtonStyle.success, custom_id="move_members_button")
    async def move_members_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        increase_num_games()

        for i, team in enumerate(self.teams):
            channel = await create_voice_channel(self.bot.guilds[0], self.bot.CATEGORY_NAME, f"Team {i + 1}")
            for member in team:
                await member.move_to(channel)

        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger, custom_id="final_cancel_button")
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Action cancelled!", ephemeral=True)
        self.stop()


class Teams(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="teams", description="Start a team selection event")
    async def teams(self, interaction: discord.Interaction):
        await delete_voice_channels(self.bot)
        view = InitialView(self.bot, interaction.user.name)
        await interaction.response.send_message("Choose an option:", view=view, ephemeral=True)

    @app_commands.command(name="clearvc", description="Clear the voice channels the bot has made")
    async def clearvc(self, interaction: discord.Interaction):
        for channel in self.bot.category:
            await channel.delete()
        await interaction.response.send_message("Voice channels have been cleared!", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Teams(bot))
    create_games_if_not_exists()

import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
import configparser
import codecs


load_dotenv()


class Bot(commands.Bot):
    def __init__(self) -> None:
        # Load configuration
        self.config = configparser.ConfigParser()
        self.config.readfp(codecs.open("config.ini", "r", "utf8"))


        self.COMMAND_PREFIX = self.config.get("Settings", "COMMAND_PREFIX")
        self.CATEGORY_NAME = self.config.get("Settings", "CATEGORY_NAME")
        self.LOBBY_CHANNEL_NAME = self.config.get("Settings", "LOBBY_CHANNEL_NAME")
        self.CREATE_CATAGORIES_AND_LOBBY = self.config.getboolean("Settings", "CREATE_CATAGORIES_AND_LOBBY")

        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=self.COMMAND_PREFIX, intents=intents)

    async def on_ready(self):
        print(f"Logged in as {self.user}")
        guild = self.guilds[0]

        # Print all category names and their channels if need to paste in congfig.ini
        for category in guild.categories:
            print(f"Category: {category.name}")
            for channel in category.channels:
                print(f" - Channel: {channel.name}")

        if self.CREATE_CATAGORIES_AND_LOBBY:
            self.category = discord.utils.get(guild.categories, name=self.CATEGORY_NAME)

            if not self.category:
                print("Creating category")
                self.category = await guild.create_category(self.CATEGORY_NAME)

            self.lobby_channel = discord.utils.get(self.category.voice_channels, name=self.LOBBY_CHANNEL_NAME)

            if not self.lobby_channel:
                print("Creating lobby channel")
                self.lobby_channel = await self.category.create_voice_channel(self.LOBBY_CHANNEL_NAME)

    async def setup_hook(self):
        for f in os.listdir("./cogs"):
            if f.endswith(".py") and f != "__init__.py":
                cog_name = f"cogs.{f[:-3]}"
                await self.load_extension(cog_name)

    def run(self) -> None:
        token = os.environ["TOKEN"]
        super().run(token)


if __name__ == "__main__":
    bot = Bot()
    bot.run()

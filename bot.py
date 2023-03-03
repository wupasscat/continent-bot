import os
from multiprocessing import managers
from typing_extensions import Self
import discord
import logging
import logging.handlers
from discord import app_commands
from discord import ui
import asyncio
from typing import Any, Dict, Iterator, List, Optional, Tuple, cast, Literal
from dotenv import load_dotenv
import time
from census_client import main

# Check if bot.py is in a container
def is_docker():
    path = '/proc/self/cgroup'
    return (
        os.path.exists('/.dockerenv') or
        os.path.isfile(path) and any('docker' in line for line in open(path))
    )
# Change secrets variables accordingly
if is_docker() == True: # Use Docker ENV variables
    TOKEN = os.environ['DISCORD_TOKEN']
    API_KEY = os.environ['CENSUS_API_KEY']
else: # Use .env file for secrets
    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')
    API_KEY = os.getenv('API_KEY')

# Configure logging
class CustomFormatter(logging.Formatter): # Formatter

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        dt_fmt = '%m/%d/%Y %I:%M:%S'
        formatter = logging.Formatter(log_fmt, dt_fmt)
        return formatter.format(record)

# Create logger
logging.getLogger('discord.http').setLevel(logging.INFO)
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
handler.setFormatter(CustomFormatter())
logger.addHandler(handler)
# Disable VoiceClient warnings
discord.VoiceClient.warn_nacl = False

# Setup Discord
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# Discord bot stuff

class Buttons(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)
    @discord.ui.button(label="Button",style=discord.ButtonStyle.primary)
    async def blurple_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.style=discord.ButtonStyle.success
        await interaction.response.edit_message(content=f"This is an edited button response!", view=self)

# /continents
@tree.command(name = "continents", description = "See open continents on a server")
async def continents(interaction, server: Literal['Connery', 'Miller', 'Cobalt', 'Emerald', 'Jaeger', 'SolTech']):
    logger.info(f"Command /continents triggered for server {server}!")
    t = time.perf_counter()
    continent_status = await main(server) # get open continents from auraxium and send user selected server to main()
    elapsed = time.perf_counter() - t
    logger.info(f"Response took {round(elapsed, 2)}s")
    # Embed
    embedVar = discord.Embed(
    title=server, description=f"Continents open: {continent_status['num_open']}", color=0x5865F2, timestamp=discord.utils.utcnow())
    embedVar.add_field(name="Amerish", value=continent_status["Amerish"], inline=True)
    embedVar.add_field(name="Esamir", value=continent_status["Esamir"], inline=True)
    embedVar.add_field(name="Hossin", value=continent_status["Hossin"], inline=True)
    embedVar.add_field(name="Indar", value=continent_status["Indar"], inline=True)
    embedVar.add_field(name="Oshur", value=continent_status["Oshur"], inline=True)
    embedVar.add_field(name="\u200B", value="\u200B", inline=True)
    embedVar.set_footer(text=f"Completed in {round(elapsed, 2)}s", icon_url="https://raw.githubusercontent.com/wupasscat/wupasscat/main/profile.png")
    await interaction.response.send_message(embed=embedVar, view=Buttons())

@client.event
async def on_ready():
    await tree.sync()
    logger.info('Bot has logged in as {0.user}'.format(client))

client.run(TOKEN, log_handler=None)
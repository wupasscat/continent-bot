import logging
import logging.handlers
import os
import time
from typing import Literal
import redis.asyncio as redis

import aiosqlite
import discord
from discord import app_commands
from dotenv import load_dotenv

# from census_client import main
from utils import log, is_docker


if is_docker is False:  # Use .env file for secrets if outside of a container
    load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN') or None
LOG_LEVEL = os.getenv('LOG_LEVEL') or 'logging.INFO'
REDIS_HOST = os.getenv('REDIS_HOST') or 'localhost'
REDIS_PORT = os.getenv('REDIS_PORT') or 6379
REDIS_DB = os.getenv('REDIS_DB') or 0
REDIS_PASS = os.getenv('REDIS_PASS') or None


# Create logger
logging.getLogger('discord.http').setLevel(logging.INFO)
# log = logging.getLogger('discord')
# if not LOG_LEVEL:
#     log.setLevel(logging.INFO)
# else:
#     log.setLevel(LOG_LEVEL)

# handler = logging.StreamHandler()
# handler.setFormatter(CustomFormatter())
# log.addHandler(handler)
# Disable VoiceClient warnings
discord.VoiceClient.warn_nacl = False

# Check for continents.db
db_exists = os.path.exists('continents.db')
if db_exists is False:
    log.error("Database does not exist!")

# Setup Discord
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


WORLD_IDS = {
    'connery': 1,
    'miller': 10,
    'cobalt': 13,
    'emerald': 17,
    'jaeger': 19,
    'soltech': 40
}


# Collect data from db and create embed
async def get_from_db(server: str):
    db = await aiosqlite.connect('continents.db')
    sql = f"""
    SELECT * FROM {server}
    """
    r = await redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        password=REDIS_PASS
    )
    async with db.execute(sql) as cursor:  # Execute query
        # Create embed title
        embedVar = discord.Embed(title=server[0].upper() + server[1:],
                                 color=0x5865F2,
                                 timestamp=discord.utils.utcnow())
        row_timestamps = []
        async for row in cursor:
            cont = row[1]  # Row 1 is continents
            cont = cont[0].upper() + cont[1:]  # Captialize
            status_emoji = {
                'open': '🟢 Open  ',
                'closed': '🔴 Closed'
            }
            status = status_emoji[row[2]]  # Format status
            # Create embed fields
            embedVar.add_field(name=cont, value=status, inline=True)
            row_timestamps.append(row[3])  # Record timestamps
        # Blank field to fill 3x3 space
        embedVar.add_field(name="\u200B", value="\u200B", inline=True)
        pop = await r.hgetall(name=f'{server}-population')
        embedVar.add_field(name="Population", value=f"""Total: {pop['average']}
        NC: {pop['nc']}
        TR: {pop['tr']}
        VS: {pop['vs']}""")
        data_age = round(time.time() - max(row_timestamps))
        mm, ss = divmod(data_age, 60)
        hh, mm = divmod(mm, 60)
        if data_age > 600:
            embedVar.set_footer(
              text=f"Data from {hh}h, {mm}m, {ss}s ago",
              icon_url="https://raw.githubusercontent.com/wupasscat/continent-bot/main/assets/exclamation-circle.png")
        else:
            embedVar.set_footer(
              text="All systems operational",
              icon_url="https://raw.githubusercontent.com/wupasscat/continent-bot/main/assets/check-circle.png")
    await db.close()
    return embedVar


# Discord
# Select menu and refresh button
class MyView(discord.ui.View):
    def __init__(self, server):
        super().__init__(timeout=None)
        self.server = server

    @discord.ui.select(
        placeholder = "Select a server",
        min_values = 1,
        max_values = 1,
        options = [
            discord.SelectOption(label="Connery", emoji="🇺🇸", description="US West"),
            discord.SelectOption(label="Miller", emoji="🇪🇺", description="Europe"),
            discord.SelectOption(label="Cobalt", emoji="🇪🇺", description="Europe"),
            discord.SelectOption(label="Emerald", emoji="🇺🇸", description="US East"),
            discord.SelectOption(label="Jaeger", emoji="⚔️", 
                                 description="Community-run events"),
            discord.SelectOption(label="SolTech", emoji="🇯🇵", description="Asia")
        ],
        row = 0
    )
    async def select_callback(self, interaction: discord.Interaction, select):
        selected_server = select.values[0]
        selected_server = selected_server[0].lower() + selected_server[1:]
        embedVar = await get_from_db(selected_server)
        await interaction.response.edit_message(embed=embedVar, view=self)

    @discord.ui.button(label="Refresh", style=discord.ButtonStyle.primary, emoji="🔄", row=1)
    async def refresh_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        log.info(f"Refresh /continents triggered for {self.server[0].upper() + self.server[1:]}")
        embedVar = await get_from_db(self.server)
        await interaction.response.edit_message(embed=embedVar, view=self)
    
    
# /continents
@tree.command(name="continents", description="See open continents on a server")
async def continents(interaction, server: Literal[
        'Connery', 'Miller', 'Cobalt', 'Emerald', 'Jaeger', 'Soltech']):
    log.info(f"Command /continents triggered for {server}")
    server = server[0].lower() + server[1:]
    embedVar = await get_from_db(server)
    await interaction.response.send_message(embed=embedVar, view=MyView(server))


@client.event
async def on_ready():
    await tree.sync()
    log.info('Bot has logged in as {0.user}'.format(client))
    # await main(True)  # Run census_client.py

if __name__ == '__main__':
    client.run(TOKEN, log_handler=None)

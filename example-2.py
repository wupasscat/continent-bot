import os
from dotenv import load_dotenv
import discord
from discord import app_commands



load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@tree.command(name = "test", description = "Test command, please ignore", guild=discord.Object(id=873908844806434846)) #Add the guild ids in which the slash command will appear. If it should be in all, remove the argument, but note that it will take some time (up to an hour) to register the command if it's for all guilds.
async def first_command(interaction):
    await interaction.response.send_message("Success!")

@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=873908844806434846))
    print("Ready!")

client.run(TOKEN)
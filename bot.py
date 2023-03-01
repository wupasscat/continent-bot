import os
from multiprocessing import managers
from typing_extensions import Self
import discord
from discord import app_commands
import asyncio
from typing import Any, Dict, Iterator, List, Optional, Tuple, cast, Literal
import auraxium
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
API_KEY = os.getenv('API_KEY')
GUILD_ID = os.getenv('GUILD_ID')

# Setup Discord
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# Server IDs
world_ids = {
    'Connery': 1,
    'Miller': 10,
    'Cobalt': 13,
    'Emerald': 17,
    'Jaeger': 19,
    'SolTech': 40
}

# A mapping of zone IDs to the region IDs of their warpgates
_WARPGATE_IDS: Dict[int, List[int]] = {
    # Indar
    2: [
        2201,  # Northern Warpgate
        2202,  # Western Warpgate
        2203,  # Eastern Warpgate
    ],
    # Hossin
    4: [
        4230,  # Western Warpgate
        4240,  # Eastern Warpgate
        4250,  # Southern Warpgate
    ],
    # Amerish
    6: [
        6001,  # Western Warpgate
        6002,  # Eastern Warpgate
        6003,  # Southern Warpgate
    ],
    # Esamir
    8: [
        18029,  # Northern Warpgate
        18030,  # Southern Warpgate
        18062,  # Eastern Warpgate
    ],
    # Oshur
    344: [
        18303,  # Northern Flotilla
        18304,  # Southwest Flotilla
        18305,  # Southeast Flotilla
    ],
}

# A mapping of zone IDs to their names since Oshur is not in the API
_ZONE_NAMES: Dict[int, str] = {
    2: "Indar",
    4: "Hossin",
    6: "Amerish",
    8: "Esamir",
    344: "Oshur",
}


def _magic_iter(
        region_data: Dict[str, Any]) -> Iterator[Tuple[int, int]]:
    # DBG returns map data in a really weird data; this iterator just
    # flattens that returned tree into a simple list of (regionId, factionId)
    for row in region_data['Row']:
        row_data = row['RowData']
        yield int(row_data['RegionId']), int(row_data['FactionId'])


async def _get_open_zones(client: auraxium.Client, world_id: int) -> List[int]:

    # Get the queried world
    world = await client.get_by_id(auraxium.ps2.World, world_id)
    if world is None:
        raise RuntimeError(f'Unable to find world: {world_id}')

    # Get the map info for all zones on the given world
    map_data = await world.map(*_WARPGATE_IDS.keys())
    if not map_data:
        raise RuntimeError('Unable to query map endpoint')

    # For each world, check if the owners of the warpgates are the same
    open_zones: List[int] = []
    for zone_map_data in cast(Any, map_data):
        zone_id = int(zone_map_data['ZoneId'])

        owner: Optional[int] = None
        for facility_id, faction_id in _magic_iter(zone_map_data['Regions']):

            # Skip non-warpgate regions
            if facility_id not in _WARPGATE_IDS[zone_id]:
                continue

            if owner is None:
                owner = faction_id
            elif owner != faction_id:
                # Different factions, so this zone is open
                open_zones.append(zone_id)
                break
        else:
            # "break" was never called, so all regions were owned by
            # one faction; zone is closed, nothing to do here
            pass

    return open_zones

async def main(server):
    async with auraxium.Client(service_id=API_KEY) as client:

        # Hard-coded world ID
        # server_id = 17  # Emerald

        # Get corresponding server ID for server name
        for i in world_ids:
            if i == server: # server input from user
                server_id = world_ids[i]

        print(server_id)

        # Perform hacky magic
        open_continents = await _get_open_zones(client, server_id)

        # Print results
        continents_str = ", ".join(_ZONE_NAMES[s] for s in open_continents)
        print(f"{len(open_continents)} continents are open on {server}: {continents_str}")
        # Return results as list
        open_continents_list = []
        for s in open_continents:
            open_continents_list.append(_ZONE_NAMES[s])
        return open_continents_list

# Discord bot stuff

# /continents
@tree.command(name = "continents", description = "See open continents on a server") # Add guild=discord.Object(id=GUILD_ID) if you dont want to wait for discord to register your command
async def continents(interaction, server: Literal['Connery', 'Miller', 'Cobalt', 'Emerald', 'Jaeger', 'SolTech']):
    continentsList = await main(server) # get open continents from auraxium and send user selected server to main()
    # Store initial continent status for embed
    status = {
        'Amerish': ":red_circle: Closed",
        'Esamir': ":red_circle: Closed",
        'Hossin': ":red_circle: Closed",
        'Indar': ":red_circle: Closed",
        'Oshur': ":red_circle: Closed"
    }
    # Update status if Planetside api response contains continent
    for i in continentsList:
        if i in status:
            status[i] = ":green_circle: Open  "
    # Embed
    embedVar = discord.Embed(
    title=server, description=f"Continents open: {len(continentsList)}", color=0x5865F2, timestamp=discord.utils.utcnow())
    embedVar.add_field(name="Amerish", value=status["Amerish"], inline=True)
    embedVar.add_field(name="Esamir", value=status["Esamir"], inline=True)
    embedVar.add_field(name="Hossin", value=status["Hossin"], inline=True)
    embedVar.add_field(name="Indar", value=status["Indar"], inline=True)
    embedVar.add_field(name="Oshur", value=status["Oshur"], inline=True)
    embedVar.add_field(name="\u200B", value="\u200B", inline=True)
    embedVar.set_footer(text="github.com/wupasscat", icon_url="https://raw.githubusercontent.com/wupasscat/wupasscat/main/profile.png")
    await interaction.response.send_message(embed=embedVar)

@client.event
async def on_ready():
    await tree.sync() # Add guild=discord.Object(id=GUILD_ID) if you dont want to wait for discord to register your command
    print('Bot has logged in as {0.user}'.format(client))

client.run(TOKEN)
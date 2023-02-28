import os
from multiprocessing import managers
from typing_extensions import Self
import discord
from discord.ext import commands
import asyncio
from typing import Any, Dict, Iterator, List, Optional, Tuple, cast
import auraxium
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Setup Discord
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(intents=intents, command_prefix='!')

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


#def __init__(self):
#    self.queue = asyncio.Queue(1)

async def main():
    async with auraxium.Client(service_id='s:696969696969') as client:

        # Hard-coded world ID for now
        server_id = 17  # Emerald

        # Perform hacky magic
        open_continents = await _get_open_zones(client, server_id)

        # Report results
        continents_str = ", ".join(_ZONE_NAMES[s] for s in open_continents)
        print(f"{len(open_continents)} continents are open: {continents_str}")
        return continents_str

# Discord bot stuff

@bot.event
async def on_ready():
    print('Bot has logged in as {0.user}'.format(bot))

#    await bot.change_presence(status=discord.Status.idle, activity=discord.Game(name="waiting"))
#    continentsList = await main()
#    if "Oshur" in continentsList: # PAIN
#       await bot.change_presence(status=discord.Status.online, activity=discord.Game(name="Oshur is OPEN"))
#
#    else:
#        await bot.change_presence(status=discord.Status.do_not_disturb, activity=discord.Game(name="Oshur is CLOSED"))
print("test 0")
@bot.command(name='99', help='test')
async def continents(ctx):
    continentsList = await main()
    print(continentsList)
    response = "Open Continents: " + continentsList
    print("Response: ", response, type(response))
    await ctx.send(response)

# TO-DO
# - Make fancy messages (include all continents + status)

asyncio.get_event_loop().run_until_complete(main())
bot.run(TOKEN)
import os
from multiprocessing import managers
from typing_extensions import Self
import logging
import logging.handlers
import asyncio
from typing import Any, Dict, Iterator, List, Optional, Tuple, cast, Literal
import auraxium
from dotenv import load_dotenv
import time
import sqlite3

# Check if bot.py is in a container
def is_docker():
    path = '/proc/self/cgroup'
    return (
        os.path.exists('/.dockerenv') or
        os.path.isfile(path) and any('docker' in line for line in open(path))
    )
# Change secrets variables accordingly
if is_docker() == True: # Use Docker ENV variables
    API_KEY = os.environ['CENSUS_API_KEY']
else: # Use .env file for secrets
    load_dotenv()
    API_KEY = os.getenv('API_KEY')

# Setup sqlite
conn = sqlite3.connect('continents.db')

sql_create_connery_table = """ CREATE TABLE IF NOT EXISTS connery (
                                    id integer PRIMARY KEY,
                                    continent text,
                                    status text
                                ); """
sql_create_miller_table = """ CREATE TABLE IF NOT EXISTS miller (
                                    id integer PRIMARY KEY,
                                    continent text,
                                    status text
                                ); """

sql_create_cobalt_table = """ CREATE TABLE IF NOT EXISTS cobalt (
                                    id integer PRIMARY KEY,
                                    continent text,
                                    status text
                                ); """
sql_create_emerald_table = """ CREATE TABLE IF NOT EXISTS emerald (
                                    id integer PRIMARY KEY,
                                    continent text,
                                    status text
                                ); """
sql_create_jaeger_table = """ CREATE TABLE IF NOT EXISTS jaeger (
                                    id integer PRIMARY KEY,
                                    continent text,
                                    status text
                                ); """

sql_create_soltech_table = """ CREATE TABLE IF NOT EXISTS soltech (
                                    id integer PRIMARY KEY,
                                    continent text,
                                    status text
                                ); """

cur = conn.cursor()

cur.execute(sql_create_connery_table)
cur.execute(sql_create_miller_table)
cur.execute(sql_create_cobalt_table)
cur.execute(sql_create_emerald_table)
cur.execute(sql_create_jaeger_table)
cur.execute(sql_create_soltech_table)

connery = [('1', 'amerish', 'closed'), ('2', 'esamir', 'closed'), ('3', 'hossin', 'closed'), ('4', 'indar', 'closed'), ('5', 'oshur', 'closed')]
cur.executemany("INSERT INTO connery VALUES(?, ?, ?);", connery)
conn.commit()
miller = [('1', 'amerish', 'closed'), ('2', 'esamir', 'closed'), ('3', 'hossin', 'closed'), ('4', 'indar', 'closed'), ('5', 'oshur', 'closed')]
cur.executemany("INSERT INTO miller VALUES(?, ?, ?);", miller)
conn.commit()
cobalt = [('1', 'amerish', 'closed'), ('2', 'esamir', 'closed'), ('3', 'hossin', 'closed'), ('4', 'indar', 'closed'), ('5', 'oshur', 'closed')]
cur.executemany("INSERT INTO cobalt VALUES(?, ?, ?);", cobalt)
conn.commit()
emerald = [('1', 'amerish', 'closed'), ('2', 'esamir', 'closed'), ('3', 'hossin', 'closed'), ('4', 'indar', 'closed'), ('5', 'oshur', 'closed')]
cur.executemany("INSERT INTO emerald VALUES(?, ?, ?);", emerald)
conn.commit()
jaeger = [('1', 'amerish', 'closed'), ('2', 'esamir', 'closed'), ('3', 'hossin', 'closed'), ('4', 'indar', 'closed'), ('5', 'oshur', 'closed')]
cur.executemany("INSERT INTO jaeger VALUES(?, ?, ?);", jaeger)
conn.commit()
soltech = [('1', 'amerish', 'closed'), ('2', 'esamir', 'closed'), ('3', 'hossin', 'closed'), ('4', 'indar', 'closed'), ('5', 'oshur', 'closed')]
cur.executemany("INSERT INTO soltech VALUES(?, ?, ?);", soltech)
conn.commit()

print('\nOriginal Table:')
original = conn.execute("SELECT * FROM emerald")
for row in original:
    print(row)

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
logger = logging.getLogger('census')
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
handler.setFormatter(CustomFormatter())
logger.addHandler(handler)

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

async def main():
    async with auraxium.Client(service_id=API_KEY) as client:
        for i in world_ids: # Servers (named)
            server_id = world_ids[i] # Save server id
            open_continents = await _get_open_zones(client, server_id) # Get open continents of server_id
            # List open continents with names
            named_open_continents = []
            for s in open_continents:
                named_open_continents.append(_ZONE_NAMES[s])
            
            continent_status = {
                'Amerish': 'closed',
                'Esamir': 'closed',
                'Hossin': 'closed',
                'Indar': 'closed',
                'Oshur': 'closed'
            }
            for s in named_open_continents:
                if s in continent_status:
                    continent_status[s] = 'open'
            if i == 'Connery':
                connery = [('1', continent_status['Amerish']), ('2', continent_status['Esamir']), ('3', continent_status['Hossin']), ('4', continent_status['Indar']), ('5', continent_status['Oshur'])]
                cur.executemany("UPDATE connery SET status = ? WHERE id = ?;", connery)
                conn.commit()
            elif i == 'Miller':
                miller = [('1', continent_status['Amerish']), ('2', continent_status['Esamir']), ('3', continent_status['Hossin']), ('4', continent_status['Indar']), ('5', continent_status['Oshur'])]
                cur.executemany("UPDATE miller SET status = ? WHERE id = ?;", miller)
                conn.commit()
            elif i == 'Cobalt':
                cobalt = [('1', continent_status['Amerish']), ('2', continent_status['Esamir']), ('3', continent_status['Hossin']), ('4', continent_status['Indar']), ('5', continent_status['Oshur'])]
                cur.executemany("UPDATE cobalt SET status = ? WHERE id = ?;", cobalt)
                conn.commit()
            elif i == 'Emerald':
                emerald = [('1', 'test'), ('2', continent_status['Esamir']), ('3', continent_status['Hossin']), ('4', continent_status['Indar']), ('5', continent_status['Oshur'])]
                cur.executemany("UPDATE emerald SET status = ? WHERE id = ?;", emerald)
                conn.commit()
            elif i == 'Jaeger':
                jaeger = [('1', continent_status['Amerish']), ('2', continent_status['Esamir']), ('3', continent_status['Hossin']), ('4', continent_status['Indar']), ('5', continent_status['Oshur'])]
                cur.executemany("UPDATE jaeger SET status = ? WHERE id = ?;", jaeger)
                conn.commit()
            elif i == 'SolTech':
                soltech = [('1', continent_status['Amerish']), ('2', continent_status['Esamir']), ('3', continent_status['Hossin']), ('4', continent_status['Indar']), ('5', continent_status['Oshur'])]
                cur.executemany("UPDATE soltech SET status = ? WHERE id = ?;", soltech)
                conn.commit()
            
             #continent_status['Amerish']
asyncio.get_event_loop().run_until_complete(main()) 
print('\nNew Table:')
new = conn.execute("SELECT * FROM emerald")
for row in new:
    print(row)
conn.close()
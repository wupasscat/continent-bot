import pytest

import auraxium
import aiosqlite

import census_client

pytest_plugins = ('pytest_asyncio')

API_KEY = census_client.API_KEY


# Test _get_open_zones()
@pytest.mark.parametrize("server_id", [1, 10, 13, 17, 19, 40])
@pytest.mark.asyncio
async def test_open_zones(server_id):
    async with auraxium.Client(service_id=API_KEY) as client:
        open_continents = await census_client._get_open_zones(client,
                                                              server_id)
        assert type(open_continents) == list


# Test db_setup()
@pytest.mark.parametrize("server", ["connery", "miller", "cobalt", "emerald",
                                    "jaeger", "soltech"])
@pytest.mark.asyncio
async def test_db_setup(server):
    ZONE_NAMES = ['amerish', 'esamir', 'hossin', 'indar', 'oshur']
    await census_client.db_setup()
    db = await aiosqlite.connect('continents.db')
    sql = f"""
    SELECT * FROM {server}
    """
    async with db.execute(sql) as cursor:
        async for row in cursor:
            assert row[1] in ZONE_NAMES
            assert row[2] == 'open' or 'closed'
    await db.close()


@pytest.mark.slow
@pytest.mark.parametrize("server", ["connery", "miller", "cobalt", "emerald",
                                    "jaeger", "soltech"])
@pytest.mark.asyncio
async def test_main(server):
    ZONE_NAMES = ['amerish', 'esamir', 'hossin', 'indar', 'oshur']
    db = await aiosqlite.connect('continents.db')
    sql = f"""
    SELECT * FROM {server}
    """
    initial_timestamp = []
    async with db.execute(sql) as cursor:
        async for row in cursor:
            assert row[1] in ZONE_NAMES
            assert row[2] == 'open' or 'closed'
            initial_timestamp.append(row[3])

    await census_client.main(False)  # False = run once

    updated_timestamp = []
    async with db.execute(sql) as cursor:
        async for row in cursor:
            assert row[1] in ZONE_NAMES
            assert row[2] == 'open' or 'closed'
            updated_timestamp.append(row[3])
    for i in range(len(initial_timestamp)):
        assert initial_timestamp[i] != updated_timestamp[i]

    await db.close()

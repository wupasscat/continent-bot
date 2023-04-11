import os
import requests
import redis
import time
from dotenv import load_dotenv

from utils import is_docker, log


if is_docker is False:  # Use .env file for secrets if outside of a container
    load_dotenv()


LOG_LEVEL = os.getenv('LOG_LEVEL') or 'logging.INFO'
REDIS_HOST = os.getenv('REDIS_HOST') or 'localhost'
REDIS_PORT = os.getenv('REDIS_PORT') or 6379
REDIS_DB = os.getenv('REDIS_DB') or 0
REDIS_PASS = os.getenv('REDIS_PASS') or None


WORLD_IDS = {
    'connery': 1,
    'miller': 10,
    'cobalt': 13,
    'emerald': 17,
    'jaeger': 19,
    'soltech': 40
}


def _get_from_api(world_id: int) -> dict:
    url = f'https://agg.ps2.live/population/{world_id}'
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.ConnectionError as error:
        log.error(error)
    except requests.HTTPError as error:
        log.error(error)
    except requests.Timeout as error:
        log.error(error)
    except requests.TooManyRedirects as error:
        log.error(error)
    except requests.RequestException as error:
        raise SystemExit(error)
    json = response.json()
    return json


def database():
    conn = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        password=REDIS_PASS
    )
    while True:
        for i in WORLD_IDS:
            pop = _get_from_api(world_id=WORLD_IDS[i])
            dict_response = {
                'id': pop['id'],
                'average': pop['average'],
                'nc': pop['factions']['nc'],
                'tr': pop['factions']['tr'],
                'vs': pop['factions']['vs']
            }
            log.info(conn.hset(name=f'{i}-population', mapping=dict_response))
        time.sleep(60)

if __name__=='__main__':
    try:
        database()
    except KeyboardInterrupt:
        raise SystemExit







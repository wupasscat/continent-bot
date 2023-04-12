import os
from dotenv import load_dotenv
import asyncio
import redis

from continentbot import continent, population
from continentbot.utils import log

def is_docker() -> bool:
    path = '/proc/self/cgroup'
    return (
        os.path.exists('/.dockerenv') or
        os.path.isfile(path) and any('docker' in line for line in open(path))
    )


if is_docker is False:  # Use .env file for secrets if outside of a container
    load_dotenv()


LOG_LEVEL = os.getenv('LOG_LEVEL') or 'logging.INFO'
REDIS_HOST = os.getenv('REDIS_HOST') or 'localhost'
REDIS_PORT = os.getenv('REDIS_PORT') or 6379
REDIS_DB = os.getenv('REDIS_DB') or 0
REDIS_PASS = os.getenv('REDIS_PASS') or None


STOPWORD = "STOP"


async def reader(channel: redis.client.PubSub):
    while True:
        message = await channel.get_message(ignore_subscribe_messages=True)
        if message is not None:
            print(f"(Reader) Message Received: {message}")
            if message["data"].decode() == STOPWORD:
                print("(Reader) STOP")
                break


r = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        password=REDIS_PASS
    )


async def startServices():
    log.info("Starting services...")
    continent_task = asyncio.create_task(
        continent(
            redis_host=REDIS_HOST,
            redis_port=REDIS_PORT, 
            redis_db=REDIS_DB, 
            redis_pass=REDIS_PASS
            )
        )
    population_task = asyncio.create_task(
        population(
            
        )
    )
    
    # await continent(redis_host=REDIS_HOST,
    #                              redis_port=REDIS_PORT, 
    #                              redis_db=REDIS_DB, 
    #                              redis_pass=REDIS_PASS
    #                              )
    # log.info("")
    # r.publish("status", "OK")


if __name__=='__main__':
    try:
        asyncio.run(startServices())
    except KeyboardInterrupt:
        raise SystemExit

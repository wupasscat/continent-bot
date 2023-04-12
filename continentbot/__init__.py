from .bot import client
from .census_client import main
from .population import database


def bot_client():
    """Returns the Discord client"""
    return client

def continent(redis_host: str,
              redis_port: int,
              redis_db: int,
              redis_pass: str,
              loop: bool = True
              ):
    """Returns the continent data collector

    Parameters  
    -----------
    redis_host: :class:`str` Redis ip/hostname  
    redis_port: :class:`int` Redis port. The default is `6379`  
    redis_db: :class:`int` Id of your database  
    redis_pass: Optional[:class:`str`] Redis password  
    loop: Optional[:class:`bool`] Set to `False` to run only once

    """
    return main(redis_host, redis_port, redis_db, redis_pass, loop)

def population():
    """Returns the population data collector"""
    return database()



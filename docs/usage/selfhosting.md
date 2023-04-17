# Using Docker (recommended)
[GitHub Packages](https://github.com/wupasscat/continent-bot/pkgs/container/continentbot) (preferred)  
[Docker Hub](https://hub.docker.com/r/wupasscat/continentbot)  

## Docker run
### Prerequisites:
- Docker ([install guide](https://docs.docker.com/engine/install/))
- Redis ([Docker Hub](https://hub.docker.com/_/redis/))
- Discord application with bot ([create one here](https://discord.com/developers/applications))
```{code-block} bash
docker run -d --name continent-bot \
    -e DISCORD_TOKEN= \
    -e API_KEY= \
    -e LOG_LEVEL=INFO \
    -e REDIS_HOST= \
    -e REDIS_PORT=
    -e REDIS_DB=0
    -e REDIS_PASS=
    ghcr.io/wupasscat/continentbot:latest
```
### Environment Variables:
- `DISCORD_TOKEN` found in the "Bot" section of your Discord application
- `API_KEY` Daybreak Games Census API service ID  
    ```{warning}
    Do not use `s:example`! This service ID is heavily rate-limited and will not work.
    It is recommended that you apply for a service ID [here](https://census.daybreakgames.com/#devSignup)
- `REDIS_HOST` IP or hostname of your Redis instance
- `REDIS_PORT` the port that Redis listens on
- `REDIS_DB` the ID of your redis database
- `REDIS_PASS` the password to your Redis instance

<br />

***

<br />

## Docker compose
### Prerequisites:
- Docker ([install guide](https://docs.docker.com/engine/install/))
- Docker compose ([install guide](https://docs.docker.com/compose/install/))
- Redis ([Docker Hub](https://hub.docker.com/_/redis/))
- Discord application with bot ([create one here](https://discord.com/developers/applications))  

From [docker-compose.yml](https://github.com/wupasscat/continent-bot/blob/main/docker-compose.yml):
```{code-block} docker
version: '3.4'
services:
    continentbot:
        container_name: continent-bot
        environment:
            - DISCORD_TOKEN=your discord bot token
            - API_KEY=
            - LOG_LEVEL=INFO
            - REDIS_HOST=
            - REDIS_PORT=
            - REDIS_DB=
            - REDIS_PASS=
        image: 'ghcr.io/wupasscat/continentbot:latest'
```
### Environment Variables:
- `DISCORD_TOKEN` found in the "Bot" section of your Discord application
- `API_KEY` Daybreak Games Census API service ID  
    ```{warning}
    Do not use `s:example`! This service ID is heavily rate-limited and will not work.
    It is recommended that you apply for a service ID [here](https://census.daybreakgames.com/#devSignup)
- `REDIS_HOST` IP or hostname of your Redis instance
- `REDIS_PORT` the port that Redis listens on
- `REDIS_DB` the ID of your redis database
- `REDIS_PASS` the password to your Redis instance


<br />

***

<br />

## Unraid
[Template support thread](https://forums.unraid.net/topic/135184-support-wupasscats-template-repository)
### Prerequisites:
- Unraid Community Apps (CA) plugin ([install guide](https://forums.unraid.net/topic/38582-plug-in-community-applications/))
- Redis ([Docker Hub](https://hub.docker.com/_/redis/))

### Setup:
1. Search for `ps2-continent-bot` in the "Apps" tab of your Unraid dashboard

### Environment Variables:
- `DISCORD_TOKEN` found in the "Bot" section of your Discord application
- `API_KEY` Daybreak Games Census API service ID  
    ```{warning}
    Do not use `s:example`! This service ID is heavily rate-limited and will not work.
    It is recommended that you apply for a service ID [here](https://census.daybreakgames.com/#devSignup)
- `REDIS_HOST` IP or hostname of your Redis instance
- `REDIS_PORT` the port that Redis listens on
- `REDIS_DB` the ID of your redis database
- `REDIS_PASS` the password to your Redis instance


<br />

***

<br />

# Python script

|Contents
--- |
|[Linux](#linux)

## Linux

### Prerequisites:
- `git`
- `python3`
- `python3-pip`
- Redis
- Discord application with bot ([create one here](https://discord.com/developers/applications))

### Setup:
1. Clone the repository  
    ```bash
    git clone https://github.com/wupasscat/continent-bot.git
    cd continent-bot
    ```
2. Install dependencies
    ```bash
    pip install -r requirements.txt
    ```
3. Create `.env` file
    ```bash
    nano .env
    ```
    Your file should look like this:
    ```{code-block} python
    # .env
    DISCORD_TOKEN=your discord bot token
    API_KEY=
    LOG_LEVEL=INFO
    REDIS_HOST=
    REDIS_PORT=
    REDIS_DB=
    REDIS_PASS=
    ```
    - `DISCORD_TOKEN` found in the "Bot" section of your Discord application
    - `API_KEY` Daybreak Games Census API service ID  
        ```{warning}
        Do not use `s:example`! This service ID is heavily rate-limited and will not work.
        It is recommended that you apply for a service ID [here](https://census.daybreakgames.com/#devSignup)
    - `REDIS_HOST` IP or hostname of your Redis instance
    - `REDIS_PORT` the port that Redis listens on
    - `REDIS_DB` the ID of your redis database
    - `REDIS_PASS` the password to your Redis instance

    
4. Run script
    ```bash
    python3 -m bot.py
    ```

# <img src="https://i.imgur.com/83v10CK.png" align="left" height="140"/>continent-bot
A Discord bot for Planetside 2 that checks which continents are open on a server so you don't have to.<br /><br />
## Features
 * [x] Uses slash commands
 * [x] Simple output
## Usage
1. **[Invite Bot](https://discord.com/oauth2/authorize?client_id=1080145429632663623&permissions=274877958208&scope=bot%20applications.commands)**  
2. Summon the bot with `/continents` and input a server
***
## Setup (For advanced users)
This assumes you already have a Discord bot set up
1. Clone this repo
2. Create `.env` file with these contents:
    
    ```python
    # .env
    DISCORD_TOKEN=your discord bot token
    API_KEY=s:example
    ```
    
3. Use pip to install `auraxium` and `discord.py`
4. Run `bot.py`

## To-Do
 * [ ] Make better readme
 * [ ] Add refresh button
 * [ ] Cogs?

## Projects Used
- [Auraxium](https://github.com/leonhard-s/auraxium)
- [discord.py](https://github.com/Rapptz/discord.py)

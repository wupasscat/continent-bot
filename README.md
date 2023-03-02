# <img src="https://i.imgur.com/83v10CK.png" align="left" height="140"/>continent-bot
A Discord bot written in Python for [Planetside 2](https://www.planetside2.com/home) that checks which continents are open on a server so you don't have to.  
![license](https://img.shields.io/github/license/wupasscat/continent-bot) [![CI](https://github.com/wupasscat/continent-bot/actions/workflows/main.yml/badge.svg)](https://github.com/wupasscat/continent-bot/actions/workflows/main.yml)
## Features
✅ Uses slash commands  
✅ Simple output
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
 * [ ] [See Issues](https://github.com/wupasscat/continent-bot/issues)
 * [ ] Cogs?

## Contributing 
File bug reports or suggest new features and changes by creating an [Issue](https://github.com/wupasscat/continent-bot/issues/)  
Feel free to create a pull request

## Credits
- [Auraxium](https://github.com/leonhard-s/auraxium)
- [discord.py](https://github.com/Rapptz/discord.py)  

Special thanks to [leonhard-s](https://github.com/leonhard-s)

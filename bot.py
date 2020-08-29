import discord 
from discord.ext import commands

# load env variables
from dotenv import load_dotenv
load_dotenv()

# get token from env variables
import os
token = os.environ.get("bot_token")


client = commands.Bot(command_prefix ='.')

@client.event
async def on_ready():
    print("bot is ready")
    
client.run(token)
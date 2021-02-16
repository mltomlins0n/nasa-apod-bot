import discord
import os
import requests
import json
from dotenv import load_dotenv
from keep_alive import keep_alive

# Create an instance of a client to connect to discord
client = discord.Client()
# Make the token in .env accessible
load_dotenv()

# The URL to grab apod from
URL = "https://api.nasa.gov/planetary/apod"

@client.event
async def on_ready():
    print("logged in as {0.user}".format(client))
    # Set the bot's presence info
    await client.change_presence(activity = discord.Game("with spacetime"))

@client.event
# test function to confirm the bot is working
async def on_message(message):
    # Stop the bot from replying to itself
    if message.author == client.user:
        return
    
    if message.content.startswith("!test"):
        await message.channel.send("I'm alive")

# Run the web server
keep_alive()
# Run the bot
client.run(os.getenv("TOKEN"))
import discord
import os
import requests
import json
from dotenv import load_dotenv
from keep_alive import keep_alive

# Create an instance of a client to connect to discord
client = discord.Client()
# Make items in the .env accessible
load_dotenv()

# The URL to grab apod from
URL = "https://api.nasa.gov/planetary/apod?&thumbs=true&api_key="
# TODO: make URL for returning X random pics
@client.event
async def on_ready():
    print("logged in as {0.user}".format(client))
    # Set the bot's presence info
    await client.change_presence(activity = discord.Game("with spacetime"))

def getAPOD():
    response = requests.get(URL + os.getenv("API_KEY"))
    data = json.loads(response.text)
    date = data["date"]
    title = data["title"]
    explanation = data["explanation"]
    url = data["url"]
    # Get the HD image if there is one
    if "hdurl" in data:
        hdURL = data["hdurl"]
        discordMessage = title + " " + date + "\n\n" + explanation + "\n\n" + hdURL
    else: # Use the standard image url instead
        discordMessage = title + " " + date + "\n\n" + explanation + "\n\n" + url
    return discordMessage

@client.event
# test function to confirm the bot is working
async def on_message(message):
    # Stop the bot from replying to itself
    if message.author == client.user:
        return
    
    if message.content.startswith("!test"):
        await message.channel.send("I'm alive")

    if message.content.startswith("!apod"):
        apod = getAPOD()
        await message.channel.send(">>> " + apod)

# Run the web server
keep_alive()
# Run the bot
client.run(os.getenv("TOKEN"))
import discord
import os
import requests
import json
import asyncio
from dotenv import load_dotenv
from keep_alive import keep_alive

# Create an instance of a client to connect to discord
client = discord.Client()
# Make items in the .env accessible
load_dotenv()

# The URL to grab apod from
URL = "https://api.nasa.gov/planetary/apod?&api_key="
request = requests.get(URL + os.getenv("API_KEY"))
multiplePicsRequest = requests.get(URL + os.getenv("API_KEY") + "&count=3")

@client.event
async def on_ready():
    print("logged in as {0.user}".format(client))
    # Set the bot's presence info
    await client.change_presence(activity = discord.Game("with spacetime 🔭 🪐"))

'''
#Parse the response from the API and create a discord message
#Param: response - the response from the API request
'''
def getAPOD(response):
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

async def post_to_discord():
    await client.wait_until_ready()
    counter = 0
    channel = client.get_channel(811674409861382214) # nasa apod channel
    apod = getAPOD(request)
    while not client.is_closed():
        counter += 1
        #await channel.send("test " + str(counter))
        await channel.send(">>> " + apod)
        await asyncio.sleep(24*60*60) # Task runs every 24 hours

@client.event
async def on_message(message):
    # Stop the bot from replying to itself
    if message.author == client.user:
        return
    
    # test to confirm the bot is online
    if message.content.startswith("!test"):
        await message.channel.send("I'm alive :thumbsup:")

    if message.content.startswith("!apod"):
        apod = getAPOD(request)
        await message.channel.send(">>> " + apod)

# Run the web server
keep_alive()
# create the background task and run it in the background
bg_task = client.loop.create_task(post_to_discord())
# Run the bot
client.run(os.getenv("TOKEN"))
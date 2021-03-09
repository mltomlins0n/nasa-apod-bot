import discord
import os
import requests
import json
import asyncio
import datetime
from dotenv import load_dotenv
from keep_alive import keep_alive

# Create an instance of a client to connect to discord
client = discord.Client()
# Make items in the .env accessible
load_dotenv()

@client.event
async def on_ready():
    print("logged in as {0.user}".format(client))
    # Set the bot's presence info
    await client.change_presence(activity = discord.Game("with spacetime 🔭 🪐"))

'''
Get today's date to pass to get_apod so that it gets the correct pic every day
current_date will be set when the bot is run and needs to be incremented
using datetime.timedelta
'''
def get_date():
    # open file to store dates
    with open("dates.json", "r") as f:
        posted = json.load(f)
    
    current_date = datetime.date.today()
    
    while True: # If current date is yesterday, get today's date
        if current_date.strftime("%F") in posted["dates"]:
            current_date -= datetime.timedelta(1)
        else:
            break

    # save the new current date
    api_date = current_date.strftime("%F")
    # add date to file
    posted["dates"].append(api_date)
    
    # write back to file
    with open("dates.json", "w") as f:
        json.dump(posted, f)
    return api_date

'''
Parse the response from the API and create a discord message
Param: response - the response from the API request
Returns: discordMessage - the formatted message to put in the discord
'''
def get_apod(api_date):
    # The URL to grab apod from
    url = "https://api.nasa.gov/planetary/apod?&api_key={}&date={}".format(os.getenv("API_KEY"), api_date)
    request = requests.get(url)
    data = json.loads(request.text)
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

'''
Gets the appropriate discord channel and posts the message
'''
async def post_to_discord():
    await client.wait_until_ready()
    channel = client.get_channel(811674409861382214) # nasa apod channel
    apod = get_apod(get_date())
    while not client.is_closed():
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
        current_date = datetime.date.today()
        apod = get_apod(current_date)
        await message.channel.send(">>> " + apod)

# Run the web server
keep_alive()
# create the background task and run it in the background
bg_task = client.loop.create_task(post_to_discord())
# Run the bot
client.run(os.getenv("TOKEN"))
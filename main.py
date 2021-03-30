import discord
import os
import requests
import json
import asyncio
import time
from datetime import datetime, timedelta
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
Get today's date to pass to get_apod, and write it to a file
to have a record of posted pics
'''
def get_date():
    # open file to store dates
    with open("dates.json", "r") as f:
        posts = json.load(f)
    
    current_date = datetime.today()

    # save the new current date
    api_date = current_date.strftime("%F")
    # add date to file
    posts["dates"].append(api_date)
    
    # write back to file
    with open("dates.json", "w") as f:
        json.dump(posts, f)
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
    while not client.is_closed():
        apod = get_apod(get_date())
        await channel.send(">>> " + apod)
        await asyncio.sleep(24*60*60) # Task runs every 24 hours

'''
Get all pics from current date to the first pic
'''
async def get_archive():
    current_date = datetime.today()
    api_date = current_date.strftime("%Y-%m-%d")
    channel = client.get_channel(825045193375744011) # archive channel
    while api_date != "1995-06-15": # 1995-06-15 to get every pic
        try:
            apod = get_apod(api_date)
            # convert api_date to a datetime object so it can be decremented
            date_obj = datetime.strptime(api_date, "%Y-%m-%d")
            # Decrement the date to get the previos pic
            date_obj -= timedelta(1)
            # convert back to string so get_apod() works
            api_date = date_obj.strftime("%Y-%m-%d")
            await channel.send(">>> " + apod)
        except KeyError:
            await channel.send(">>> " + "No data available for date: " + api_date)
            date_obj -= timedelta(1)
            api_date = date_obj.strftime("%Y-%m-%d")
        time.sleep(0.2)

@client.event
async def on_message(message):
    # Stop the bot from replying to itself
    if message.author == client.user:
        return
    
    # test to confirm the bot is online
    if message.content.startswith("!test"):
        await message.channel.send("I'm alive :thumbsup:")

    if message.content.startswith("!apod"):
        apod = get_apod(get_date())
        await message.channel.send(">>> " + apod)

    if message.content.startswith("!archive"):
        await get_archive()

# Run the web server
keep_alive()
# create the background task and run it in the background
bg_task = client.loop.create_task(post_to_discord())
# Run the bot
client.run(os.getenv("TOKEN"))
import discord
import os
import requests
import json
import asyncio
import time
import random
import datetime
from datetime import timedelta
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
Retuns: api_date - a date string used in the API call
'''
def get_date():
    # open file to store dates
    with open("dates.json", "r") as f:
        posts = json.load(f)
    
    current_date = datetime.date.today()

    # save the new current date
    api_date = current_date.strftime("%F")
    # add date to file
    posts["dates"].append(api_date)
    
    # write back to file
    with open("dates.json", "w") as f:
        json.dump(posts, f)
    return api_date

'''
Generates a random date which gets a random apod when passed to the API
Returns: rand_date - a random date string to be used in the API call
'''
def get_random_date():
    start_date = datetime.date(1995, 6, 16) # First NASA apod image
    end_date = datetime.date.today()
    time_delta = end_date - start_date # Get the diff between start and end dates
    days_delta = time_delta.days # Convert to an int
    # Generate random int between start and end date
    rand_days = random.randrange(days_delta)
    rand_date = start_date + timedelta(days=rand_days) # Convert to a datetime object
    rand_date = rand_date.strftime("%F") # Convert to a string for the API
    return rand_date

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
    # Get the HD image if there is one
    if "hdurl" in data:
        hdURL = data["hdurl"]
        discordMessage = title + " " + date + "\n\n" + explanation + "\n\n" + hdURL
    elif "url" in data: # Use the standard image url instead
        url = data["url"]
        discordMessage = title + " " + date + "\n\n" + explanation + "\n\n" + url
    else: # For pics without urls
        discordMessage = title + " " + date + "\n\n" + explanation
    return discordMessage

'''
Gets the appropriate discord channel and posts the message
Params: - channel_id - the ID of the discord channel to post in
'''
async def post_to_discord(channel_id):
    await client.wait_until_ready()
    channel = client.get_channel(channel_id) # nasa apod channel
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
            date_obj = datetime.strptime(api_date, "%Y-%m-%d")
            date_obj -= timedelta(1)
            api_date = date_obj.strftime("%Y-%m-%d")
        time.sleep(0.5)

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

    if message.content.startswith("!random"):
        apod = get_apod(get_random_date())
        await message.channel.send(">>> " + apod)

# Run the web server
keep_alive()
# create the background task and run it
bg_task = client.loop.create_task(post_to_discord(811674409861382214))
# Run the bot
client.run(os.getenv("TOKEN"))
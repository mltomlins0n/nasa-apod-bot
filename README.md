# NASA_APOD Bot

A bot to grab NASA's Astronomy Picture of the Day and post it in your Discord.

When run, the bot will get today's Astronomy Pic of the Day and post it in the channel of your choice, just put your channel's ID in `post_to_discord(your channel id here)`. It will do this every 24 hours as long as it is still running.

## Commands:

`!test` - Get a response from the bot to make sure it's online.

`!apod` - Get today's Astronomy Pic of the Day.

`!archive` - Get every pic from today's date to the date of the first submission (16/06/1995) 
**WARNING - This will return over 9000 results and spam the channel for about 3 hours. I only made this command to see if I could.**

`!random` - Get a random image from the archive.
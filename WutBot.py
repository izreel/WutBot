'''
"Simple" bot for Discord to play songs from Youtube until I decided to add more features.
'''
import discord
from discord.ext import commands
import json
import asyncio
from commands import misc, audio_records, music_player, image_classifier

#reads config file containing information such as token and youtube download data
with open('key.config') as json_file:
    data = json.load(json_file)

WutBot = commands.Bot(command_prefix= '$')
records = audio_records.AudioRecords(data["youtube_dl"])

#lists all songs stored in discord at time of startup
@WutBot.event
async def on_ready():
    channel = misc.get_channel(WutBot.guilds[0], 'song-list')

    print('We have logged in as {0.user}'.format(WutBot))
    print('Deleting old messages from song-list')
    await channel.purge()

    print('Printing list on song-list')
    audio_list = misc.get_audio_list(channel, records)

    for partial_list in audio_list:
        await channel.send(partial_list)
                    
@WutBot.command()
async def summon(ctx):
    await ctx.channel.send('Cannot summon. Not enough sacrifices.')

WutBot.add_cog(music_player.MusicPlayer(WutBot, data))
WutBot.add_cog(image_classifier.ImageClassifier(WutBot, data))
WutBot.run(data["token"])
print('Shutting down, updating records')
records.update()
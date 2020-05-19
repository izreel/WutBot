'''
Simple bot for Discord to play songs from Youtube until I decided to add more features.
'''
import discord
from discord.ext import commands
import json
import audio_records
import asyncio
import random

#reads config file containing information such as token and youtube download data
with open('key.config') as json_file:
    data = json.load(json_file)

wut_bot = commands.Bot(command_prefix= '$')
records = audio_records.AudioRecords(data)

'''
list containing songs in queue
each element is a tuple containing path of audio and title of video (audio)
'''
audio_queue = []

#used for listing all stored songs in song-list channel in discord
def get_list_channel():
    for channel in wut_bot.guilds[0].channels:
        if channel.name == 'song-list':
            return channel

#lists all songs stored in discord at time of startup
@wut_bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(wut_bot))
    
    record_list = records.get_records()
    audio_list = '`'
    
    for row in record_list.index:
        audio_list += records.get_audio_record(row)
        if row % 30 == 0 and row > 0:
            await get_list_channel().send(audio_list+ '`')
            audio_list = '`'
                    
    await get_list_channel().send(audio_list +'`')

'''
functions for joining voice channel.
First function joins voice channel using command but call second function (due to decorator).
Second function actually makes bot join voice.
'''
@wut_bot.command(description= 'Connects to voice channel')
async def join(message):
    await join_voice(message)

async def join_voice(message):
    channel = message.author.voice.channel
    await channel.connect()

@wut_bot.command(descrpition= 'Disconnects from voice channel')
async def leave(message):
    if wut_bot.voice_clients:
        await wut_bot.voice_clients[0].disconnect()
    else:
        await message.channel.send('Not in a voice channel')

@wut_bot.command(description= 'Pause any audio playing')
async def pause(message):
    if wut_bot.voice_clients[0].is_playing():
        wut_bot.voice_clients[0].pause()

@wut_bot.command(description= 'Resumes playing audio')
async def resume(message):
    if wut_bot.voice_clients[0].is_paused():
        wut_bot.voice_clients[0].resume()

@wut_bot.command(description= 'Tells you to look at song-list u fk')
async def songlist(message):
    await message.channel.send('check song-list channel')

@wut_bot.command(description= 'Skips song/audio')
async def skip(message):
     wut_bot.voice_clients[0].stop()

@wut_bot.command(aliases= 'current', description= 'Displays current song/audio playing')
async def current_song(message):
    await message.channel.send('Playing: ' + audio_queue[0][1])

@wut_bot.command(description= 'Displays all songs/audio currently in queue alongside current song playing')
async def queue(message):
    queue_list = '`Currently in queue:\n'
    
    for i,j in enumerate(audio_queue):
        queue_list += str(i) + ' ' + j[1]+ '\n'
        if i % 30 == 0 and i > 0:
            await message.channel.send(queue_list+'`')
            queue_list = '`'    
    
    await message.channel.send(queue_list+'`')

'''
Adds audio to queue. If nothing is playing, the audio that was just added to the queue gets played.
Otherwise, send message to server about which audio was added to the queue. 
'''
async def play_audio(message, audio_file):
    def update_queue():
        if audio_queue:
            try:
                audio_queue.pop(0)
                audio_source = discord.FFmpegOpusAudio(audio_queue[0][0])
                wut_bot.voice_clients[0].play(audio_source, after= lambda e: update_queue())
                print(f'playing {audio_queue[0][1]}')
            except:
                print('queue empty')
    
    if not wut_bot.voice_clients:
        await join_voice(message)
    
    audio_queue.append(audio_file)
    
    if not wut_bot.voice_clients[0].is_playing():
        audio_source = discord.FFmpegOpusAudio(audio_queue[0][0])
        wut_bot.voice_clients[0].play(audio_source, after= lambda e: update_queue())
    else:
        await message.channel.send(f'adding to {audio_file[0][1]} queue')

'''
expected usage: $play [youtube link or integer]
When called on, checks if user has included a youtube link or a number.
If input is a number, get audio file and title if number is a valid index in audio records.
If input is a youtube link, download audio if it has not been downloaded yet and get audio and title. Also it will update records if it needs to download.
Once audio file is received, call play_audio function.
'''
@wut_bot.command(description= 'plays audio from youtube link or from list of audio available')
async def play(message):
    if 'https://www.youtube.com/watch?v=' not in message.content:
        try:
            file_num = int(message.content.split(' ')[1])
            audio_file = records.get_file(records.get_records().loc[file_num, 'id'])   
        except:
            await message.channel.send('Choose a valid number from list or give a proper youtube link')
            return
    else:
        video_url = message.content.split(' ')[1]
        try:
            audio_file = records.add(video_url)
        except:
            await message.channel.send('Error while getting ready to play, try again')
            return
                
        await get_list_channel().send('`'+ records.get_latest_record() +'`')

    await play_audio(message, audio_file)

'''
Picks random number from 0 to total number of available (downloaded) audio and adds it to queue through play_audio function.
'''
@wut_bot.command(aliases= 'random', description= 'Plays random song/audio from song list')
async def randomsong(message):
    song_number = random.randint(0, records.record_length()-1)
    audio_file = records.get_file(records.get_records().loc[song_number, 'id'])

    await play_audio(message, audio_file)

wut_bot.run(data.get("token"))
records.update()
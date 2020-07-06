'''
Simple bot for Discord to play songs from Youtube until I decided to add more features.
'''
import discord
from discord.ext import commands
import json
import audio_records
import asyncio
import numpy as np
import cv2
import tensorflow as tf
import requests
import shutil

#reads config file containing information such as token and youtube download data
with open('key.config') as json_file:
    data = json.load(json_file)

wut_bot = commands.Bot(command_prefix= '$')
records = audio_records.AudioRecords(data["youtube_dl"])
classification_model = tf.keras.models.load_model(data["model_weights"])

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

async def delete_previous_list():
    channel = get_list_channel()

    await channel.purge()

#lists all songs stored in discord at time of startup
@wut_bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(wut_bot))
    print('Deleting old messages from song-list')
    await delete_previous_list()

    print('Printing list on song-list')
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
async def join(ctx):
    await join_voice(ctx)

async def join_voice(ctx):
    channel = ctx.author.voice.channel
    await channel.connect()

@wut_bot.command(descrpition= 'Disconnects from voice channel')
async def leave(ctx):
    if wut_bot.voice_clients:
        await wut_bot.voice_clients[0].disconnect()
    else:
        await ctx.channel.send('Not in a voice channel')

@wut_bot.command(description= 'Pause any audio playing')
async def pause(ctx):
    if wut_bot.voice_clients[0].is_playing():
        wut_bot.voice_clients[0].pause()

@wut_bot.command(description= 'Resumes playing audio')
async def resume(ctx):
    if wut_bot.voice_clients[0].is_paused():
        wut_bot.voice_clients[0].resume()

@wut_bot.command(description= 'Tells you to look at song-list u fk')
async def songlist(ctx):
    await ctx.channel.send('check #song-list channel')

@wut_bot.command(description= 'Skips song/audio')
async def skip(ctx):
    wut_bot.voice_clients[0].stop()

@wut_bot.command(description= 'Displays current song/audio playing')
async def current(ctx):
    await ctx.channel.send('Playing: ' + audio_queue[0][1])

@wut_bot.command(description= 'Displays all songs/audio currently in queue alongside current song playing')
async def queue(ctx):
    queue_list = '`Currently in queue:\n'
    
    for i,j in enumerate(audio_queue):
        queue_list += str(i) + ' ' + j[1]+ '\n'
        if i % 30 == 0 and i > 0:
            await ctx.channel.send(queue_list+'`')
            queue_list = '`'    
    
    await ctx.channel.send(queue_list+'`')

'''
Adds audio to queue. If nothing is playing, the audio that was just added to the queue gets played.
Otherwise, send ctx to server about which audio was added to the queue. 
'''
async def play_audio(ctx, audio_file, queue_message= True):
    def update_queue():
        if audio_queue:
            try:
                audio_queue.pop(0)
                audio_source = discord.FFmpegOpusAudio(audio_queue[0][0])
                print(f'playing {audio_queue[0][1]}')
                wut_bot.voice_clients[0].play(audio_source, after= lambda e: update_queue())
            except:
                print('queue is now empty')
    
    if not wut_bot.voice_clients:
        await join_voice(ctx)
    
    audio_queue.append(audio_file)
    
    if not wut_bot.voice_clients[0].is_playing() and len(audio_queue) == 1:
        audio_source = discord.FFmpegOpusAudio(audio_file[0])
        await ctx.channel.send(f'Playing {audio_file[1]}')
        wut_bot.voice_clients[0].play(audio_source, after= lambda e: update_queue())
    elif queue_message:
        await ctx.channel.send(f'adding {audio_file[1]} to queue')

'''
expected usage: $play [youtube link or integer]
When called on, checks if user has included a youtube link or a number.
If input is a number, get audio file and title if number is a valid index in audio records.
If input is a youtube link, download audio if it has not been downloaded yet and get audio and title. Also it will update records if it needs to download.
Once audio file is received, call play_audio function.
'''
@wut_bot.command(description= 'plays audio from youtube link or from list of audio available')
async def play(ctx):
    
    if 'https://www.youtube.com/watch?v=' not in ctx.message.content:
        try:
            file_num = int(ctx.message.content.split(' ')[1])
            audio_file = records.get_file(records.get_records().loc[file_num, 'id'])   
        except:
            await ctx.channel.send('Choose a valid number from list or give a proper youtube link')
            return
    else:
        video_url = ctx.message.content.split(' ')[1]
        try:
            audio_file = records.add(video_url)
        except:
            await ctx.channel.send('Error while getting ready to play, try again')
            return
     
        await get_list_channel().send('`'+ records.get_latest_record() +'`')

    await play_audio(ctx, audio_file)

'''
Picks one or several random numbers from 0 to total number of available (downloaded) audio and adds it to queue through play_audio function.
'''
@wut_bot.command(aliases= ['random'], description= 'Plays random song/audio from song list')
async def randomsong(ctx):
    #if no number in ctx
    if ctx.message.content in ['$random', '$randomsong']:
        song_number = np.random.randint(records.record_length())
        audio_file = records.get_file(records.get_records().loc[song_number, 'id'])

        await play_audio(ctx, audio_file)
    else:
        random_numbers = int(ctx.message.content.split(' ')[1])
    
        if random_numbers < records.record_length() and random_numbers > 0:
            audio_choices = np.random.choice(records.record_length(), random_numbers, False)
            
            for i in audio_choices:
                audio_file = records.get_file(records.get_records().loc[i, 'id'])
                await play_audio(ctx, audio_file, False)
            
            await ctx.channel.send(f'Added {random_numbers} songs to queue')
        else:
            await ctx.channel.send(f'Pick a valid number from 1 to {records.record_length()}')

#download an image from a given URL. Mainly used when $classify command also includes a url instead of an attachment
def download_image(url):
    r = requests.get(url, stream= True)

    if r.status_code == 200:
        r.raw.decode_content = True
        with open(data["images"], 'wb') as f:
            shutil.copyfileobj(r.raw, f)
            f.close()
    else:
        return False


#gets image and modifies it so that it can be fed to the model
def get_image():
    image = cv2.imread(data["images"])
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = cv2.resize(image, (200,200))
    image = np.expand_dims(image, axis= 0)
    return image

'''
Given an input of an image(s) or url of an image, use a neural network to classify them as either a dog or cat picture.
'''
@wut_bot.command()
async def classify(ctx):
    results = []
    
    #loops every attachment added to command call and classifies them one by one
    for attachment in  ctx.message.attachments:
        await attachment.save(data["images"])
        result = classification_model.predict(get_image())
        results.append(result.round())

    #loops through every url given and downloads image from url and classifies them one by one
    for embed in ctx.message.embeds:
        image_url = embed.url
        
        if not download_image(image_url):
            await ctx.channel.send('Could not properly download image')
            return
        
        result = classification_model.predict(get_image())
        results.append(result.round())
    
    if len(results) > 1:
        result_output = 'The following from top to bottom are: '
    elif len(results) == 1:
        result_output = 'This is a '
    else:
        result_output = 'Nothing to classify, try again'

    for result in results:
        if result == 1:
             result_list += 'Dog '
        else:
            result_list+= 'Cat '
    
    await ctx.channel.send(result_output)

wut_bot.run(data.get("token"))
print('Shutting down, updating records')
records.update()
import discord
import json
import audio_records
import asyncio

with open('key.config') as json_file:
    data = json.load(json_file)

client = discord.Client()
records = audio_records.AudioRecords(data)

#file name?
audio_queue = []

def test_print(m):
    m.channel.send('testing')

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    def update_queue():
        if audio_queue:
            try:
                audio_queue.pop(0)
                audio_source = discord.FFmpegOpusAudio(audio_queue[0][0])
                client.voice_clients[0].play(audio_source, after= lambda e: update_queue())
            except:
                print('queue empty')

    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('hello')  
    
    if message.content.startswith('$join'):
        channel = message.author.voice.channel
        await channel.connect()
    
    if message.content.startswith('$leave') and client.voice_clients:
        await client.voice_clients[0].disconnect()
    
    if message.content.startswith('$play'):
        
        if 'https://www.youtube.com/watch?v=' not in message.content:
            try:
                file_num = int(message.content.split(' ')[1])
            except:
                await message.channel.send('Choose a valid number from list or give a proper youtube link')
                return
            audio_file = records.get_file(records.get_records().loc[file_num, 'id'])    
        else:
            video_url = message.content.split(' ')[1]
            try:
                audio_file = records.add(video_url)
            except:
                await message.channel.send('Error while getting ready to play')
                return

        if not client.voice_clients:
            channel = message.author.voice.channel
            await channel.connect()
        
        audio_queue.append(audio_file)
        if not client.voice_clients[0].is_playing():
            audio_source = discord.FFmpegOpusAudio(audio_queue[0][0])
            client.voice_clients[0].play(audio_source, after= lambda e: update_queue())
        else:
            await message.channel.send('adding to queue')
    
    if message.content.startswith('$pause') and client.voice_clients[0].is_playing():
        client.voice_clients[0].pause()

    if message.content.startswith('$resume') and client.voice_clients[0].is_paused():
        client.voice_clients[0].resume()
    
    if message.content.startswith('$list'):
        record_list = records.get_records()
        audio_list = ''
        for row in record_list.index:
            audio_time = f'{int(record_list.loc[row, "duration"]/60)}:{record_list.loc[row, "duration"]%60:02d}'
            audio_list += f'{row} {record_list.loc[row, "title"]} ' + audio_time+ '\n'
        
        await message.channel.send(audio_list)
        return 
    
    if message.content.startswith('$skip'):
        client.voice_clients[0].stop()
    
    if message.content.startswith('$current'):
        await message.channel.send('Playing: ' + audio_queue[0][1])
    
    if message.content.startswith('$l'):
        queue_list = 'Currently in queue:\n'
        for i,j in enumerate(audio_queue):
            queue_list += str(i) + ' ' + j[1]+ '\n'
        
        await message.channel.send(queue_list)

client.run(data.get("token"))
records.update()
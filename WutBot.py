import discord
import json
import download_audio
import audio_records

with open('key.config') as json_file:
    data = json.load(json_file)

client = discord.Client()
records = audio_records.AudioRecords()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):

    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('hello')  
    
    elif message.content.startswith('$join'):
        channel = message.author.voice.channel
        await channel.connect()
    
    elif message.content.startswith('$leave') and client.voice_clients:
        await client.voice_clients[0].disconnect()
    
    elif message.content.startswith('$play'):
        
        if 'https://www.youtube.com/watch?v=' not in message.content:
            file_num = int(message.content.split(' ')[1])
            audio_file = download_audio.get_file(records.get_records().loc[file_num, 'id'])    
        else:
            video_url = message.content.split(' ')[1]
            audio_file = download_audio.download(video_url, records)

        try:
            audio_source = await discord.FFmpegOpusAudio.from_probe(audio_file)
        except:
            await message.channel.send('Error while getting ready to play')
            return
        
        if not client.voice_clients:
            channel = message.author.voice.channel
            await channel.connect()

        if not client.voice_clients[0].is_playing():
            client.voice_clients[0].play(audio_source)       
    
    elif message.content.startswith('$pause') and client.voice_clients[0].is_playing():
        client.voice_clients[0].pause()

    elif message.content.startswith('$resume') and client.voice_clients[0].is_paused():
        client.voice_clients[0].resume()
    
    elif message.content.startswith('$list'):
        record_list = records.get_records()
        for row in record_list.index:
            await message.channel.send('{} {}'.format(row, record_list.loc[row, 'title']))


client.run(data.get("token"))
records.update()
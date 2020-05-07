import discord
import json
import youtube_dl

with open('key.config') as json_file:
    data = json.load(json_file)

client = discord.Client()

options = {
    # 'download_archive' : 'Download_Archive',
    'outtmpl' : '%(display_id)s.%(ext)s',
    # 'format' : 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality' : '5'
    }]
}


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):

    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('$hello')  
    
    if message.content.startswith('$join'):
        channel = message.author.voice.channel
        await channel.connect()
    
    if message.content.startswith('$leave') and client.voice_clients:
        await client.voice_clients[0].disconnect()

    if message.content.startswith('$play'):
        video_url = message.content.split(' ')[1]
        audio_file = video_url.split('=')[1] + '.mp3'

        with youtube_dl.YoutubeDL(options) as ydl:
            ydl.download([video_url])
        
        source = await discord.FFmpegOpusAudio.from_probe(audio_file)
        
        channel = message.author.voice.channel
        await channel.connect()
        
        client.voice_clients[0].play(source)

client.run(data.get("token"))

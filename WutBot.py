import discord
import json
import youtube_dl


with open('key.config') as json_file:
    data = json.load(json_file)

download_options = {
    'download_archive' : '/mnt/d/downloaded_audio/already_downloaded.txt',
    'outtmpl' : '/mnt/d/downloaded_audio/%(display_id)s.%(ext)s',
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality' : '5'
    }]
}

client = discord.Client()
audio_queue = []

def download_audio(url):
    audio_file =  '/mnt/d/downloaded_audio/{}.mp3'.format(url.split('=')[1])

    with youtube_dl.YoutubeDL(download_options) as ydl:
        ydl.download([url])
        print(ydl.extract_info(url, download=False)['title'])
    return audio_file


def play_audio():
    client.voice_clients[0].play(audio_queue[0])

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
        audio_source = await discord.FFmpegOpusAudio.from_probe(download_audio(video_url))
        audio_queue.append(audio_source)
        
        if not client.voice_clients:
            channel = message.author.voice.channel
            await channel.connect()

        if not client.voice_clients[0].is_playing():
            client.voice_clients[0].play(audio_source)
            
    if message.content.startswith('$pause') and client.voice_clients[0].is_playing():
        client.voice_clients[0].pause()

    if message.content.startswith('$resume') and client.voice_clients[0].is_paused():
        client.voice_clients[0].resume()

client.run(data.get("token"))

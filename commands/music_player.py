'''
File for audio commands (join, resume, pause)
anything to do with voice and audio consolidated as a class
'''
import discord
from discord.ext import commands
from commands import misc, audio_records
import numpy as np

class MusicPlayer(commands.Cog):
    def __init__(self, bot, data):
        self.bot = bot
        self.records = audio_records.AudioRecords(data["youtube_dl"])
        
        #each element is a tuple containing path of audio and title of video (audio)
        self.audio_queue = []

        self.audio_repeat = False
    
    '''
    function for joining voice channel.
    '''
    async def join_voice(self, ctx):
        channel = ctx.author.voice.channel
        await channel.connect()
    
    '''
    Adds audio to queue. If nothing is playing, the audio that was just added to the queue gets played.
    Otherwise, send ctx to server about which audio was added to the queue. 
    '''
    async def play_audio(self, ctx, audio_file, queue_message= True):
        def update_queue():
            if self.audio_queue:
                try:
                    if not self.audio_repeat:
                        self.audio_queue.pop(0)
                    audio_source = discord.FFmpegOpusAudio(self.audio_queue[0][0])
                    print(f'playing {self.audio_queue[0][1]}')
                    ctx.voice_client.play(audio_source, after= lambda e: update_queue())
                except:
                    print('queue is now empty')
        
        if not ctx.voice_client:
            await self.join_voice(ctx)
        
        self.audio_queue.append(audio_file)
        
        if not ctx.voice_client.is_playing() and len(self.audio_queue) == 1:
            audio_source = discord.FFmpegOpusAudio(audio_file[0])
            await ctx.channel.send(f'Playing {audio_file[1]}')

            ctx.voice_client.play(audio_source, after= lambda e: update_queue())
        elif queue_message:
            await ctx.channel.send(f'adding {audio_file[1]} to queue')

    def interpreter(self, sequence):
        sequence = sequence.split(',')
        song_ranges = []

        for i in sequence:
            if '-' in i:
                i = i.split('-')
                song_ranges.append((int(i[0]), int(i[1])+1))
            else:
                song_num = int(i)
                song_ranges.append((song_num, song_num+1))
        
        return song_ranges

    @commands.command(description= 'Connects to voice channel')
    async def join(self, ctx):
        await self.join_voice(ctx)

    @commands.command(descrpition= 'Disconnects from voice channel')
    async def leave(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
        else:
            await ctx.channel.send('Not in a voice channel')

    @commands.command(description= 'Pause any audio playing')
    async def pause(self, ctx):
        if ctx.voice_client.is_playing():
            ctx.voice_client.pause()

    @commands.command(description= 'Resumes playing audio')
    async def resume(self, ctx):
        if ctx.voice_client.is_paused():
            ctx.voice_client.resume()

    @commands.command(description= 'Tells you to look at song-list u fk')
    async def songlist(self, ctx):
        await ctx.channel.send('check #song-list channel')

    @commands.command(description= 'Skips song/audio')
    async def skip(self, ctx):
        ctx.voice_client.stop()

    @commands.command(description= 'Displays current song/audio playing')
    async def current(self, ctx):
        await ctx.channel.send('Playing: ' + self.audio_queue[0][1])

    @commands.command(description= 'Displays all songs/audio currently in queue alongside current song playing')
    async def queue(self, ctx):
        queue_list = '`Currently in queue:\n'
        
        for i,j in enumerate(self.audio_queue):
            queue_list += str(i) + ' ' + j[1]+ '\n'
            if i % 30 == 0 and i > 0:
                await ctx.channel.send(queue_list+'`')
                queue_list = '`'    
        
        await ctx.channel.send(queue_list+'`')

    '''
    expected usage: $play [youtube link or integer]
    When called on, checks if user has included a youtube link or a number.
    If input is a number, get audio file and title if number is a valid index in audio records.
    If input is a youtube link, download audio if it has not been downloaded yet and get audio and title. Also it will update records if it needs to download.
    Once audio file is received, call play_audio function.
    '''
    @commands.command(description= 'plays audio from youtube link or from list of audio available')
    async def play(self, ctx):
        audio = []
        
        if 'youtube' not in ctx.message.content:
            try:
                song_nums = self.interpreter(ctx.message.content.split(' ')[1])
                for song in song_nums:
                    for i in range(song[0], song[1]):
                        audio.append(self.records.get_file(self.records.get_records().loc[i, 'id']))
            except:
                await ctx.channel.send('Choose a valid number(s) from list or give a proper youtube link')
                return
        else:
            video_url = ctx.message.content.split(' ')[1]
            try:
                audio.append(self.records.add(video_url))
            except:
                await ctx.channel.send('Error while getting ready to play, try again')
                return
        
            await misc.get_channel(ctx.guild, 'song-list').send('`'+ self.records.get_latest_record() +'`')
        
        await self.play_audio(ctx, audio[0])
        if len(audio) > 1:
            for song in audio[1:]:
                await self.play_audio(ctx, song, False)
            await ctx.channel.send(f'Added {len(audio) - 1} songs to queue')

    '''
    Picks one or several random numbers from 0 to total number of available (downloaded) audio and adds it to queue through play_audio function.
    '''
    @commands.command(aliases= ['random'], description= 'Plays random song/audio from song list')
    async def randomsong(self, ctx):
        #if no number in ctx
        if ctx.message.content in ['$random', '$randomsong']:
            song_number = np.random.randint(self.records.record_length())
            audio_file = self.records.get_file(self.records.get_records().loc[song_number, 'id'])

            await self.play_audio(ctx, audio_file)
        else:
            random_numbers = int(ctx.message.content.split(' ')[1])
        
            if random_numbers < self.records.record_length() and random_numbers > 0:
                audio_choices = np.random.choice(self.records.record_length(), random_numbers, False)
                
                for i in audio_choices:
                    audio_file = self.records.get_file(self.records.get_records().loc[i, 'id'])
                    await self.play_audio(ctx, audio_file, False)
                
                await ctx.channel.send(f'Added {random_numbers} songs to queue')
            else:
                await ctx.channel.send(f'Pick a valid number from 1 to {self.records.record_length()}')
    
    @commands.command(aliases= ['clearqueue'], description= 'Clears current queue if not empty. If audio currently playing, it will continue playing while queue is cleared.')
    async def clear(self, ctx):
        print('Clearing queue')
        self.audio_queue.clear()

    @commands.command(description= 'Sets Music Player on repeat')
    async def repeat(self, ctx):
        self.audio_repeat = not self.audio_repeat
        await ctx.channel.send('Setting repeat to ' + str(self.audio_repeat))
import discord
from discord.ext import commands
import json

with open('key.config') as json_file:
    data = json.load(json_file)

client = discord.Client()

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


client.run(data.get("token"))

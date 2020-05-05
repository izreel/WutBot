import discord
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
    
    

client.run(data.get("token"))
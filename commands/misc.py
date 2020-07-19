'''
File for commands that does random things (Send a random message on discord)
'''
import asyncio

#used for listing all stored songs in song-list channel in discord
def get_channel(server, channel_name):
    for channel in server.channels:
        if channel.name == channel_name:
            return channel

def get_audio_list(channel, records):
    record_list = records.get_records()
    audio_list = []
    partial_list = '`'
    
    for row in record_list.index:
        partial_list += records.get_audio_record(row)
        if row % 30 == 0 and row > 0:
            audio_list.append(partial_list + '`')
            partial_list = '`'
    
    return audio_list


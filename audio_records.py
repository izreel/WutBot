import pandas as pd
import youtube_dl

'''
Class used to keep track of all downloaded audio used for Discord bot.
'''
class AudioRecords:
    
    '''
    Constructor for class. Creates class variables config (contains data from key.config) and audio_list (contains information on downloaded audio)
    Takes in data from config file which is used for directory of stored audio and audio records.
    '''
    def __init__(self, config):
        self.config = config

        #DataFrame created from csv, has columns [title, duration, id]
        self.audio_list = pd.read_csv(self.config["directory"] + self.config["audio_records"])

    '''
    Downloads audio and video/audio information from Youtube using youtube-dl package.
    Download options received from config.
    '''
    def download(self, url, d= True):
        with youtube_dl.YoutubeDL(self.config["options"]) as ydl:
            video_info = ydl.extract_info(url, download= d)

        return {col : video_info[col] for col in self.audio_list.columns}

    '''
    Returns path of audio and title of video/audio.
    '''
    def get_file(self, id):
        return self.config["directory"] + id + '.mp3', self.audio_list[self.audio_list['id'] == id].iloc[0]['title']

    '''
    Downloads video/audio (if needed) and it's info.
    Will add info if not already in the records and update csv.
    '''
    def add(self, url, d= True):
        added_record = self.download(url, d)

        if not ((self.audio_list['title'] == added_record['title']) & (self.audio_list['duration'] == added_record['duration']) & (self.audio_list['id'] == added_record['id'])).any():
            print(f'Adding {added_record["title"]}, {added_record["id"]} to records')
            self.audio_list = self.audio_list.append(added_record, ignore_index= True)
            self.audio_list.to_csv(self.config["directory"] + self.config["audio_records"], index= False)
        
        return self.get_file(added_record['id'])

    '''
    Update records if for some reason audio not recorded in csv after being downloaded.
    '''
    def update(self):
        download_list = open(self.config["directory"] + self.config["download_archive"], 'r')

        for x in download_list:
            url = 'https://www.youtube.com/watch?v='
            id =  x.split(' ')[1].replace('\n', '')
            url += id
            
            if not (self.audio_list['id'] == id).any(): 
                try:
                    self.add(url, False)
                except:
                    continue
        
        download_list.close()
        self.audio_list.to_csv(self.config["directory"] + self.config["audio_records"], index= False)
    
    def get_records(self):
        return self.audio_list

    def get_audio_record(self, i):
        audio_record = self.audio_list.iloc[i]
        return f'{i} {audio_record["title"]} {int(audio_record["duration"]/60)}:{audio_record["duration"]%60:02d}\n'

    def get_latest_record(self):
        return self.get_audio_record(self.audio_list.index[-1])

    def record_length(self):
        return len(self.audio_list)

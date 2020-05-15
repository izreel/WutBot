import pandas as pd
import youtube_dl

class AudioRecords:
    def __init__(self, config):
        self.config = config
        self.audio_list = pd.read_csv(self.config["directory"] + self.config["audio_records"])

    def download(self, url, d= True):
        with youtube_dl.YoutubeDL(self.config["options"]) as ydl:
            video_info = ydl.extract_info(url, download= d)

        return {col : video_info[col] for col in self.audio_list.columns}

    def get_file(self, id):
        return self.config["directory"] + id + '.mp3'

    def add(self, url, d= True):
        added_record = self.download(url, d)
        self.audio_list = self.audio_list.append(added_record, ignore_index= True)
        return self.get_file(added_record['id'])

    def update(self):
        download_list = open(self.config["directory"] + self.config["download_archive"], 'r')

        for x in download_list:
            url = 'https://www.youtube.com/watch?v='
            id =  x.split(' ')[1].replace('\n', '')
            url += id
            
            if len(self.audio_list[self.audio_list['id'] == id]) == 0: 
                try:
                    self.add(url, False)
                except:
                    continue
        
        download_list.close()
        self.audio_list.to_csv(self.config["directory"] + self.config["audio_records"], index= False)
    
    def get_records(self):
        return self.audio_list
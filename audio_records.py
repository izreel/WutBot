import pandas as pd
import download_audio
import youtube_dl

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

class AudioRecords:
    def __init__(self):
        self.audio_list = pd.read_csv('/mnt/d/downloaded_audio/audio_list.csv')

    def add(self, title, id):
        self.audio_list = self.audio_list.append({'title': title, 'id': id}, ignore_index= True)

    def update(self):
        download_list = open('/mnt/d/downloaded_audio/already_downloaded.txt', 'r')

        for x in download_list:
            url = 'https://www.youtube.com/watch?v='
            id =  x.split(' ')[1].replace('\n', '')
            url += id
            if len(self.audio_list[self.audio_list['id'] == id]) == 0: 
                try:
                    with youtube_dl.YoutubeDL(download_options) as ydl:
                        title = ydl.extract_info(url, download=False)['title']

                        self.add(title, id)
                except:
                    continue
        
        download_list.close()
        self.audio_list.to_csv('/mnt/d/downloaded_audio/audio_list.csv', index= False)
    
    def get_records(self):
        return self.audio_list
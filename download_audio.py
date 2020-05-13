import youtube_dl
import audio_records

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

def download(url, r):
    video_id = url.split('=')[1]
    
    with youtube_dl.YoutubeDL(download_options) as ydl:
        ydl.download([url])
        video_title = ydl.extract_info(url, download=False)['title']
    r.add(video_title, video_id)
    
    return get_file(video_id)

def get_file(id):
    return '/mnt/d/downloaded_audio/{}.mp3'.format(id)
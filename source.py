import asyncio
from yt_dlp import YoutubeDL


def _source( *, url: str) -> str:
    options = {
        'format': 'bestaudio/best',  
        'quiet': True,               
        'simulate': True,            
    }
    with YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=False)  
        return (audio_url := info['url'])



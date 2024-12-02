import yt_dlp
import asyncio
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError
from urllib.parse import urlparse, parse_qs


options = {
        'format': 'bestaudio/best',  
        'quiet': True,               
        'simulate': True,            
    }

def _source( url: str) -> str:
    options = {
        'format': 'bestaudio/best',  
        'quiet': True,               
        'simulate': True,            
    }
    with YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=False)  
        return info

async def asearch(url: str) -> str:
    return await asyncio.to_thread(_source, url)

async def _get(url) -> bool | DownloadError:
    """
    :param url: The URL of the YouTube video to check
    :return: True if the video exists, False if it doesn't, or a DownloadError if there's an error
    :rtype: bool | DownloadError
    """
    try:
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        video_id = query_params.get("v", [None])[0]
        res= await asearch(f"https://www.youtube.com/watch?v={video_id}")
        if 'id' in res:
            return res["url"]
        else:
            return False
    except yt_dlp.utils.DownloadError as e:
        return e
import yt_dlp
from yt_dlp.utils import DownloadError
from urllib.parse import urlparse, parse_qs


options = {
        'format': 'bestaudio/best',  
        'quiet': True,               
        'simulate': True,            
    }


def check_youtube_video(url) -> bool | DownloadError:
    """
    :param url: The URL of the YouTube video to check
    :return: True if the video exists, False if it doesn't, or a DownloadError if there's an error
    :rtype: bool | DownloadError
    """
    try:
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        video_id = query_params.get("v", [None])[0]
        with yt_dlp.YoutubeDL(options) as ydl:
            info_dict = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            if 'id' in info_dict:
                return True
            else:
                return False
    
    except yt_dlp.utils.DownloadError as e:
        return e



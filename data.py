from pytubefix import YouTube
import asyncio
from source import _source


def adata(url:str) -> dict:
    """
    get video data from youtube url.

    :param url: youtube video url
    :type url: str
    :return: video data
    :rtype: dict
    """
    imfor=YouTube(url)
    data:dict={}
    data['source']=_source(url=url)
    data['url']=url
    data['title']=imfor.title

    if int(imfor.views)>=1_000_000_000:
        data['views']=f"{imfor.views/1_000_000_000:.1f}B"

    elif int(imfor.views)>=1_000_000:
        data['views']=f"{imfor.views/1_000_000:.1f}M"

    elif int(imfor.views)>=1000:
        data['views']=f"{imfor.views/1000:.1f}K"

    else:
        data['views']=imfor.views

    data['author']=imfor.author
    data['thumbnail']=imfor.thumbnail_url
    min, sec=divmod(imfor.length, 60)
    if min>59:
        hour, min=divmod(min, 60)
        data['length']=f"{hour}:{min}:{sec}"
    else:
        data['length']=f"{min}:{sec}"

    return data
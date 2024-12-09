import discord
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class Now:
    '''
    :param voice_client: Dict
    :param queue: Deque
    :param source_url: str
    :param current: List
    :param data_page: Dict
    :param Embed: discord.Embed 
    :param asource: discord.PCMVolumeTransformer
    :param current_queue_index: int
    :param cool: List[bool]
    '''
    source_url: str=""
    current: List= field(default_factory=lambda: []) 
    data_page: Dict= field(default_factory=lambda: {}) 
    Embed: discord.Embed=""
    asource: discord.PCMVolumeTransformer=""
    current_queue_index: int = 0
    cool: List[bool] = field(default_factory=lambda: [False] * 4)  

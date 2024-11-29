import discord
import discord.ui as ui


class MusicView(ui.View):
    def __init__(
            self, 
            pause:bool,
            _source:str,
        ):
        super().__init__(
            ui.Button(
                label='',
                style=discord.ButtonStyle.grey,
                custom_id="pause" if pause else "resume",
                emoji="<:play:1311297384554430526>" if pause else "<:pause:1311954413811798066>"
                ),
            ui.Button(
                label='',
                style=discord.ButtonStyle.grey,
                custom_id="next",
                emoji="<:next:1311297797907021834>"
                ),
            ui.Button(
                label='',
                style=discord.ButtonStyle.grey,
                custom_id="repeat",
                emoji='<:repeat:1311295712176377896>'
                ),
            ui.Button(
                label='',
                style=discord.ButtonStyle.link,
                url=_source,
                ),
        )
        
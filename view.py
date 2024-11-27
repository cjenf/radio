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
                label="▶" if pause else "❚❚",
                style=discord.ButtonStyle.grey,
                custom_id="pause" if pause else "resume",
                ),
            ui.Button(
                label="▶❚",
                style=discord.ButtonStyle.grey,
                custom_id="next",
                ),
            ui.Button(
                label="歌曲來源",
                style=discord.ButtonStyle.link,
                url=_source,
                ),
            )
        
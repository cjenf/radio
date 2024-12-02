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
                label='  ',
                style= discord.ButtonStyle.red if pause else discord.ButtonStyle.grey,
                custom_id="pause" if pause else "resume",
                emoji="<:25b6:1313024253376987197>" if pause else "<:pause:1313021074702864414>"
                
                ),
            ui.Button(
                style=discord.ButtonStyle.grey,
                label='  ',
                custom_id="next",
                emoji="<:skip:1266005302713651291>"
                ),
            ui.Button(
                style=discord.ButtonStyle.grey,
                label='⟲',
                custom_id="repeat",
                ),
            ui.Button(
                style=discord.ButtonStyle.link,
                label='link',
                url=_source,
                ),
        )
        
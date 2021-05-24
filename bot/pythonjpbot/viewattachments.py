import os
import itertools
import re
import fnmatch
import discord
import pygments.lexers

_lexers = [lexer[2] for lexer in pygments.lexers.get_all_lexers()] + [("*.txt", "*.log")]

re_ext = re.compile(
    "|".join(fnmatch.translate(ext) for ext in itertools.chain.from_iterable(_lexers))
)


async def on_attachment(client, message):
    channel = message.channel
    guild = channel.guild

    for attachment in message.attachments:
        if re_ext.match(attachment.filename):
            embed = discord.Embed(
                title=f"View {attachment.filename}",
                url=f"https://www.python.jp/dcfileview/{guild.id}/{channel.id}/{message.id}/{attachment.id}/{attachment.filename}",
            )
            await message.channel.send(embed=embed)

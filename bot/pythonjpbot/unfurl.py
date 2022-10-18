from typing import Any
import re
import discord

DISCORD_URLS = re.compile(
    "https://discord(app)?.com/channels/"
    r"(?P<server>[\d]{18})/(?P<channel>[\d]+)/(?P<msg>[\d]+)"
)


def compose_embed(channel: Any, msg: discord.Message) -> discord.Embed:
    embed = discord.Embed(description=msg.content, timestamp=msg.created_at)
    embed.set_author(name=msg.author.display_name, icon_url=msg.author.display_avatar.url)
    embed.set_footer(text=f"via {msg.channel.name}")
    return embed


async def on_message(client: discord.Client, msg: discord.Message):
    for m in DISCORD_URLS.finditer(msg.content):
        if msg.guild.id == int(m.group("server")):
            channel = client.get_channel(int(m.group("channel")))
            if not channel:
                continue
            orgmsg = await channel.fetch_message(int(m.group("msg")))
            if not orgmsg:
                continue

            embed = compose_embed(channel, orgmsg)
            await msg.channel.send(embed=embed)

import os
import traceback
import discord
from . import unfurl
from . import reactions
from . import viewattachments
from . import commands

client = discord.Client(intents=discord.Intents.all())


async def send_exp(channel):
    s = traceback.format_exc()
    print(s)
    await channel.send(s)


@client.event
async def on_message(message: discord.Message):
    try:
        if message.author.bot:
            return

        if message.author == client.user:
            return

        await viewattachments.on_attachment(client, message)

        if not message.content:
            return

        if await reactions.on_message(client, message):
            return

        if await commands.on_message(client, message):
            return

        await unfurl.on_message(client, message)
    except Exception:
        await send_exp(message.channel)


@client.event
async def on_raw_reaction_add(payload):
    await reactions.on_reaction(client, payload)


key = open(os.environ['DISCORD_BOT_KEYFILE']).read().strip()
client.run(key)

# https://discordapp.com/channels/411079445927952385/411761902327431169/471620068330176532

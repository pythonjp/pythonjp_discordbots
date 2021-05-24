import os
import discord

client = discord.Client()
key = open(os.environ['DISCORD_BOT_KEYFILE']).read().strip()
await discord_client.login(token=key, bot=True)

#http://localhost:411079445927952385/411079445927952389/820472571291369513/820472571535294484/a.c


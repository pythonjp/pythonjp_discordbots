import os
import discord
from github import Github, UnknownObjectException, GithubException
from collections import defaultdict, Counter
import datetime

TOKEN = open(os.environ['GITHUB_ACCESS_TOKEN']).read().strip()

g = Github(TOKEN)


cmd = "/wiki"

USAGE = """Usage:
/wiki register GitHubUserName
"""

count_invitation = defaultdict(set)
total_invitaion = Counter()

async def on_message(client:discord.Client, msg: discord.Message):

    tokens = msg.content.strip().split()
    if not tokens or (tokens[0] != "/wiki"):
        return

    if (len(tokens) != 3) or (tokens[1] != "register"):
        await msg.channel.send(USAGE)
        return True

    today = datetime.date.today()
    if len(count_invitation[(today, msg.author.id)]) >= 4:
        if tokens[2] not in count_invitation[(today, msg.author.id)]:
            await msg.channel.send(f"Quota limit exceeded")
            return True


    if total_invitaion[(today, msg.author.id)] > 10:
        await msg.channel.send(f"Quota limit exceeded")

    if '@' in tokens[2]:
        await msg.channel.send(f"Invalid GitHub account")
        return True

    wiki = g.get_repo("pythonjp/community")

    for inv in  wiki.get_pending_invitations():
        if inv.invitee.login == tokens[2]:
            await msg.channel.send(f"`{tokens[2]}' is already invited. Check your mailbox.")
            return True

    try:
        wiki.add_to_collaborators(tokens[2], "push")
    except UnknownObjectException:
        await msg.channel.send(f"Unknown GitHub user name: {tokens[2]}")
        return True

    await msg.channel.send(f"GitHubユーザ {tokens[2]} のメールアドレスに確認メールを送信しました。")

    channel = msg.channel.guild.get_channel(464333368537120779)
    if channel:
        await channel.send(f"Sent wiki invitation to `{tokens[2]}` as per request by {msg.author.mention})")
    count_invitation[(today, msg.author.id)].add(tokens[2])
    total_invitaion[(today, msg.author.id)] += 1

    return True



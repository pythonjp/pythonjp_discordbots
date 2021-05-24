import os
import asyncio
from pygments import highlight
from pygments.lexers import get_lexer_for_filename, ClassNotFound, TextLexer
from pygments.formatters import HtmlFormatter

import urllib.parse
from typing import Optional
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import jinja2
import discord

app = FastAPI()

html = jinja2.Template(
    """
<html>
<link rel="stylesheet" href="https://unpkg.com/normalize.css@8.0.1/normalize.css">

<style>
 {{ style | safe }}

  @media(min-width: 576px) {
    .body {
      max-width: 540px;
    }
  }
  @media(min-width: 768px) {
    .body {
      max-width: 720px;
    }
  }
  @media(min-width: 992px) {
    .body {
      max-width: 960px;
    }
  }
  @media(min-width: 1200px) {
    .body {
      max-width: 1140px;
    }
  }
  .body {
    margin-top: 1em;
    margin-bottom: 1em;
    margin-right: auto;  
    margin-left: auto;  
  }
  .linenos {
    border-right: solid 1px #988383;
  }

  .linenodiv {
    color: #848896;
    padding-right: 5px:
  }
  .highlight {
    padding-left: 5px;
  }
  pre {
    line-height: 1.5em;
    font-family: SFMono-Regular,Menlo,Monaco,Consolas,
                  "Liberation Mono","Courier New",monospace;
  }
</style>
<body>
<div class="body">
{{ src | safe }}
</div>
</html>
"""
)


def render_src(filename: str, src: str) -> str:
    try:
        lexer = get_lexer_for_filename(filename)
    except ClassNotFound:
        lexer = TextLexer

    formatter = HtmlFormatter(linenos=True)
    style = formatter.get_style_defs()
    s = highlight(src, lexer, formatter)
    return html.render(style=style, src=s)


async def get_file(url):
    async with httpx.AsyncClient() as client:
        async with client.stream("GET", url) as resp:
            resp.raise_for_status()

            size = int(resp.headers.get("content-length", 1))
            assert size < 1024 * 1024

            src = "".join([t async for t in resp.aiter_text()])

    return src

#/411079445927952385/411079445927952389/820472571291369513/820472571535294484/a.c
@app.get("/{guild}/{channel}/{message}/{attachmentid}/{filename}")
async def view_file(guild: int, channel:int, message: int, attachmentid:int, filename: str):
    assert guild
    assert channel
    assert message
    assert attachmentid
    assert filename

    channel = await discord_client.fetch_channel(channel)
    assert guild == channel.guild.id
    try:
        msg = await channel.fetch_message(message)
    except discord.NotFound:
        raise HTTPException(status_code=404, detail="Item not found")

    for attachment in msg.attachments:
        if attachment.id == attachmentid:
            break
    else:
        raise HTTPException(status_code=404, detail="Item not found")

    src = await get_file(attachment.url)
    html = render_src(filename, src)
    return HTMLResponse(f"<html>{html}</html>")


@app.on_event("startup")
async def onstartup():
    global discord_client 

    loop = asyncio.get_event_loop()
    discord_client = discord.Client(loop=loop)
    key = open(os.environ['DISCORD_BOT_KEYFILE']).read().strip()
    await discord_client.login(token=key, bot=True)


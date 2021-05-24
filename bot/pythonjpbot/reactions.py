import re
import zlib
import collections
import json
from google.cloud import datastore

# export GOOGLE_APPLICATION_CREDENTIALS="[PATH]"
datastore_client = datastore.Client()


async def add_reaction(client, payload):
    #    'emoji': {'name': 'guido', 'id': '467217552016408579', 'animated': False},

    channel = client.get_channel(payload.channel_id)
    if not channel:
        return

    msg = await channel.fetch_message(payload.message_id)
    if not msg:
        return

    name = payload.emoji.name
    id = payload.emoji.id

    if id:
        s = [name, str(id)]
    else:
        s = [name, None]

    k = datastore_client.key("USERREACTION", str(msg.author.id))
    ret = datastore_client.get(k)

    if ret:
        d = json.loads(zlib.decompress(ret["rc"]))
    else:
        d = []

    updated = []

    n = 1
    for emoji, v in d:
        if emoji == s:
            n = v + 1
        else:
            updated.append((emoji, v))

    updated.insert(0, (s, n))

    e = datastore.Entity(key=k, exclude_from_indexes=["rc"])
    e["rc"] = zlib.compress(json.dumps(updated).encode("utf-8"))
    datastore_client.put(e)


def get_reactions(userid, emojis):
    k = datastore_client.key("USERREACTION", userid)
    ret = datastore_client.get(k)

    if not ret:
        return ""

    org = json.loads(zlib.decompress(ret["rc"]))

    emojis = {e.id: e for e in emojis}

    # emoji ids are str in some old record.
    converted = collections.defaultdict(int)
    for (name, id), v in org:
        if id:
            id = int(id)
            if id not in emojis:  # ignore external/unknown emoji
                continue

        converted[(name, id)] += v

    all = sorted(converted.items(), key=(lambda v: (v[1], v[0])), reverse=True)
    s = []
    for (name, id), v in all:
        if id:
            name = f"<{'a' if emojis[id].animated else ''}:{name}:{id}>"
        s.append(f"{name}: {v}")

    if s:
        return ",".join(s)
    else:
        return ""


async def on_message(client, msg):
    c = msg.content.rstrip()
    m = re.match(r"^/reaction\s*(<@!?(\d{18})>)?$", c)
    if not m:
        return

    if not m[2]:
        userid = str(msg.author.id)
    else:
        userid = m[2]
    reactions = get_reactions(userid, msg.guild.emojis)
    await msg.channel.send(reactions)
    return True

async def on_reaction(client, payload):
    await add_reaction(client, payload)

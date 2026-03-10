"""Delete empty categories and default channels."""

import discord
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path.home() / ".ccmux" / "secrets" / "discord.env")

TOKEN = os.environ["DISCORD_BOT_TOKEN"]
GUILD_ID = int(os.environ["DISCORD_GUILD_ID"])

intents = discord.Intents.default()
client = discord.Client(intents=intents)

DELETE_CATEGORIES = {"📖 BOOK DISCUSSION | 读书讨论", "文字频道", "语音频道"}


@client.event
async def on_ready():
    guild = client.get_guild(GUILD_ID)

    for cat in guild.categories:
        if cat.name in DELETE_CATEGORIES:
            for ch in cat.channels:
                await ch.delete()
                print(f"  Deleted: #{ch.name}")
            await cat.delete()
            print(f"  Deleted category: {cat.name}")

    # Delete #常规 if exists
    for ch in guild.text_channels:
        if ch.name == "常规":
            await ch.delete()
            print(f"  Deleted: #常规")

    print("\nRemaining:")
    guild = client.get_guild(GUILD_ID)
    for ch in guild.text_channels:
        cat_name = ch.category.name if ch.category else "No category"
        print(f"  [{cat_name}] #{ch.name}")

    await client.close()


client.run(TOKEN)

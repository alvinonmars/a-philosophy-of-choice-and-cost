"""Remove extra channels, keep only dao-marks and general-chat."""

import discord
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path.home() / ".ccmux" / "secrets" / "discord.env")

TOKEN = os.environ["DISCORD_BOT_TOKEN"]
GUILD_ID = int(os.environ["DISCORD_GUILD_ID"])

intents = discord.Intents.default()
client = discord.Client(intents=intents)

# Channels to keep (by name)
KEEP_CHANNELS = {
    "公告-announcements",
    "规则-rules",
    "道痕日记-dao-marks",
    "自由讨论-general-chat",
}

# Categories to remove entirely
REMOVE_CATEGORIES = {
    "🛠️ COMMUNITY | 社区",
}

# Channels to remove from remaining categories
REMOVE_CHANNELS = {
    "自我介绍-introductions",
    "五境讨论-five-states",
    "白黑石头-stones",
    "建议反馈-feedback",
    "资源分享-resources",
}


@client.event
async def on_ready():
    guild = client.get_guild(GUILD_ID)
    if not guild:
        print("Guild not found")
        await client.close()
        return

    print(f"Cleaning up: {guild.name}")

    # Delete unwanted channels
    for ch in guild.text_channels:
        if ch.name in REMOVE_CHANNELS:
            await ch.delete()
            print(f"  Deleted channel: #{ch.name}")

    # Delete empty categories
    for cat in guild.categories:
        if cat.name in REMOVE_CATEGORIES:
            # Delete any remaining channels in the category
            for ch in cat.channels:
                await ch.delete()
                print(f"  Deleted channel: #{ch.name}")
            await cat.delete()
            print(f"  Deleted category: {cat.name}")

    # Rename WELCOME category to simpler name
    welcome_cat = discord.utils.get(guild.categories, name="📋 WELCOME | 欢迎区")
    if welcome_cat:
        # Move dao-marks and general-chat here
        dao_ch = discord.utils.get(guild.text_channels, name="道痕日记-dao-marks")
        general_ch = discord.utils.get(guild.text_channels, name="自由讨论-general-chat")

        # Delete the book discussion category if empty
        book_cat = discord.utils.get(guild.categories, name="📖 BOOK DISCUSSION | 读书讨论")
        if book_cat:
            if dao_ch:
                await dao_ch.edit(category=welcome_cat)
                print(f"  Moved #道痕日记-dao-marks to welcome category")
            if general_ch:
                await general_ch.edit(category=welcome_cat)
                print(f"  Moved #自由讨论-general-chat to welcome category")
            # Delete empty category
            if not book_cat.channels:
                await book_cat.delete()
                print(f"  Deleted empty category: {book_cat.name}")

    print("\n✅ Cleanup complete!")
    print("Remaining channels:")
    guild = client.get_guild(GUILD_ID)
    for ch in guild.text_channels:
        print(f"  #{ch.name}")

    await client.close()


client.run(TOKEN)

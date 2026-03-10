"""Disable channel creation for regular members."""

import discord
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path.home() / ".ccmux" / "secrets" / "discord.env")

TOKEN = os.environ["DISCORD_BOT_TOKEN"]
GUILD_ID = int(os.environ["DISCORD_GUILD_ID"])

intents = discord.Intents.default()
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    guild = client.get_guild(GUILD_ID)
    if not guild:
        print("Guild not found")
        await client.close()
        return

    print(f"Fixing permissions: {guild.name}")

    # Disable create channels/threads for @everyone on all categories
    for cat in guild.categories:
        await cat.set_permissions(
            guild.default_role,
            create_instant_invite=True,
            send_messages=None,  # inherit
            manage_channels=False,
            create_public_threads=False,
            create_private_threads=False,
        )
        print(f"  Locked category: {cat.name}")

    print("\n✅ Permissions fixed - members cannot create channels or threads.")
    await client.close()


client.run(TOKEN)

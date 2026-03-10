"""One-time setup script to configure Discord server channels, roles, and welcome message."""

import discord
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Load secrets from ~/.ccmux/secrets/discord.env
load_dotenv(Path.home() / ".ccmux" / "secrets" / "discord.env")

TOKEN = os.environ["DISCORD_BOT_TOKEN"]
GUILD_ID = int(os.environ["DISCORD_GUILD_ID"])

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

client = discord.Client(intents=intents)


async def setup_roles(guild):
    """Create roles for the server."""
    roles_config = [
        {"name": "中文读者", "color": discord.Color.red()},
        {"name": "English Reader", "color": discord.Color.blue()},
        {"name": "道痕践行者 | Practitioner", "color": discord.Color.gold()},
    ]
    created = []
    for rc in roles_config:
        existing = discord.utils.get(guild.roles, name=rc["name"])
        if existing:
            print(f"  Role '{rc['name']}' already exists, skipping.")
            created.append(existing)
        else:
            role = await guild.create_role(name=rc["name"], color=rc["color"])
            print(f"  Created role: {rc['name']}")
            created.append(role)
    return created


async def setup_channels(guild):
    """Create categories and channels."""
    structure = {
        "\U0001f4cb WELCOME | \u6b22\u8fce\u533a": [
            {"name": "\u516c\u544a-announcements", "read_only": True},
            {"name": "\u81ea\u6211\u4ecb\u7ecd-introductions", "read_only": False},
            {"name": "\u89c4\u5219-rules", "read_only": True},
        ],
        "\U0001f4d6 BOOK DISCUSSION | \u8bfb\u4e66\u8ba8\u8bba": [
            {"name": "\u4e94\u5883\u8ba8\u8bba-five-states", "read_only": False},
            {"name": "\u767d\u9ed1\u77f3\u5934-stones", "read_only": False},
            {"name": "\u9053\u75d5\u65e5\u8bb0-dao-marks", "read_only": False},
            {"name": "\u81ea\u7531\u8ba8\u8bba-general-chat", "read_only": False},
        ],
        "\U0001f6e0\ufe0f COMMUNITY | \u793e\u533a": [
            {"name": "\u5efa\u8bae\u53cd\u9988-feedback", "read_only": False},
            {"name": "\u8d44\u6e90\u5206\u4eab-resources", "read_only": False},
        ],
    }

    for cat_name, channels in structure.items():
        # Check if category exists
        existing_cat = discord.utils.get(guild.categories, name=cat_name)
        if existing_cat:
            category = existing_cat
            print(f"  Category '{cat_name}' already exists.")
        else:
            category = await guild.create_category(cat_name)
            print(f"  Created category: {cat_name}")

        for ch in channels:
            existing_ch = discord.utils.get(
                guild.text_channels, name=ch["name"], category=category
            )
            if existing_ch:
                print(f"    Channel '#{ch['name']}' already exists, skipping.")
                continue

            if ch["read_only"]:
                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(send_messages=False),
                    guild.me: discord.PermissionOverwrite(send_messages=True),
                }
                channel = await guild.create_text_channel(
                    ch["name"], category=category, overwrites=overwrites
                )
            else:
                channel = await guild.create_text_channel(
                    ch["name"], category=category
                )
            print(f"    Created channel: #{ch['name']}")


async def post_welcome_messages(guild):
    """Post welcome and rules messages."""

    # Post in rules channel
    rules_ch = discord.utils.get(guild.text_channels, name="\u89c4\u5219-rules")
    if rules_ch:
        # Check if already posted
        async for msg in rules_ch.history(limit=5):
            if msg.author == guild.me:
                print("  Rules already posted, skipping.")
                return

        rules_text = """🌊 **欢迎来到「人选天选论」读者社区**
**Welcome to the A Philosophy of Choice and Cost community**

📖 **在线阅读 / Read Online:**
https://alvinonmars.github.io/a-philosophy-of-choice-and-cost/

🔑 **核心理念 / Core Principle:**
> "这个世界没有运气，只有选择。"
> "This world contains no luck, only choices."

📌 **社区规则 / Rules:**
1️⃣ 中英文皆可，鼓励双语交流 / Both Chinese and English are welcome
2️⃣ 尊重不同观点，理性讨论 / Respect different perspectives
3️⃣ 欢迎在 #道痕日记-dao-marks 分享你的日常自省 / Share your daily reflections
4️⃣ 禁止广告、spam 和无关内容 / No ads, spam, or off-topic content

🌐 **选择你的语言角色 / Choose your language role:**
React below: 🇨🇳 = 中文读者 | 🇬🇧 = English Reader

从 #自我介绍-introductions 开始吧！告诉我们你是怎么发现这本书的。
Start at #自我介绍-introductions — tell us how you found this book!"""

        msg = await rules_ch.send(rules_text)
        await msg.add_reaction("🇨🇳")
        await msg.add_reaction("🇬🇧")
        print("  Posted rules and welcome message.")

    # Post in announcements
    ann_ch = discord.utils.get(guild.text_channels, name="\u516c\u544a-announcements")
    if ann_ch:
        async for msg in ann_ch.history(limit=5):
            if msg.author == guild.me:
                print("  Announcement already posted, skipping.")
                return

        ann_text = """📢 **社区正式上线！/ Community is now live!**

欢迎来到《人选天选论》读者社区。这里是一个探讨选择与代价、贪婪与恐惧的空间。

Welcome to the reader community for "A Philosophy of Choice and Cost" by Jiang Lan (姜蓝).

📖 https://alvinonmars.github.io/a-philosophy-of-choice-and-cost/"""

        await ann_ch.send(ann_text)
        print("  Posted announcement.")


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    guild = client.get_guild(GUILD_ID)
    if not guild:
        print(f"ERROR: Could not find guild {GUILD_ID}")
        await client.close()
        return

    print(f"Setting up server: {guild.name}")

    print("\n[1/3] Creating roles...")
    await setup_roles(guild)

    print("\n[2/3] Creating channels...")
    await setup_channels(guild)

    print("\n[3/3] Posting welcome messages...")
    await post_welcome_messages(guild)

    print("\n✅ Server setup complete!")
    await client.close()


client.run(TOKEN)

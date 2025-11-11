import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from keep_alive import keep_alive

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

NICK_CHANNELS_FILE = "nick_channels.json"
LOG_CHANNELS_FILE = "log_channels.json"

# ------------------- Load Saved Channels -------------------

def load_json(filename):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return {}

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

nick_channels = load_json(NICK_CHANNELS_FILE)
log_channels = load_json(LOG_CHANNELS_FILE)

# ------------------- Slash Commands -------------------

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Logged in as {bot.user}")

@bot.tree.command(name="setnickchannel", description="Set the channel where users can change their nicknames")
async def set_nick_channel(interaction: discord.Interaction):
    nick_channels[str(interaction.guild.id)] = interaction.channel.id
    save_json(NICK_CHANNELS_FILE, nick_channels)
    await interaction.response.send_message(
        f"✅ Nickname change channel set to {interaction.channel.mention}", ephemeral=True
    )

@bot.tree.command(name="setlogchannel", description="Set the channel for nickname change logs")
async def set_log_channel(interaction: discord.Interaction):
    log_channels[str(interaction.guild.id)] = interaction.channel.id
    save_json(LOG_CHANNELS_FILE, log_channels)
    await interaction.response.send_message(
        f"✅ Log channel set to {interaction.channel.mention}", ephemeral=True
    )

# ------------------- Nickname Handler -------------------

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    guild_id = str(message.guild.id)
    if guild_id not in nick_channels:
        return

    if message.channel.id == nick_channels[guild_id]:
        new_nick = message.content.strip()

        try:
            await message.author.edit(nick=new_nick)
            await message.channel.send(f"{message.author.mention}'s nickname was changed to **{new_nick}**")

            # Log if log channel is set
            if guild_id in log_channels:
                log_channel = bot.get_channel(log_channels[guild_id])
                if log_channel:
                    await log_channel.send(f"📝 **{message.author}** changed nickname to **{new_nick}**")

        except discord.Forbidden:
            await message.channel.send("❌ I don’t have permission to change your nickname.")
        except Exception as e:
            await message.channel.send(f"⚠️ Error: {e}")

# ------------------- Keep Alive for Render -------------------

keep_alive()

# ------------------- Run Bot -------------------

bot.run(os.getenv("DISCORD_TOKEN"))


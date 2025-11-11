import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from keep_alive import keep_alive

# Intents
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.messages = True
intents.message_content = True

# Bot setup
bot = commands.Bot(command_prefix="!", intents=intents)

# Load saved log and nickname channels
try:
    with open("nick_channels.json", "r") as f:
        nick_channels = json.load(f)
except FileNotFoundError:
    nick_channels = {}

log_channels = {}

@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

# Slash command to set nickname channel
@bot.tree.command(name="setnickchannel", description="Set the channel for nickname changes.")
@app_commands.checks.has_permissions(administrator=True)
async def setnickchannel(interaction: discord.Interaction, channel: discord.TextChannel):
    nick_channels[str(interaction.guild_id)] = channel.id
    with open("nick_channels.json", "w") as f:
        json.dump(nick_channels, f, indent=4)
    await interaction.response.send_message(f"Nickname channel set to {channel.mention}", ephemeral=True)

# Slash command to set log channel
@bot.tree.command(name="setlogchannel", description="Set the channel where nickname change logs will be sent.")
@app_commands.checks.has_permissions(administrator=True)
async def setlogchannel(interaction: discord.Interaction, channel: discord.TextChannel):
    log_channels[str(interaction.guild_id)] = channel.id
    await interaction.response.send_message(f"Log channel set to {channel.mention}", ephemeral=True)

# Detect messages in nickname channel
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    guild_id = str(message.guild.id)
    if guild_id in nick_channels and message.channel.id == nick_channels[guild_id]:
        try:
            await message.author.edit(nick=message.content[:32])
            await message.channel.send(f"Nickname updated to: {message.content}", delete_after=5)

            if guild_id in log_channels:
                log_channel = bot.get_channel(log_channels[guild_id])
                if log_channel:
                    await log_channel.send(f"{message.author} changed nickname to: {message.content}")

        except discord.Forbidden:
            await message.channel.send("I don't have permission to change that nickname.", delete_after=5)

keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))

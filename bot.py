import discord
from discord.ext import commands
import json
import os
from keep_alive import keep_alive  # Keeps bot alive on Render

# Start the keep_alive web server
keep_alive()

# Set up the bot with intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True  # Required for reading messages in new Discord API versions

bot = commands.Bot(command_prefix="!", intents=intents)

# Load nickname channel data from file
try:
    with open("nick_channels.json", "r") as f:
        nick_channels = json.load(f)
except FileNotFoundError:
    nick_channels = {}

# Event: Bot is ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print("Bot is ready and running!")

# Command: Set the nickname channel
@bot.command()
@commands.has_permissions(manage_guild=True)
async def setnickchannel(ctx, channel: discord.TextChannel):
    """Set the channel where nickname changes are allowed."""
    nick_channels[str(ctx.guild.id)] = channel.id
    with open("nick_channels.json", "w") as f:
        json.dump(nick_channels, f, indent=4)
    await ctx.send(f"Nickname change channel set to {channel.mention}")

# Command:


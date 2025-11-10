import discord
from discord.ext import commands
import json
import os
from keep_alive import keep_alive  # keeps the bot alive on Render

# Start the keep_alive server
keep_alive()

# Set up the bot with intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True  # if your bot needs to read messages

bot = commands.Bot(command_prefix="!", intents=intents)

# Load nickname channel data
try:
    with open("nick_channels.json", "r") as f:
        nick_channels = json.load(f)
except FileNotFoundError:
    nick_channels = {}

# Event when bot is ready
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    print("Bot is ready and running!")

# Command to set the nickname channel
@bot.command()
@commands.has_permissions(manage_guild=True)
async def setnickchannel(ctx, channel: discord.TextChannel):
    """Set the channel where nickname changes are allowed."""
    nick_channels[str(ctx.guild.id)] = channel.id
    with open("nick_channels.json", "w") as f:
        json.dump(nick_channels, f, indent=4)
    await ctx.send(f"✅ Nickname change channel set to {channel.mention}")

# Command for users to change their nickname
@bot.command()
async def nick(ctx, *, new_nick: str):
    """Change your nickname (only works in the assigned channel)."""
    guild_id = str(ctx.guild.id)
    if guild_id not in nick_channels or ctx.channel.id != nick_channels[guild_id]:
        await ctx.send(⚠️ You can only change your nickname in the designated channel!")
        return

    try:
        await ctx.author.edit(nick=new_nick)
        await ctx.send(f"✅ Your nickname has been changed to **{new_nick}**")
    except discord.Forbidden:
        await ctx.send("❌ I don’t have permission to change your nickname!")

# Run the bot using the token from Render's environment variable
bot.run(os.getenv("DISCORD_TOKEN"))

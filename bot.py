import os
import discord
from discord.ext import commands
from keep_alive import keep_alive  # Keeps the bot alive on Render

# Enable intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Create the bot client
bot = commands.Bot(command_prefix="!", intents=intents)

# Event when bot is ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("Bot is online and running successfully.")

# Test command to confirm the bot is active
@bot.command()
async def ping(ctx):
    await ctx.send("Pong! The bot is active and responding.")

# Command to set nickname channel (example placeholder)
@bot.command()
async def setnickchannel(ctx):
    await ctx.send("This command will let you set a nickname channel in the future.")

# Start the keep_alive web server (so Render stays awake)
keep_alive()

# Get the Discord bot token from Render environment variables
token = os.getenv("DISCORD_TOKEN")

# Run the bot
if token:
    bot.run(token)
else:
    print("ERROR: No Discord token found. Please check your Render environment settings.")


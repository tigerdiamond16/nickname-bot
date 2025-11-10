import discord
from discord.ext import commands
import json
import os
from keep_alive import keep_alive  # keeps bot alive on Render

# Load nickname channel data
try:
    with open("nick_channels.json", "r") as f:
        nick_channels = json.load(f)
except FileNotFoundError:
    nick_channels = {}

# Set up bot intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    print("✅ Slash commands synced successfully!")

@bot.tree.command(name="setnickchannel", description="Set the channel where nickname messages will be read.")
async def setnickchannel(interaction: discord.Interaction, channel: discord.TextChannel):
    guild_id = str(interaction.guild.id)
    nick_channels[guild_id] = channel.id

    with open("nick_channels.json", "w") as f:
        json.dump(nick_channels, f, indent=4)

    await interaction.response.send_message(f"✅ Nickname channel set to {channel.mention}", ephemeral=True)

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    guild_id = str(message.guild.id)
    if guild_id in nick_channels and message.channel.id == nick_channels[guild_id]:
        try:
            await message.author.edit(nick=message.content[:32])
            await message.delete()
        except discord.Forbidden:
            await message.channel.send("❌ I don’t have permission to change that nickname.")
        except Exception as e:
            print(f"Error: {e}")

    await bot.process_commands(message)

# Start the small web server to keep Render alive
keep_alive()

# Run the bot using Render’s environment variable
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    print("❌ No TOKEN found! Please set it in Render Environment settings.")
else:
    bot.run(TOKEN)


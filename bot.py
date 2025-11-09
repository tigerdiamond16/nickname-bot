import discord
from discord import app_commands
from discord.ext import commands
import json
import os
import os

TOKEN = os.getenv("TOKEN")
DATA_FILE = "nick_channels.json"

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Load or create nickname channel data
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        nick_channels = json.load(f)
else:
    nick_channels = {}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(nick_channels, f, indent=4)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Logged in as {bot.user}")
    print(f"Slash commands synced successfully!")

# --- Slash command to set nickname channel ---
@bot.tree.command(name="setnickchannel", description="Set the channel where nickname changes happen.")
@app_commands.checks.has_permissions(administrator=True)
async def setnickchannel(interaction: discord.Interaction, channel: discord.TextChannel):
    nick_channels[str(interaction.guild_id)] = channel.id
    save_data()
    await interaction.response.send_message(f"✅ Nickname channel set to {channel.mention}", ephemeral=True)


@setnickchannel.error
async def setnickchannel_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message("❌ You need to be an administrator to use this command.", ephemeral=True)

# --- Listen for messages in the nickname channel ---
@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    guild_id = str(message.guild.id)
    if guild_id in nick_channels and message.channel.id == nick_channels[guild_id]:
        new_nick = message.content.strip()
        if new_nick:
            try:
                await message.author.edit(nick=new_nick)
                await message.delete()
                print(f"Changed {message.author} nickname to '{new_nick}'")
            except discord.Forbidden:
                await message.channel.send("❌ I don't have permission to change nicknames.", delete_after=5)
            except Exception as e:
                print(f"Error changing nickname: {e}")
    else:
        await bot.process_commands(message)

bot.run(TOKEN)

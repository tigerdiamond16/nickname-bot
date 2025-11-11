import discord
from discord.ext import commands
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

# Load nickname and log channel data
try:
    with open("nick_channels.json", "r") as f:
        data = json.load(f)
        nick_channels = data.get("nick_channels", {})
        log_channels = data.get("log_channels", {})
except FileNotFoundError:
    nick_channels = {}
    log_channels = {}

# --- Events ---
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    print("Bot is ready to receive nickname messages.")


# --- Commands ---

@bot.command(name="setnickchannel")
@commands.has_permissions(administrator=True)
async def setnickchannel(ctx, channel: discord.TextChannel):
    """Sets the nickname input channel."""
    nick_channels[str(ctx.guild.id)] = channel.id
    save_channels()
    await ctx.send(f"✅ Nickname channel set to {channel.mention}")


@bot.command(name="setlogchannel")
@commands.has_permissions(administrator=True)
async def setlogchannel(ctx, channel: discord.TextChannel):
    """Sets the channel where nickname change logs will be sent."""
    log_channels[str(ctx.guild.id)] = channel.id
    save_channels()
    await ctx.send(f"✅ Log channel set to {channel.mention}")


def save_channels():
    """Saves the nickname and log channel data."""
    with open("nick_channels.json", "w") as f:
        json.dump({
            "nick_channels": nick_channels,
            "log_channels": log_channels
        }, f, indent=4)


# --- Nickname handling ---
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    guild_id = str(message.guild.id)

    # Check if the message is in the nickname channel
    if guild_id in nick_channels and message.channel.id == nick_channels[guild_id]:
        try:
            new_nick = message.content.strip()
            await message.author.edit(nick=new_nick)
            await message.channel.send(f"✅ Nickname changed to: {new_nick}", delete_after=5)

            # Log nickname change
            if guild_id in log_channels:
                log_channel = bot.get_channel(log_channels[guild_id])
                if log_channel:
                    await log_channel.send(f"🔔 {message.author} changed nickname to: `{new_nick}`")

        except discord.Forbidden:
            await message.channel.send("⚠️ I don't have permission to change that nickname.", delete_after=5)
        except Exception as e:
            await message.channel.send(f"⚠️ An error occurred: {e}", delete_after=5)

    await bot.process_commands(message)


# Keep-alive (Render ping)
keep_alive()

# Run the bot
bot.run(os.getenv("DISCORD_TOKEN"))

import os
import json
import discord
from discord.ext import commands
from datetime import datetime
from keep_alive import keep_alive

# ===== INTENTS =====
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Create bot with slash command support
bot = discord.Bot(intents=intents)

# ===== SETTINGS =====
ALLOWED_CHANNEL_NAME = "in-city-name-id"  # change this to your nickname input channel name
CONFIG_FILE = "config.json"  # stores the log channel ID

# ===== LOAD CONFIG =====
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
else:
    config = {"log_channel_id": None}


# ===== HELPER FUNCTION =====
async def send_log_embed(guild, user, old_nick, new_nick):
    """Send a formatted embed to the log channel."""
    log_channel_id = config.get("log_channel_id")
    if not log_channel_id:
        return  # No log channel set yet

    log_channel = guild.get_channel(log_channel_id)
    if not log_channel:
        return  # Channel not found or deleted

    embed = discord.Embed(
        title="Nickname Changed",
        color=discord.Color.blurple(),
        timestamp=datetime.now()
    )
    embed.add_field(name="User", value=f"{user.mention} ({user})", inline=False)
    embed.add_field(name="Old Nickname", value=old_nick or "None", inline=True)
    embed.add_field(name="New Nickname", value=new_nick or "None", inline=True)
    embed.set_footer(text=f"User ID: {user.id}")

    try:
        await log_channel.send(embed=embed)
    except Exception as e:
        print(f"Failed to send log embed: {e}")


# ===== SLASH COMMANDS =====
@bot.slash_command(name="setlogchannel", description="Set the channel where nickname logs will be sent.")
@discord.default_permissions(manage_guild=True)
async def setlogchannel(ctx, channel: discord.TextChannel):
    """Allows admins to set the nickname log channel."""
    config["log_channel_id"] = channel.id
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

    await ctx.respond(f"Log channel has been set to {channel.mention}")
    print(f"✅ Log channel set to {channel.name} in guild {ctx.guild.name}")


@bot.slash_command(name="showlogchannel", description="Show the current log channel for nickname updates.")
async def showlogchannel(ctx):
    """Displays which log channel is currently set."""
    log_channel_id = config.get("log_channel_id")
    if log_channel_id:
        channel = ctx.guild.get_channel(log_channel_id)
        if channel:
            await ctx.respond(f"Current log channel: {channel.mention}")
            return
    await ctx.respond("No log channel has been set yet. Use `/setlogchannel` to set one.")


# ===== EVENTS =====
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    print("Bot is running and ready to change nicknames and send logs!")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.channel.name == ALLOWED_CHANNEL_NAME:
        nickname = message.content.strip()
        if not nickname:
            return

        try:
            old_nick = message.author.display_name
            await message.author.edit(nick=nickname)
            await message.delete()

            confirmation = await message.channel.send(
                f"Nickname for {old_nick} changed to '{nickname}'."
            )
            await confirmation.delete(delay=3)

            await send_log_embed(message.guild, message.author, old_nick, nickname)
            print(f"Changed nickname for {message.author} to '{nickname}' and logged it.")

        except discord.Forbidden:
            await message.channel.send(
                f"I don't have permission to change nicknames for {message.author.mention}.",
                delete_after=5
            )
        except Exception as e:
            await message.channel.send(
                f"Error changing nickname for {message.author.mention}: {e}",
                delete_after=5
            )


# ===== KEEP ALIVE =====
keep_alive()

# ===== RUN BOT =====
token = os.getenv("DISCORD_TOKEN")
if token:
    bot.run(token)
else:
    print("ERROR: Discord token not found in environment variables.")


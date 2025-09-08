import os
import discord
from discord import app_commands
from discord.ext import commands

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("❌ DISCORD_BOT_TOKEN environment variable not set!")

# Test guilds (replace with yours)
TEST_GUILDS = [1373066824278605874, 1399784437440319508]

intents = discord.Intents.default()
intents.guilds = True
intents.members = True  # needed for role-based checks later
bot = commands.Bot(command_prefix="!", intents=intents)


# ---------------------------
# Slash Commands
# ---------------------------
@bot.tree.command(name="settings", description="Enable or disable DM notifications")
@app_commands.describe(dm_enabled="Set to true or false")
async def settings(interaction: discord.Interaction, dm_enabled: bool):
    await interaction.response.send_message(
        f"✅ DM notifications {'enabled' if dm_enabled else 'disabled'}",
        ephemeral=True
    )


@bot.tree.command(name="reload", description="Reloads the bot's commands (Admin only)")
async def reload(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ No permission.", ephemeral=True)
        return

    for guild_id in TEST_GUILDS:
        guild = discord.Object(id=guild_id)
        synced = await bot.tree.sync(guild=guild)
        print(f"🔄 Reloaded {len(synced)} commands in guild {guild_id}")
    await interaction.response.send_message("✅ Commands reloaded.", ephemeral=True)


@bot.tree.command(name="test", description="Test if the bot is working")
async def test(interaction: discord.Interaction):
    await interaction.response.send_message("✅ Test successful!", ephemeral=True)


# ---------------------------
# Events
# ---------------------------
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} ({bot.user.id})")

    for guild_id in TEST_GUILDS:
        guild = discord.Object(id=guild_id)
        synced = await bot.tree.sync(guild=guild)
        print(f"📜 Synced {len(synced)} commands to guild {guild_id}")


# ---------------------------
# Run bot
# ---------------------------
bot.run(TOKEN)

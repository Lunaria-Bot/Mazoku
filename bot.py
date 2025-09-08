import os
import json
import discord
from discord import app_commands
from discord.ext import commands

DATA_FILE = "botdata.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"settings": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

data = load_data()

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# constants for summon detection
CAPTAIN_HOOK_ID = 1412644989908946954  # the user sending High Tier summons
HIGH_TIER_ROLE_ID = 1410321968279977985  # role required for receiving alerts

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} ({bot.user.id})")
    try:
        for guild in bot.guilds:
            synced = await bot.tree.sync(guild=guild)
            print(f"📜 Synced {len(synced)} commands to guild {guild.id}")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

@bot.tree.command(name="settings", description="Enable or disable DM notifications")
@app_commands.describe(dm_enabled="True to enable, False to disable")
async def settings(interaction: discord.Interaction, dm_enabled: bool):
    user_id = str(interaction.user.id)
    data.setdefault("settings", {})[user_id] = {"dm_enabled": dm_enabled}
    save_data(data)
    await interaction.response.send_message(f"✅ DM notifications {'enabled' if dm_enabled else 'disabled'}", ephemeral=True)

@bot.tree.command(name="reload", description="Reload slash commands (Admin only)")
async def reload(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You do not have permission.", ephemeral=True)
        return
    try:
        synced = await bot.tree.sync(guild=interaction.guild)
        await interaction.response.send_message(f"✅ Reloaded {len(synced)} commands.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Reload failed: {e}", ephemeral=True)

@bot.tree.command(name="test", description="Simulate a High Tier Summon alert (Admin only)")
async def test(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You do not have permission.", ephemeral=True)
        return

    role = interaction.guild.get_role(HIGH_TIER_ROLE_ID)
    if not role:
        await interaction.response.send_message("⚠️ High Tier role not found in this server.", ephemeral=True)
        return

    sent_count = 0
    for member in role.members:
        user_id = str(member.id)
        prefs = data.get("settings", {}).get(user_id, {})
        if prefs.get("dm_enabled", True):  # default = enabled
            try:
                await member.send(
                    f"⚠️ **High Tier Summon detected (TEST)** ⚠️\n"
                    f"Check it here: https://discord.com/channels/{interaction.guild.id}/{interaction.channel.id}/{interaction.id}"
                )
                sent_count += 1
            except discord.Forbidden:
                continue

    await interaction.response.send_message(f"✅ Test alert sent to {sent_count} members with the High Tier role.")

if __name__ == "__main__":
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        raise RuntimeError("❌ DISCORD_BOT_TOKEN environment variable not set!")
    bot.run(token)

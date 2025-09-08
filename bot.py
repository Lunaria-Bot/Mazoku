import os
import discord
from discord import app_commands
from discord.ext import commands

# Your test guilds
TEST_GUILDS = [1373066824278605874, 1399784437440319508]

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

# --- Slash commands (must be declared before on_ready) ---

@bot.tree.command(name="test", description="Test High Tier Summon DM")
async def test(interaction: discord.Interaction):
    await interaction.response.send_message("✅ Test command works!", ephemeral=True)

@bot.tree.command(name="settings", description="Update your DM preferences")
@app_commands.describe(dm_enabled="Enable or disable DM notifications (true/false)")
async def settings(interaction: discord.Interaction, dm_enabled: bool):
    await interaction.response.send_message(
        f"✅ DM notifications {'enabled' if dm_enabled else 'disabled'}",
        ephemeral=True
    )

@bot.tree.command(name="reload", description="Reload slash commands (admin only)")
async def reload(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You do not have permission.", ephemeral=True)
        return

    reloaded = 0
    for guild_id in TEST_GUILDS:
        guild = discord.Object(id=guild_id)
        synced = await bot.tree.sync(guild=guild)
        reloaded += len(synced)
    await interaction.response.send_message(f"✅ Reloaded {reloaded} commands", ephemeral=True)

# --- Events ---

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} ({bot.user.id})")

    try:
        for guild_id in TEST_GUILDS:
            guild = discord.Object(id=guild_id)
            synced = await bot.tree.sync(guild=guild)
            print(f"📜 Synced {len(synced)} commands to guild {guild_id}")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

# --- Run bot ---
if __name__ == "__main__":
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        raise RuntimeError("❌ DISCORD_BOT_TOKEN not set!")
    bot.run(token)

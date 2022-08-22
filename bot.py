import discord
from discord.ext import commands
from discord import guild
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option
from dotenv import load_dotenv

client = commands.Bot(command_prefix="$")
slash = SlashCommand(client, sync_commands=True)
token = "MTAxMTM0OTI5NDQ5NTgzODMyOQ.Gvg2zG.tssIbqSl9rSMC2vii5FOY5FLtdG5yA1U5ze0bA"

@slash.slash(
    name="hello"
    description="Just sends a message",
    guild_ids=[218070024894676993]
)
async def _hello(ctx:SlashContext):
    await ctx.send("World!")

client.run(token)

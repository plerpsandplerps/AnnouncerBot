import interactions
import discord

bot = interactions.Client(token="MTAxMTM0OTI5NDQ5NTgzODMyOQ.Gvg2zG.tssIbqSl9rSMC2vii5FOY5FLtdG5yA1U5ze0bA")

@bot.command(
    name="Action",
    description="Number between one and nine",
    scope=1011380009010724924,
)
async def first_command(ctx: interactions.CommandContext):
    await ctx.send("Hi there!")

@bot.command(
    name="Other",
    description="Set Destination or Item target",
    scope=1011380009010724924,
)
async def second_command(ctx: interactions.CommandContext):
    await ctx.send("Hi there!")

@bot.command(
        name="Player",
        description="Set a Player target",
        scope=1011380009010724924,
    )
async def third_command(ctx: interactions.CommandContext):
    await ctx.send("Hi there!")

@bot.command(
        name="Printout",
        description="Fetch most recent printout",
        scope=1011380009010724924,
    )
async def fourth_command(ctx: interactions.CommandContext):
    await ctx.send("Hi there!")

bot.start ()

import interactions
import discord

bot = interactions.Client(token="MTAxMTM0OTI5NDQ5NTgzODMyOQ.Gvg2zG.tssIbqSl9rSMC2vii5FOY5FLtdG5yA1U5ze0bA")

@bot.event
async def on_ready():
    print(f"We're online! We've logged in as {bot.me.name}.")
    print(f"Our latency is {round(bot.latency)} ms.")

@bot.event(name="on_message_create")
async def name_this_however_you_want(message: interactions.Message):
    print(
        f"We've received a message from {message.author.username}. The message is: {message.content}."
    )

@bot.command(
    name="action",
    description="number between one and nine",
    scope=1011380009010724924,
)
async def first_command(ctx: interactions.CommandContext):
    await ctx.send("DM @Sabrina the Teenage Lich#8706 if you want access to the test env")

@bot.command(
    name="other",
    description="set destination or item target",
    scope=1011380009010724924,
)
async def second_command(ctx: interactions.CommandContext):
    await ctx.send("DM @Sabrina the Teenage Lich#8706 if you want access to the test env")

@bot.command(
        name="player",
        description="set a player target",
        scope=1011380009010724924,
    )
async def third_command(ctx: interactions.CommandContext):
    await ctx.send("DM @Sabrina the Teenage Lich#8706 if you want access to the test env")

@bot.command(
        name="printout",
        description="fetch most recent printout",
        scope=1011380009010724924,
    )
async def fourth_command(ctx: interactions.CommandContext):
    await ctx.send("DM @Sabrina the Teenage Lich#8706 if you want access to the test env")

bot.start ()

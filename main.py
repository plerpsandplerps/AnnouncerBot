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
    name="lightattack",
    description="1turn. attack a player in your area for 950. gain 1rage.",
    scope=1011380009010724924,
    options = [
        interactions.Option(
            name="playertarget",
            description="who you want to light attack",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)
async def first_command(ctx: interactions.CommandContext, playertarget: str):
    await ctx.send(f"You will use light attack on '{playertarget}'!")

@bot.command(
    name="normalattack",
    description="2turn. attack a player in your area for 2300.gain 2rage.",
    scope=1011380009010724924,
    options = [
        interactions.Option(
            name="playertarget",
            description="who you want to normal attack",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)
async def second_command(ctx: interactions.CommandContext, playertarget: str):
    await ctx.send("DM me if you want access to the test env")

@bot.command(
    name="heavyattack",
    description="3turn. attack a player in your area for 3650.gain 3rage.",
    scope=1011380009010724924,
    options = [
        interactions.Option(
            name="playertarget",
            description="who you want to heavy attack",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)
async def third_command(ctx: interactions.CommandContext, playertarget: str):
    await ctx.send("DM me if you want access to the test env")

@bot.command(
    name="interrupt",
    description="1turn. deal 4200 damage to your target if they are resting or evading",
    scope=1011380009010724924,
    options = [
        interactions.Option(
            name="playertarget",
            description="who you want to interrupt",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)
async def fourth_command(ctx: interactions.CommandContext, playertarget: str):
    await ctx.send("DM me if you want access to the test env")

@bot.command(
    name="evade",
    description="2turn. for the duration receive no damage from sources other than interrupts",
    scope=1011380009010724924,
)
async def fifth_command(ctx: interactions.CommandContext):
    await ctx.send("DM me if you want access to the test env")

@bot.command(
    name="rest",
    description="2turn. heal one quarter of your missing health each turn",
    scope=1011380009010724924,
)
async def sixth_command(ctx: interactions.CommandContext):
    await ctx.send("DM me if you want access to the test env")

@bot.command(
    name="travel",
    description="set destination",
    scope=1011380009010724924,
    options = [
        interactions.Option(
            name="destination",
            description="travel to any area from the crossroads or travel from any area to the crossroads",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)
async def seventh_command(ctx: interactions.CommandContext, destination: str):
    await ctx.send("DM me if you want access to the test env")

@bot.command(
    name="exchange",
    description="choose a player in the area. give that player an unused item from your inventory",
    scope=1011380009010724924,
    options = [
        interactions.Option(
            name="unusedinventoryitem",
            description="choose an unused item from your inventory",
            type=interactions.OptionType.STRING,
            required=True,
        ),
        interactions.Option(
            name="playertarget",
            description="who you want to give your item to",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)
async def eigth_first_command(ctx: interactions.CommandContext, playertarget: str, unusedinventoryitem: str):
    await ctx.send("DM me if you want access to the test env")

@bot.command(
    name="loot",
    description="roll 1d4. on 4 or higher gain two random items. low roll loses 0.25 of their current health",
    scope=1011380009010724924,
)
async def eigth_second_command(ctx: interactions.CommandContext):
    await ctx.send("DM me if you want access to the test env")

@bot.command(
    name="farm",
    description="roll 1d4. gain that many seed coins.",
    scope=1011380009010724924,
)
async def eigth_third_command(ctx: interactions.CommandContext):
    await ctx.send("DM me if you want access to the test env")

@bot.command(
    name="aid",
    description="roll 1d4. high roll heals their chosen player for 0.25 of their missing health",
    scope=1011380009010724924,
    options = [
        interactions.Option(
            name="playertarget",
            description="choose the player you wish to heal",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)
async def eigth_fourth_command(ctx: interactions.CommandContext, playertarget: str):
    await ctx.send("DM me if you want access to the test env")

@bot.command(
    name="battlelich",
    description="roll 1d4. if you are the highest roller and rolled 5 gain the lich item",
    scope=1011380009010724924,
)
async def eigth_fifth_command(ctx: interactions.CommandContext):
    await ctx.send("DM me if you want access to the test env")

@bot.command(
    name="trade",
    description="exchange seed coins for an item",
    scope=1011380009010724924,
    options = [
        interactions.Option(
            name="shopitem",
            description="choose an item in the shop you wish to purchase",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)
async def eigth_sixth_command(ctx: interactions.CommandContext, shopitem: str):
    await ctx.send("DM me if you want access to the test env")

@bot.command(
    name="drinkingchallenge",
    description="roll 1d4. high roll adds 420 damage to a random attack. low roller loses 0.25 of their current hp",
    scope=1011380009010724924,
)
async def eigth_seventh_command(ctx: interactions.CommandContext):
    await ctx.send("DM me if you want access to the test env")

@bot.command(
    name="useitem",
    description="choose an unused item in your inventory and use it",
    scope=1011380009010724924,
    options = [
        interactions.Option(
            name="unusedinventoryitem",
            description="choose an item in your inventory you want to use",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)
async def ninth_command(ctx: interactions.CommandContext, unusedinventoryitem: str):
    await ctx.send("DM me if you want access to the test env")

@bot.command(
        name="printout",
        description="fetch most recent printout",
        scope=1011380009010724924,
    )
async def tenth_command(ctx: interactions.CommandContext):
    await ctx.send("DM me if you want access to the test env")

bot.start ()

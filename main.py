import interactions
from interactions import Button, ButtonStyle, SelectMenu, SelectOption, ActionRow
import discord

crossroads = 1011675481403310153
dungeon = 1011675534066974770
farmland = 1011675659992571914
keep = 1011675740535787530
lichcastle = 1011675767295451228
shop = 1011675826741325834
tavern = 1011675868726304868
guildid= 1011380009010724924
bot = interactions.Client(token="MTAxMTM0OTI5NDQ5NTgzODMyOQ.Gvg2zG.tssIbqSl9rSMC2vii5FOY5FLtdG5yA1U5ze0bA", intents=interactions.Intents.DEFAULT | interactions.Intents.GUILD_MESSAGE_CONTENT)

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
    scope=guildid,
    options = [
        interactions.Option(
            name="playertarget",
            type=interactions.OptionType.USER,
            description="who you want to light attack",
            required=True,
        ),
    ],
)
async def first_command(ctx: interactions.CommandContext, playertarget: str):
    await ctx.send(f"You will use light attack on '{playertarget}'!", ephemeral=True)

@bot.command(
    name="altattack",
    description="1turn. attack a player in your area for 950. gain 1rage.",
    scope=guildid,
)
async def altattack_command(ctx: interactions.CommandContext,):
    select_menu = SelectMenu(
        custom_id="lightattackalt",
        options=[
            SelectOption(label="User 1", value="User-1"),
            SelectOption(label="User 2", value="User-2"),
        ],
        placeholder="Select a player target",
    )
    await ctx.send("Pick a player target in your area", components=select_menu, ephemeral=True)

@bot.command(
    name="normalattack",
    description="2turn. attack a player in your area for 2300.gain 2rage.",
    scope=guildid,
    options = [
        interactions.Option(
            name="playertarget",
            description="who you want to normal attack",
            type=interactions.OptionType.USER,
            required=True,
        ),
    ],
)
async def second_command(ctx: interactions.CommandContext, playertarget: str):
    await ctx.send(f"You will use normal attack on '{playertarget}'!", ephemeral=True)

@bot.command(
    name="heavyattack",
    description="3turn. attack a player in your area for 3650.gain 3rage.",
    scope=guildid,
    options = [
        interactions.Option(
            name="playertarget",
            description="who you want to heavy attack",
            type=interactions.OptionType.USER,
            required=True,
        ),
    ],
)
async def third_command(ctx: interactions.CommandContext, playertarget: str):
    await ctx.send(f"You will use heavy attack on '{playertarget}'!", ephemeral=True)

@bot.command(
    name="interrupt",
    description="1turn. deal 4200 damage to your target if they are resting or evading",
    scope=guildid,
    options = [
        interactions.Option(
            name="playertarget",
            description="who you want to interrupt",
            type=interactions.OptionType.USER,
            required=True,
        ),
    ],
)
async def fourth_command(ctx: interactions.CommandContext, playertarget: str):
    await ctx.send(f"You will use interrupt on '{playertarget}'!", ephemeral=True)

@bot.command(
    name="evade",
    description="2turn. for the duration receive no damage from sources other than interrupts",
    scope=guildid,
)
async def fifth_command(ctx: interactions.CommandContext):
    await ctx.send("You will receive no damage from sources other than interrupts.", ephemeral=True)

@bot.command(
    name="rest",
    description="2turn. heal one quarter of your missing health each turn",
    scope=guildid,
)
async def sixth_command(ctx: interactions.CommandContext):
    await ctx.send("You will heal one quarter of your missing health each turn", ephemeral=True)

@bot.command(
    name="traveltocrossroads",
    description="travel to the crossroads from any area",
    scope=guildid,
)
async def seventh_to_command(ctx: interactions.CommandContext):
    await ctx.send(f"You will travel to the Crossroads!", ephemeral=True)
    await ctx.author.remove_role(dungeon, guildid)
    await ctx.author.remove_role(farmland, guildid)
    await ctx.author.remove_role(keep, guildid)
    await ctx.author.remove_role(lichcastle, guildid)
    await ctx.author.remove_role(shop, guildid)
    await ctx.author.remove_role(tavern, guildid)
    await ctx.author.add_role(crossroads, guildid)

@bot.command(
    name="travelfromcrossroads",
    description="set destination",
    scope=guildid,
    options = [
        interactions.Option(
            name="destination",
            description="travel to any area from the crossroads",
            type=interactions.OptionType.ROLE,
            required=True,
        ),
    ],
)
async def seventh_from_command(ctx: interactions.CommandContext, destination: str):
    if crossroads not in ctx.author.roles:
        return await ctx.send("You aren't in the crossroads! You must use / traveltocrossroads first!", ephemeral=True)
    await ctx.send(f"You will travel to the {destination.mention}!", ephemeral=True)
    await ctx.author.remove_role(crossroads, guildid)
    await ctx.author.add_role(destination, guildid)

@bot.command(
    name="exchange",
    description="choose a player in the area. give that player an unused item from your inventory",
    scope=guildid,
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
            type=interactions.OptionType.USER,
            required=True,
        ),
    ],
)
async def eigth_first_command(ctx: interactions.CommandContext, playertarget: str, unusedinventoryitem: str):
    await ctx.send(f"You will give '{unusedinventoryitem}' to '{playertarget}'!", ephemeral=True)

@bot.command(
    name="loot",
    description="roll 1d4. on 4 or higher gain two random items. low roll loses 0.25 of their current health",
    scope=guildid,
)
async def eigth_second_command(ctx: interactions.CommandContext):
    await ctx.send("You will attempt to loot the dungeon!", ephemeral=True)

@bot.command(
    name="farm",
    description="roll 1d4. gain that many seed coins.",
    scope=guildid,
)
async def eigth_third_command(ctx: interactions.CommandContext):
    await ctx.send("You will gain 1d4 seed coins!", ephemeral=True)

@bot.command(
    name="aid",
    description="roll 1d4. high roll heals their chosen player for 0.25 of their missing health",
    scope=guildid,
    options = [
        interactions.Option(
            name="playertarget",
            description="choose the player you wish to heal",
            type=interactions.OptionType.USER,
            required=True,
        ),
    ],
)
async def eigth_fourth_command(ctx: interactions.CommandContext, playertarget: str):
    await ctx.send(f"You will attempt to heal '{playertarget}'!", ephemeral=True)

@bot.command(
    name="battlelich",
    description="roll 1d4. if you are the highest roller and rolled 5 gain the lich item",
    scope=guildid,
)
async def eigth_fifth_command(ctx: interactions.CommandContext):
    await ctx.send("You will attempt to battle the lich!", ephemeral=True)

@bot.command(
    name="trade",
    description="exchange seed coins for an item",
    scope=guildid,
    options = [
        interactions.Option(
            name="shopitem",
            description="choose an item in the shop you wish to purchase",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)
async def eigth_sixth_command(ctx: interactions.CommandContext, shopitem:str):
    await ctx.send(f"You will purchase '{shopitem}' !", ephemeral=True)

@bot.command(
    name="drinkingchallenge",
    description="roll 1d4. high roll adds 420 damage to a random attack. low roller loses 0.25 of their current hp",
    scope=guildid,
)
async def eigth_seventh_command(ctx: interactions.CommandContext):
    await ctx.send("You will try to best the rest in a drinking challenge!", ephemeral=True)

@bot.command(
    name="useitem",
    description="choose an unused item in your inventory and use it",
    scope=guildid,
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
    await ctx.send(f"You will use '{unusedinventoryitem}'!", ephemeral=True)

@bot.command(
        name="printout",
        description="fetch most recent printout",
        scope=guildid,
    )
async def tenth_command(ctx: interactions.CommandContext):
    await ctx.send("DM me if you want access to the test env", ephemeral=True)

bot.start ()

import interactions
from interactions import Button, ButtonStyle, SelectMenu, SelectOption, ActionRow, spread_to_rows
import discord
import asyncio
from datetime import datetime
import time
import math
import json


crossroads = 1011675481403310153
dungeon = 1011675534066974770
farmland = 1011675659992571914
keep = 1011675740535787530
lichcastle = 1011675767295451228
shop = 1011675826741325834
tavern = 1011675868726304868
guildid= 1011380009010724924
poisonchannel= 1011701650798424185
bot = interactions.Client(token="MTAxMTM0OTI5NDQ5NTgzODMyOQ.Gvg2zG.tssIbqSl9rSMC2vii5FOY5FLtdG5yA1U5ze0bA", intents=interactions.Intents.DEFAULT | interactions.Intents.GUILD_MESSAGE_CONTENT)

#new poison
poison to world.json to keep it consistent between script reboots
@bot.event
async def on_ready():
   print(f"We're online! We've logged in as {bot.me.name}.")
   print(f"Our latency is {round(bot.latency)} ms.")
   current_time = int(time.time())
   print(f"Started at {current_time}")
   smalltime=int(86400)
   smalltimeunit="days"
   countdown=int(300)
   current_time = int(time.time())
   futuretime=int(countdown + current_time)
   world = await getworlddata()
   channel = await interactions.get(bot, interactions.Channel, object_id=poisonchannel)
   if str("poisondate") in players:
       print(f"poison date already exists!")
       return False
       with open("world.json", "r") as h:
       #pull poison info from json into pull variables
       poisondate_pull = world["poisondate"]
       poison_pull = world["poison"]
       print (f"poison date {poisondate_pull} and poison {poison_pull}")
       await channel.send(f"The next poison comes <t:{poisondate_pull}> dealing {poison_pull} damage.")
   else:
       world[] = {}
       world["poisondate"] = futuretime
       world["poison"] = 0
       with open("world.json","w") as h:
           json.dump(world,f, indent=4)
       await channel.send(f"Poison is coming in {int(countdown/smalltime)} {smalltimeunit}. Poison will begin <t:{futuretime}>.")
       await channel.send(f"Poison is coming in {int(countdown/smalltime)} {smalltimeunit}. Poison will begin <t:{futuretime}>.")
   await asyncio.sleep(countdown)
   world = await getworlddata()
   poisondate_pull = world["poisondate"]
   poison_pull = world["poison"]
   while poison_pull < 20000:
       poison_pull=poison_pull+100
       countdown=math.ceil(countdown*.75)
       current_time=int(time.time())
       futuretime=int(current_time+countdown)
       print(f"{poison_pull} poison damage")
       print(f"{countdown} seconds till next poison")
       await channel.send(f"Poison damage increased by 100, then dealt **{poison_pull} damage** to everyone! The time between poison damage decreases by 25%! The next poison damage will occur on <t:{futuretime}> (in {countdown} seconds)." )
       actually damage everyone lol
       world["poisondate"] = futuretime
       world["poison"] = poison_pull
       with open("world.json","w") as h:
          json.dump(world,f, indent=4)
       await asyncio.sleep(countdown)

@bot.event(name="on_message_create")
async def listen(message: interactions.Message):
    print(
        f"We've received a message from {message.author.username}. The message is: {message.content}."
    )

# old poison
#@bot.event
#async def on_ready():
#    print(f"We're online! We've logged in as {bot.me.name}.")
#    print(f"Our latency is {round(bot.latency)} ms.")
#    current_time = int(time.time())
#    print(f"Started at {current_time}")
#    smalltime=int(86400)
#    smalltimeunit="days"
#    countdown=int(14*smalltime)
#    futuretime=int(countdown + current_time)
#    Poison=0
#    channel = await interactions.get(bot, interactions.Channel, object_id=poisonchannel)
#    await channel.send(f"Poison is coming in {int(countdown/smalltime)} {smalltimeunit}. Poison will begin <t:{futuretime}>.")
#    await asyncio.sleep(countdown)
#    while Poison < 20000:
#            Poison=Poison+100
#            countdown=math.ceil(countdown*.75)
#            current_time=int(time.time())
#            futuretime=int(current_time+countdown)
#            print(f"{Poison} poisons")
#            print(f"{countdown}s")
#            await channel.send(f"Poison damage increased by 100, then dealt **{Poison} damage** to everyone! The time between poison damage decreases by 25%! The next poison damage will occur on <t:{futuretime}> (in {countdown} seconds)." )
#            await asyncio.sleep(countdown)
#

#pulls player.json into dict
async def getplayerdata():
    with open("players.json","r") as f:
        players = json.load(f)
    return players

#this pulls the bounty data into dict
async def getbountydata():
    with open("bounties.json","r") as g:
        startingbounties = json.load(g)
    return bounties

#pulls world.json into dict
async def getworlddata():
    with open("world.json","r") as h:
        world = json.load(h)
    return world

@bot.command(
    name="join",
    description="join the game!",
    scope=guildid,
)
async def join_command(ctx: interactions.CommandContext):
    players = await getplayerdata()
    # need to add:
    # check for bounties
    # bounties = await getbountydata()
    # depends on adding poison to world.json first:
        # check for poisondate (if join b4 poison, 10SC+bounty and 10000hp, otherwise min(SC)-1 and MIN(HP)-1)
    if str(ctx.author.id) in players:
        await ctx.send(f"Failed to Join! {ctx.author} already exists as a player! ")
        return False
    else:
        await ctx.author.add_role(crossroads, guildid)
        current_time = int(time.time())
        countdown=int(300)
        #if str(ctx.author.id) in bounties:
        #    bounty_pull = startingbounties[str(ctx.author.id)]["bounty"]
        #    await ctx.send(f"{ctx.author} has claimed prior bounties for {bounty_pull}!")
        players[str(ctx.author.id)] = {}
        players[str(ctx.author.id)]["HP"] = 10000
        players[str(ctx.author.id)]["Location"] = "Crossroads"
        players[str(ctx.author.id)]["SC"] = 10 #+ bounty_pull
        players[str(ctx.author.id)]["Rage"] = 0
        players[str(ctx.author.id)]["ReadyInventory"] = ""
        players[str(ctx.author.id)]["UsedInventory"] = ""
        players[str(ctx.author.id)]["DelayDate"] = current_time+countdown
        players[str(ctx.author.id)]["Delay"] = True
        players[str(ctx.author.id)]["Evade"] = False
        players[str(ctx.author.id)]["Rest"] = False
        players[str(ctx.author.id)]["Lastaction"] = "Start"
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
        print(f"Created {ctx.author.id} player in players.json")
        players = await getplayerdata()
        hp_pull = players[str(ctx.author.id)]["HP"]
        # hpmoji = write code to convert hp to emojis if i still want to
        location_pull = players[str(ctx.author.id)]["Location"]
        SC_pull = players[str(ctx.author.id)]["SC"]
        Rage_pull = players[str(ctx.author.id)]["Rage"]
        ReadyInventory_pull = players[str(ctx.author.id)]["ReadyInventory"]
        UsedInventory_pull = players[str(ctx.author.id)]["UsedInventory"]
        DelayDate_pull = players[str(ctx.author.id)]["DelayDate"]
        Delay_pull = players[str(ctx.author.id)]["Delay"]
        Evade_pull = players[str(ctx.author.id)]["Evade"]
        Rest_pull = players[str(ctx.author.id)]["Rest"]
        Lastaction_pull = players[str(ctx.author.id)]["Lastaction"]
        await ctx.send(f"{ctx.author}'s HP: {hp_pull} \nLocation: {location_pull} \nSC: {SC_pull} \nRage: {Rage_pull} \nInventory: \n    Ready: {ReadyInventory_pull} \n    Used:{UsedInventory_pull} \nDelay: <t:{DelayDate_pull}> ({Delay_pull})")
        await asyncio.sleep(countdown)
        await ctx.send(f"<@{ctx.author.id}> your countdown is over!")

@bot.command(
    name="lightattack",
    description="24h. attack a player in your area for 950. gain 1rage.",
    scope=guildid,
    options = [
        interactions.Option(
            # limit targets to those in area here
            name="playertarget",
            type=interactions.OptionType.USER,
            description="who you want to light attack",
            required=True,
        ),
    ],
)
async def first_command(ctx: interactions.CommandContext, playertarget: str):
    players = await getplayerdata()
    Delay_pull = players[str(ctx.author.id)]["Delay"]
    DelayDate_pull = players[str(ctx.author.id)]["DelayDate"]
    if str(ctx.author.id) in players:
        if Delay_pull:
            await ctx.send(f"You cannot act yet! You are delayed until <t:{DelayDate_pull}>.", ephemeral = False)
        else:
            # damagebuff =
            # damage = 950 + damagebuff
            # dump to json targethp = players[str(playertarget.id)]["HP"] - damage
            # put message to target in here with current hp
            # hpmoji = write code to convert hp to emojis if i still want to
            # add delay
            # countdown=86400 #seconds in a day
            # dump to json delay = True
            # current_time = int(time.time())
            # dump to json delay_date = countdown + current_time
            await ctx.send(f"You use light attack on '{playertarget}'! and are delayed for 24h", ephemeral=False)
            # await asyncio.sleep(countdown) #sleep
            # await ctx.send(f"Your delay is over!")
    else:
        await ctx.send(f"You need to join with /join before you can do that!")

@bot.command(
    name="normalattack",
    description="48h. attack a player in your area for 2300. gain 2rage.",
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
    players = await getplayerdata()
    Delay_pull = players[str(ctx.author.id)]["Delay"]
    DelayDate_pull = players[str(ctx.author.id)]["DelayDate"]
    if str(ctx.author.id) in players:
        if Delay_pull :
            await ctx.send(f"You cannot act yet! You are delayed until <t:{DelayDate_pull}>.", ephemeral = False)
        else:
            # damagebuff =
            # damage = 2300 + damagebuff
            # dump to json targethp = players[str(playertarget.id)]["HP"] - damage
            # put message to target in here with current hp
            # hpmoji = write code to convert hp to emojis if i still want to
            # add delay
            # countdown=int(86400*2) #seconds in two days
            # dump to json delay = True
            # current_time = int(time.time())
            # dump to json delay_date = countdown + current_time
            await ctx.send(f"You use normal attack on '{playertarget}'! and are delayed for 48h", ephemeral=False)
            # await asyncio.sleep(countdown) #sleep
            # await ctx.send(f"Your delay is over!")
    else:
        await ctx.send(f"You need to join with /join before you can do that!")

@bot.command(
    name="heavyattack",
    description="72h. attack a player in your area for 3650. gain 3rage.",
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
    players = await getplayerdata()
    Delay_pull = players[str(ctx.author.id)]["Delay"]
    DelayDate_pull = players[str(ctx.author.id)]["DelayDate"]
    if str(ctx.author.id) in players:
        if Delay_pull:
            await ctx.send(f"You cannot act yet! You are delayed until <t:{DelayDate_pull}>.", ephemeral = False)
        else:
            # damagebuff =
            # damage = 3650 + damagebuff
            # dump to json targethp = players[str(playertarget.id)]["HP"] - damage
            # put message to target in here with current hp
            # hpmoji = write code to convert hp to emojis if i still want to
            # add delay
            # countdown=int(86400*3) #seconds in three days
            # dump to json delay = True
            # current_time = int(time.time())
            # dump to json delay_date = countdown + current_time
            await ctx.send(f"You use heavy attack on '{playertarget}'! and are delayed for 72h", ephemeral=False)
            # await asyncio.sleep(countdown) #sleep
            # await ctx.send(f"Your delay is over!")
    else:
        await ctx.send(f"You need to join with /join before you can do that!")

@bot.command(
    name="interrupt",
    description="24h. deal 4200 damage to your target if they are resting or evading",
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
    players = await getplayerdata()
    Delay_pull = players[str(ctx.author.id)]["Delay"]
    DelayDate_pull = players[str(ctx.author.id)]["DelayDate"]
    if str(ctx.author.id) in players:
        if Delay_pull:
            await ctx.send(f"You cannot act yet! You are delayed until <t:{DelayDate_pull}>.", ephemeral = False)
        else:
            # damagebuff =
            # evaderest = check for evaderest of target
            # damage = 0 + (if evaderest 4200)
            # dump to json targethp = players[str(playertarget.id)]["HP"] - damage
            # put message to target in here with current hp
            # hpmoji = write code to convert hp to emojis if i still want to
            # add delay
            # countdown=int(86400*1) #seconds in one day
            # dump to json delay = True
            # current_time = int(time.time())
            # dump to json delay_date = countdown + current_time
            await ctx.send(f"You use interrupt on '{playertarget}'! and are delayed for 24h", ephemeral=False)
            # await asyncio.sleep(countdown) #sleep
            # await ctx.send(f"Your delay is over!")
    else:
        await ctx.send(f"You need to join with /join before you can do that!")

@bot.command(
    name="evade",
    description="48h. for the duration receive no damage from sources other than interrupts",
    scope=guildid,
)
async def fifth_command(ctx: interactions.CommandContext, playertarget: str):
    players = await getplayerdata()
    Delay_pull = players[str(ctx.author.id)]["Delay"]
    DelayDate_pull = players[str(ctx.author.id)]["DelayDate"]
    if str(ctx.author.id) in players:
        if Delay_pull:
            await ctx.send(f"You cannot act yet! You are delayed until <t:{DelayDate_pull}>.", ephemeral = False)
        else:
            # dump to json evade = true
            # add delay
            countdown=int(86400*2) #seconds in two days
            # dump to json delay = True
            current_time = int(time.time())
            # dump to json delay_date = countdown + current_time
            await ctx.send(f"You use evade and are delayed for 48h", ephemeral=False)
            # await asyncio.sleep(countdown) #sleep
            # await ctx.send(f"Your delay is over!")
    else:
        await ctx.send(f"You need to join with /join before you can do that!")

@bot.command(
    name="rest",
    description="48h. heal one quarter of your missing health each turn",
    scope=guildid,
)
async def sixth_command(ctx: interactions.CommandContext, playertarget: str):
    players = await getplayerdata()
    Delay_pull = players[str(ctx.author.id)]["Delay"]
    DelayDate_pull = players[str(ctx.author.id)]["DelayDate"]
    if str(ctx.author.id) in players:
        if Delay_pull:
            await ctx.send(f"You cannot act yet! You are delayed until <t:{DelayDate_pull}>.", ephemeral = False)
        else:
            # dump to json rest = true
            # add delay
            countdown=int(86400*2) #seconds in two days
            # dump to json delay = True
            current_time = int(time.time())
            # HP_pull = players[str(ctx.author.id)]["DelayDate"]
            # missing_health =
            # dump to json delay_date = countdown + current_time
            await ctx.send(f"You heal for half of your missing health!", ephemeral=False)
            # await asyncio.sleep(countdown) #sleep
            # await ctx.send(f"Your delay is over!")
    else:
        await ctx.send(f"You need to join with /join before you can do that!")

@bot.command(
    name="traveltocrossroads",
    description="24h. travel to the crossroads from any area",
    scope=guildid,
)
async def seventh_to_command(ctx: interactions.CommandContext):
    players = await getplayerdata()
    await ctx.send(f"You travel to the Crossroads!", ephemeral=False)
    await ctx.author.remove_role(dungeon, guildid)
    await ctx.author.remove_role(farmland, guildid)
    await ctx.author.remove_role(keep, guildid)
    await ctx.author.remove_role(lichcastle, guildid)
    await ctx.author.remove_role(shop, guildid)
    await ctx.author.remove_role(tavern, guildid)
    await ctx.author.add_role(crossroads, guildid)

@bot.command(
    name="travelfromcrossroads",
    description="24h. travel anywhere from the crossroads",
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
        return await ctx.send("You aren't in the crossroads! You must use / traveltocrossroads first!", ephemeral=False)
    await ctx.send(f"You travel to {destination.mention}!", ephemeral=False)
    players = await getplayerdata()
    await ctx.author.remove_role(crossroads, guildid)
    await ctx.author.add_role(destination, guildid)

@bot.command(
    name="exchange",
    description="choose a player in your area. give that player an unused item from your inventory",
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
    players = await getplayerdata()
    await ctx.send(f"You give '{unusedinventoryitem}' to '{playertarget}'!", ephemeral=False)

@bot.command(
    name="loot",
    description="roll 1d100. high score: get two random items. low score: lose 0.25 of your current health",
    scope=guildid,
)
async def eigth_second_command(ctx: interactions.CommandContext):
    players = await getplayerdata()
    roll = random.randint(1,100)
    await ctx.send("You attempt to loot the dungeon!", ephemeral=False)

@bot.command(
    name="farm",
    description="roll 1d4. gain that many seed coins.",
    scope=guildid,
)
async def eigth_third_command(ctx: interactions.CommandContext):
    players = await getplayerdata()
    roll = random.randint(1,4)
    await ctx.send("You gain 1d4 seed coins!", ephemeral=False)

@bot.command(
    name="aid",
    description="roll 1d100. high score: heal chosen player for 0.25 of their missing health",
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
    roll = random.randint(1,100)
    await ctx.send(f"You heal '{playertarget}'!", ephemeral=False)

@bot.command(
    name="battlelich",
    description="roll 1d100. high score > 90: gain magic orb",
    scope=guildid,
)
async def eigth_fifth_command(ctx: interactions.CommandContext):
    roll = random.randint(1,100)
    players = await getplayerdata()
    await ctx.send("You defeat the lich!", ephemeral=False)

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
    players = await getplayerdata()
    await ctx.send(f"You purchase '{shopitem}' !", ephemeral=False)

@bot.command(
    name="drinkingchallenge",
    description="roll 1d100. high score: add 420 damage to a random attack. low score: lose 0.25 current hp",
    scope=guildid,
)
async def eigth_seventh_command(ctx: interactions.CommandContext):
    players = await getplayerdata()
    await ctx.send("You best the rest in a drinking challenge!", ephemeral=False)

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
    players = await getplayerdata()
    await ctx.send(f"You use '{unusedinventoryitem}'!", ephemeral=False)

@bot.command(
        name="printout",
        description="fetch most recent printout",
        scope=guildid,
    )
async def tenth_command(ctx: interactions.CommandContext):
    players = await getplayerdata()
    hp_pull = players[str(ctx.author.id)]["HP"]
    location_pull = players[str(ctx.author.id)]["Location"]
    SC_pull = players[str(ctx.author.id)]["SC"]
    Rage_pull = players[str(ctx.author.id)]["Rage"]
    ReadyInventory_pull = players[str(ctx.author.id)]["ReadyInventory"]
    UsedInventory_pull = players[str(ctx.author.id)]["UsedInventory"]
    DelayDate_pull = players[str(ctx.author.id)]["DelayDate"]
    Delay_pull = players[str(ctx.author.id)]["Delay"]
    Evade_pull = players[str(ctx.author.id)]["Evade"]
    Rest_pull = players[str(ctx.author.id)]["Rest"]
    Lastaction_pull = players[str(ctx.author.id)]["Lastaction"]
    await ctx.send(f"{ctx.author}'s HP: {hp_pull} \nLocation: {location_pull} \nSC: {SC_pull} \nRage: {Rage_pull} \nInventory: \n    Ready: {ReadyInventory_pull} \n    Used:{UsedInventory_pull} \nDelay: <t:{DelayDate_pull}> ({Delay_pull})", ephemeral=True)

bot.start ()

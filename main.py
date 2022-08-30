import interactions
from interactions import Button, ButtonStyle, SelectMenu, SelectOption, ActionRow, spread_to_rows
import asyncio
from datetime import datetime
import time
import math
import json


crossroads = 1013916584642891898
dungeon = 1013916641177907242
farmland = 1013916731372216380
keep = 1013916770056278016
lichcastle = 1013916812695580693
shop = 1013916856333127690
tavern = 1013916898729140264
guildid= 1011380009010724924
poisonchannel= 1011701650798424185
bot = interactions.Client(token="MTAxMTM0OTI5NDQ5NTgzODMyOQ.Gvg2zG.tssIbqSl9rSMC2vii5FOY5FLtdG5yA1U5ze0bA", intents=interactions.Intents.DEFAULT | interactions.Intents.GUILD_MESSAGE_CONTENT)

#new poison
#poison to poison.json to keep it consistent between script reboots
@bot.event
async def on_ready():
    print(f"We're online! We've logged in as {bot.me.name}.")
    print(f"Our latency is {round(bot.latency)} ms.")
    current_time = int(time.time())
    print(f"Started at {current_time}")
    poison = await getpoisondata()
    channel = await interactions.get(bot, interactions.Channel, object_id=poisonchannel)
    if str("poisondate") in poison:
        #this case has tested successfully!
        print(f"poison date already exists!")
        with open("poison.json", "r") as h:
            poisondate_pull = poison["poisondate"]
            poisondamage_pull = poison["poisondamage"]
            poisontimer_pull = poison["poisontimer"]
        print (f"poison date pulled as {poisondate_pull}, poison timer pulled as {poisontimer_pull}, and poisondamage pulled as {poisondamage_pull}")
        if poisondate_pull < current_time :
            poisondamage_pull=poisondamage_pull+100
            poisontimer_pull=math.ceil(poisontimer_pull*.75)
            nextpoisontime=int(current_time+poisontimer_pull)
            print(f"{poisondamage_pull} poison damage at {nextpoisontime} and {poisontimer_pull} seconds till next poison")
            players = await getplayerdata ()
            print ("before")
            print (players)
            players = {key:{key2:value2-poisondamage_pull if key2=="HP" else value2 for (key2,value2) in value.items()} for (key,value) in players.items()}
            print ("after")
            print (players)
            with open("players.json","w") as f:
                json.dump(players,f, indent=4)
            await channel.send(f"Poison damage increased by 100, then dealt **{poisondamage_pull} damage** to everyone! \nThe time between poison damage decreases by 25%! \nThe next poison damage will occur on <t:{nextpoisontime}> (in {poisontimer_pull} seconds)." )
            poison["poisondate"] = nextpoisontime
            poison["poisondamage"] = poisondamage_pull
            poison["poisontimer"] = poisontimer_pull
            with open("poison.json","w") as h:
               json.dump(poison,h, indent=4)
        else:
            #this case has been tested successfully!
            await channel.send(f"I have awoken! \n (@-everyone to go here) \n The next poison comes <t:{poisondate_pull}> ({int(poisondate_pull-current_time)} seconds) to deal {int(poisondamage_pull+100)} damage.")
    else:
        #this case has tested successfully!
        smalltime=int(86400) #set to 86400 (seconds in a day) when golive and blank poison.json
        smalltimeunit="seconds" #set to days on golive
        firstcountdown=int(14*smalltime)
        nextpoisontime=current_time+firstcountdown
        poison = {}
        poison["poisondate"] = nextpoisontime
        poison["poisondamage"] = 0
        poison["poisontimer"] = smalltime
        with open("poison.json","w") as h:
            json.dump(poison,h, indent=4)
        await channel.send(f"Poison is coming in {int(firstcountdown/smalltime)} {smalltimeunit}. \nPoison will begin <t:{nextpoisontime}>.")
    poison = await getpoisondata()
    poisondate_pull = poison["poisondate"]
    poisondamage_pull = poison["poisondamage"]
    poisontimer_pull = poison["poisontimer"]
    await asyncio.sleep(int(poisondate_pull-current_time))
    while poisondamage_pull < 20000:
        #test successful!
        poisondamage_pull=poisondamage_pull+100
        poisontimer_pull=math.ceil(poisontimer_pull*.75)
        nextpoisontime=int(current_time+poisontimer_pull)
        print(f"{poisondamage_pull} poison damage at {nextpoisontime} and {poisontimer_pull} seconds till next poison")
        await channel.send(f"Poison damage increased by 100, then dealt **{poisondamage_pull} damage** to everyone! \nThe time between poison damage decreases by 25%! \nThe next poison damage will occur on <t:{nextpoisontime}> (in {poisontimer_pull} seconds)." )
        players = await getplayerdata ()
        print ("before")
        print (players)
        players = {key:{key2:value2-poisondamage_pull if key2=="HP" else value2 for (key2,value2) in value.items()} for (key,value) in players.items()}
        print ("after")
        print (players)
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
        poison["poisondate"] = nextpoisontime
        poison["poisondamage"] = poisondamage_pull
        poison["poisontimer"] = poisontimer_pull
        with open("poison.json","w") as h:
          json.dump(poison,h, indent=4)
        await asyncio.sleep(nextpoisontime-current_time)

@bot.event(name="on_message_create")
async def listen(message: interactions.Message):
    print(
        f"We've received a message from {message.author.username}. The message is: {message.content}."
    )
    #if interactions.ChannelType.DM == True :
    #    print ("3")
    #    channel = message.channel_id
    #    await channel.send("join the test environment! \n test")
    #else:
    #    pass

#pulls player.json into dict
async def getplayerdata():
    with open("players.json","r") as f:
        players = json.load(f)
    return players

#this pulls the bounty data into dict
async def getbountydata():
    with open("bounties.json","r") as g:
        bounties = json.load(g)
    return bounties

#pulls poison.json into dict
async def getpoisondata():
    with open("poison.json","r") as h:
        poison = json.load(h)
    return poison

#pulls location.json into dict:
async def getlocationdata():
    with open("locations.json","r") as i:
        locations = json.load(i)
    return locations

@bot.command(
    name="join",
    description="join the game!",
    scope=guildid,
)
async def join_command(ctx: interactions.CommandContext):
    players = await getplayerdata()
    bounties = await getbountydata()
    # need to add:
        # depends on adding poison to poison.json first:
    # check for poisondate (if join b4 poison, 10SC+bounty and 10000hp, otherwise min(SC)-1 and MIN(HP)-1)
    if str(ctx.author.id) in players:
        await ctx.send(f"Failed to Join! {ctx.author} already exists as a player! ", ephemeral = True)
        return False
    else:
        current_time = int(time.time())
        delaytimer=int(300)
        await ctx.author.add_role(crossroads, guildid)
        if str(ctx.author.id) in bounties:
            bounty_pull = bounties[str(ctx.author.id)]["Bounty"]
            await ctx.send(f"{ctx.author} has claimed prior bounties for {bounty_pull}!", ephemeral = True)
        else:
            bounty_pull = 0
            return
        players[str(ctx.author.id)] = {}
        players[str(ctx.author.id)]["Username"] = str(ctx.author.user)
        players[str(ctx.author.id)]["HP"] = 10000
        players[str(ctx.author.id)]["Location"] = "Crossroads"
        players[str(ctx.author.id)]["SC"] = 10 + bounty_pull
        players[str(ctx.author.id)]["Rage"] = 0
        players[str(ctx.author.id)]["ReadyInventory"] = ""
        players[str(ctx.author.id)]["UsedInventory"] = ""
        players[str(ctx.author.id)]["DelayDate"] = current_time
        players[str(ctx.author.id)]["Evade"] = False
        players[str(ctx.author.id)]["Rest"] = False
        players[str(ctx.author.id)]["Lastaction"] = "start"
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
        Evade_pull = players[str(ctx.author.id)]["Evade"]
        Rest_pull = players[str(ctx.author.id)]["Rest"]
        Lastaction_pull = players[str(ctx.author.id)]["Lastaction"]
        await ctx.send(f"{ctx.author}'s HP: {hp_pull} \nLocation: {location_pull} \nSC: {SC_pull} \nRage: {Rage_pull} \nInventory: \n    Ready: {ReadyInventory_pull} \n    Used:{UsedInventory_pull} \nCooldown: <t:{DelayDate_pull}>", ephemeral = True)

#light attack is below

@bot.command(
    name="lightattack",
    description="24h. attack a player in your area for 950.",
    scope = guildid ,
    options=[
        interactions.Option(
            type=interactions.OptionType.STRING,
            name="playertarget",
            description="who you want to attack",
            required=True,
            autocomplete=True,
        )
    ]
)
async def lightattack(ctx: interactions.CommandContext, playertarget: str):
    players = await getplayerdata()
    #Rage_pull=players[str(ctx.author.id)]["Rage"]
    current_time = int(time.time())
    print(f"{playertarget} is the player target")
    for k,v in players.items():
        if v['Username']==str(playertarget):
            playertargetid=k
    print(f"{playertargetid} is the player target id")
    if str(ctx.author.id) in players:
        DelayDate_pull = players[str(ctx.author.id)]["DelayDate"]
        if DelayDate_pull > current_time:
            await ctx.send(f"You cannot act yet! You are delayed until <t:{DelayDate_pull}>.", ephemeral = True) #golive
        else:
            if players[str(playertargetid)]["Evade"]:
                damage = 0
                targethp = players[str(playertargetid)]["HP"] - damage
                # targethpmoji = write code to convert hp to emojis?
                players[str(playertargetid)]["HP"] = targethp
                #players[str(ctx.author.id)]["Rage"] = players[str(ctx.author.id)]["Rage"] +200
                cooldown=86400 #seconds in a day
                players[str(ctx.author.id)]["DelayDate"] = current_time+cooldown
                DelayDate_pull=current_time+cooldown
                players[str(ctx.author.id)]["Lastaction"] = "lightattack"
                with open("players.json","w") as f:
                    json.dump(players,f, indent=4)
                await ctx.send(f"<@{playertargetid}> evaded a light attack from <@{ctx.author.id}>! \nNew HP: {targethp} ", ephemeral=False)
                await ctx.send(f"<@{ctx.author.id}> used a light attack on <@{playertargetid}>! \n<@{ctx.author.id}> is on cooldown until <t:{DelayDate_pull}>", ephemeral=False)
                await asyncio.sleep(cooldown)
                players[str(ctx.author.id)]["DelayDate"] = current_time
                with open("players.json","w") as f:
                    json.dump(players,f, indent=4)
                await ctx.send(f"<@{ctx.author.id}> Your cooldown is over and you are free to act!", ephemeral = True)
            else:
                damage = 950 #+ Rage_pull #+ damagebuff
                targethp = players[str(playertargetid)]["HP"] - damage
                # targethpmoji = write code to convert hp to emojis?
                players[str(playertargetid)]["HP"] = targethp
                #players[str(ctx.author.id)]["Rage"] = players[str(ctx.author.id)]["Rage"] +200
                cooldown=86400 #seconds in a day
                players[str(ctx.author.id)]["DelayDate"] = current_time+cooldown
                DelayDate_pull=current_time+cooldown
                players[str(ctx.author.id)]["Lastaction"] = "lightattack"
                with open("players.json","w") as f:
                    json.dump(players,f, indent=4)
                await ctx.send(f"<@{playertargetid}> was hit by a light attack by <@{ctx.author.id}>! \nNew HP: {targethp} ", ephemeral=False)
                await ctx.send(f"<@{ctx.author.id}> used a light attack on <@{playertargetid}>! \n<@{ctx.author.id}> is on cooldown until <t:{DelayDate_pull}>", ephemeral=False)
                await asyncio.sleep(cooldown)
                players[str(ctx.author.id)]["DelayDate"] = current_time
                with open("players.json","w") as f:
                    json.dump(players,f, indent=4)
                await ctx.send(f"<@{ctx.author.id}> Your cooldown is over and you are free to act!", ephemeral = True)
    else:
        await ctx.send(f"You need to join with /join before you can do that!" , ephemeral = True)


@bot.autocomplete("lightattack", "playertarget")
async def light_autocomplete(ctx: interactions.CommandContext, value: str = ""):
    players = await getplayerdata()
    LocationPull = players[str(ctx.author.id)]["Location"]
    sameLocationUserIDs = {k: v for k, v in players.items() if v['Location'] == LocationPull}
    sameLocationUsernames = [v["Username"] for v in players.values() if v['Location'] == LocationPull]
    print (LocationPull)
    print (sameLocationUsernames)
    items = sameLocationUsernames
    choices = [
        interactions.Choice(name=item, value=item) for item in items if value in item
    ]
    await ctx.populate(choices)

#normal attack is below

@bot.command(
    name="normalattack",
    description="48h. attack a player in your area for 2300.",
    scope = guildid ,
    options=[
        interactions.Option(
            type=interactions.OptionType.STRING,
            name="playertarget",
            description="who you want to attack",
            required=True,
            autocomplete=True,
        )
    ]
)
async def normalattack(ctx: interactions.CommandContext, playertarget: str):
    players = await getplayerdata()
    #Rage_pull=players[str(ctx.author.id)]["Rage"]
    current_time = int(time.time())
    print(f"{playertarget} is the player target")
    for k,v in players.items():
        if v['Username']==str(playertarget):
            playertargetid=k
    print(f"{playertargetid} is the player target id")
    if str(ctx.author.id) in players:
        DelayDate_pull = players[str(ctx.author.id)]["DelayDate"]
        if DelayDate_pull > current_time:
            await ctx.send(f"You cannot act yet! You are delayed until <t:{DelayDate_pull}>.", ephemeral = True) #golive
        else:
            if players[str(playertargetid)]["Evade"]:
                damage = 0
                targethp = players[str(playertargetid)]["HP"] - damage
                # targethpmoji = write code to convert hp to emojis?
                players[str(playertargetid)]["HP"] = targethp
                #players[str(ctx.author.id)]["Rage"] = players[str(ctx.author.id)]["Rage"] +200
                cooldown=86400*2 #seconds in two days
                players[str(ctx.author.id)]["DelayDate"] = current_time+cooldown
                DelayDate_pull=current_time+cooldown
                players[str(ctx.author.id)]["Lastaction"] = "lightattack"
                with open("players.json","w") as f:
                    json.dump(players,f, indent=4)
                await ctx.send(f"<@{playertargetid}> evaded a normal attack from <@{ctx.author.id}>! \nNew HP: {targethp} ", ephemeral=False)
                await ctx.send(f"<@{ctx.author.id}> used a normal attack on <@{playertargetid}>! \n<@{ctx.author.id}> is on cooldown until <t:{DelayDate_pull}>", ephemeral=False)
                await asyncio.sleep(cooldown)
                players[str(ctx.author.id)]["DelayDate"] = current_time
                with open("players.json","w") as f:
                    json.dump(players,f, indent=4)
                await ctx.send(f"<@{ctx.author.id}> Your cooldown is over and you are free to act!", ephemeral = True)
            else:
                damage = 2300 #+ Rage_pull #+ damagebuff
                targethp = players[str(playertargetid)]["HP"] - damage
                # targethpmoji = write code to convert hp to emojis?
                players[str(playertargetid)]["HP"] = targethp
                #players[str(ctx.author.id)]["Rage"] = players[str(ctx.author.id)]["Rage"] +200
                cooldown=86400*2 #seconds in two days
                players[str(ctx.author.id)]["DelayDate"] = current_time+cooldown
                DelayDate_pull=current_time+cooldown
                players[str(ctx.author.id)]["Lastaction"] = "normalattack"
                with open("players.json","w") as f:
                    json.dump(players,f, indent=4)
                await ctx.send(f"<@{playertargetid}> was hit by a normal attack by <@{ctx.author.id}>! \nNew HP: {targethp} ", ephemeral=False)
                await ctx.send(f"<@{ctx.author.id}> used a normal attack on <@{playertargetid}>! \n<@{ctx.author.id}> is on cooldown until <t:{DelayDate_pull}>", ephemeral=False)
                await asyncio.sleep(cooldown)
                players[str(ctx.author.id)]["DelayDate"] = current_time
                with open("players.json","w") as f:
                    json.dump(players,f, indent=4)
                await ctx.send(f"<@{ctx.author.id}> Your cooldown is over and you are free to act!", ephemeral = True)
    else:
        await ctx.send(f"You need to join with /join before you can do that!" , ephemeral = True)


@bot.autocomplete("normalattack", "playertarget")
async def normal_autocomplete(ctx: interactions.CommandContext, value: str = ""):
    players = await getplayerdata()
    LocationPull = players[str(ctx.author.id)]["Location"]
    sameLocationUserIDs = {k: v for k, v in players.items() if v['Location'] == LocationPull}
    sameLocationUsernames = [v["Username"] for v in players.values() if v['Location'] == LocationPull]
    print (LocationPull)
    print (sameLocationUsernames)
    items = sameLocationUsernames
    choices = [
        interactions.Choice(name=item, value=item) for item in items if value in item
    ]
    await ctx.populate(choices)

#heavy attack is below

@bot.command(
    name="heavyattack",
    description="72h. attack a player in your area for 3650.",
    scope = guildid ,
    options=[
        interactions.Option(
            type=interactions.OptionType.STRING,
            name="playertarget",
            description="who you want to attack",
            required=True,
            autocomplete=True,
        )
    ]
)
async def heavyattack(ctx: interactions.CommandContext, playertarget: str):
    players = await getplayerdata()
    #Rage_pull=players[str(ctx.author.id)]["Rage"]
    current_time = int(time.time())
    print(f"{playertarget} is the player target")
    for k,v in players.items():
        if v['Username']==str(playertarget):
            playertargetid=k
    print(f"{playertargetid} is the player target id")
    if str(ctx.author.id) in players:
        DelayDate_pull = players[str(ctx.author.id)]["DelayDate"]
        if DelayDate_pull > current_time:
            await ctx.send(f"You cannot act yet! You are delayed until <t:{DelayDate_pull}>.", ephemeral = True) #golive
        else:
            if players[str(playertargetid)]["Evade"]:
                damage = 0
                targethp = players[str(playertargetid)]["HP"] - damage
                # targethpmoji = write code to convert hp to emojis?
                players[str(playertargetid)]["HP"] = targethp
                #players[str(ctx.author.id)]["Rage"] = players[str(ctx.author.id)]["Rage"] +200
                cooldown=86400*3 #seconds in three days
                players[str(ctx.author.id)]["DelayDate"] = current_time+cooldown
                DelayDate_pull=current_time+cooldown
                players[str(ctx.author.id)]["Lastaction"] = "heavyattack"
                with open("players.json","w") as f:
                    json.dump(players,f, indent=4)
                await ctx.send(f"<@{playertargetid}> evaded a heavy attack from <@{ctx.author.id}>! \nNew HP: {targethp} ", ephemeral=False)
                await ctx.send(f"<@{ctx.author.id}> used a heavy attack on <@{playertargetid}>! \n<@{ctx.author.id}> is on cooldown until <t:{DelayDate_pull}>", ephemeral=False)
                await asyncio.sleep(cooldown)
                players[str(ctx.author.id)]["DelayDate"] = current_time
                with open("players.json","w") as f:
                    json.dump(players,f, indent=4)
                await ctx.send(f"<@{ctx.author.id}> Your cooldown is over and you are free to act!", ephemeral = True)
            else:
                damage = 3650 #+ Rage_pull #+ damagebuff
                targethp = players[str(playertargetid)]["HP"] - damage
                # targethpmoji = write code to convert hp to emojis?
                players[str(playertargetid)]["HP"] = targethp
                #players[str(ctx.author.id)]["Rage"] = players[str(ctx.author.id)]["Rage"] +200
                cooldown=86400*3 #seconds in three days
                players[str(ctx.author.id)]["DelayDate"] = current_time+cooldown
                DelayDate_pull=current_time+cooldown
                players[str(ctx.author.id)]["Lastaction"] = "heavyattack"
                with open("players.json","w") as f:
                    json.dump(players,f, indent=4)
                await ctx.send(f"<@{playertargetid}> was hit by a heavy attack by <@{ctx.author.id}>! \nNew HP: {targethp} ", ephemeral=False)
                await ctx.send(f"<@{ctx.author.id}> used a heavy attack on <@{playertargetid}>! \n<@{ctx.author.id}> is on cooldown until <t:{DelayDate_pull}>", ephemeral=False)
                await asyncio.sleep(cooldown)
                players[str(ctx.author.id)]["DelayDate"] = current_time
                with open("players.json","w") as f:
                    json.dump(players,f, indent=4)
                await ctx.send(f"<@{ctx.author.id}> Your cooldown is over and you are free to act!", ephemeral = True)
    else:
        await ctx.send(f"You need to join with /join before you can do that!" , ephemeral = True)


@bot.autocomplete("heavyattack", "playertarget")
async def heavy_autocomplete(ctx: interactions.CommandContext, value: str = ""):
    players = await getplayerdata()
    LocationPull = players[str(ctx.author.id)]["Location"]
    sameLocationUserIDs = {k: v for k, v in players.items() if v['Location'] == LocationPull}
    sameLocationUsernames = [v["Username"] for v in players.values() if v['Location'] == LocationPull]
    print (LocationPull)
    print (sameLocationUsernames)
    items = sameLocationUsernames
    choices = [
        interactions.Choice(name=item, value=item) for item in items if value in item
    ]
    await ctx.populate(choices)

#interruptis below

@bot.command(
    name="interrupt",
    description="24h. hit a player in your area for 4200 if they are resting or evading.",
    scope = guildid ,
    options=[
        interactions.Option(
            type=interactions.OptionType.STRING,
            name="playertarget",
            description="who you want to interrupt",
            required=True,
            autocomplete=True,
        )
    ]
)
async def interrupt(ctx: interactions.CommandContext, playertarget: str):
    players = await getplayerdata()
    #Rage_pull=players[str(ctx.author.id)]["Rage"]
    current_time = int(time.time())
    print(f"{playertarget} is the player target")
    for k,v in players.items():
        if v['Username']==str(playertarget):
            playertargetid=k
    print(f"{playertargetid} is the player target id")
    if str(ctx.author.id) in players:
        DelayDate_pull = players[str(ctx.author.id)]["DelayDate"]
        if DelayDate_pull > current_time:
            await ctx.send(f"You cannot act yet! You are delayed until <t:{DelayDate_pull}>.", ephemeral = True) #golive
        else:
            print (players[str(playertargetid)]["Evade"])
            print (players[str(playertargetid)]["Rest"])
            if players[str(playertargetid)]["Evade"] or players[str(playertargetid)]["Rest"] :
                targethp = players[str(playertargetid)]["HP"] - 4200
                players[str(playertargetid)]["HP"] = targethp
                #players[str(ctx.author.id)]["Rage"] = players[str(ctx.author.id)]["Rage"] +200
                cooldown=86400*1 #seconds in one day
                players[str(ctx.author.id)]["DelayDate"] = current_time+cooldown
                DelayDate_pull=current_time+cooldown
                players[str(ctx.author.id)]["Lastaction"] = "interrupt"
                with open("players.json","w") as f:
                    json.dump(players,f, indent=4)
                await ctx.send(f"<@{playertargetid}> was hit and damaged by an interrupt by <@{ctx.author.id}>! \nNew HP: {targethp} ", ephemeral=False)
                await ctx.send(f"<@{ctx.author.id}> used an interrupt on <@{playertargetid}>! \n<@{ctx.author.id}> is on cooldown until <t:{DelayDate_pull}>", ephemeral=False)
                await asyncio.sleep(cooldown)
                players[str(ctx.author.id)]["DelayDate"] = current_time
                with open("players.json","w") as f:
                    json.dump(players,f, indent=4)
                await ctx.send(f"<@{ctx.author.id}> Your cooldown is over and you are free to act!", ephemeral = True)
            else:
                #players[str(ctx.author.id)]["Rage"] = players[str(ctx.author.id)]["Rage"] +200
                cooldown=86400*1 #seconds in one day
                players[str(ctx.author.id)]["DelayDate"] = current_time+cooldown
                DelayDate_pull=current_time+cooldown
                players[str(ctx.author.id)]["Lastaction"] = "interrupt"
                with open("players.json","w") as f:
                    json.dump(players,f, indent=4)
                await ctx.send(f"<@{playertargetid}> was not damaged by an interrupt from <@{ctx.author.id}>! \nNew HP: {targethp} ", ephemeral=False)
                await ctx.send(f"<@{ctx.author.id}> used an interrupt on <@{playertargetid}> for zero damage! \n<@{ctx.author.id}> is on cooldown until <t:{DelayDate_pull}>", ephemeral=False)
                await asyncio.sleep(cooldown)
                players[str(ctx.author.id)]["DelayDate"] = current_time
                with open("players.json","w") as f:
                    json.dump(players,f, indent=4)
                await ctx.send(f"<@{ctx.author.id}> Your cooldown is over and you are free to act!", ephemeral = True)
    else:
        await ctx.send(f"You need to join with /join before you can do that!" , ephemeral = True)


@bot.autocomplete("interrupt", "playertarget")
async def interrupt_autocomplete(ctx: interactions.CommandContext, value: str = ""):
    players = await getplayerdata()
    LocationPull = players[str(ctx.author.id)]["Location"]
    sameLocationUserIDs = {k: v for k, v in players.items() if v['Location'] == LocationPull}
    sameLocationUsernames = [v["Username"] for v in players.values() if v['Location'] == LocationPull]
    print (LocationPull)
    print (sameLocationUsernames)
    items = sameLocationUsernames
    choices = [
        interactions.Choice(name=item, value=item) for item in items if value in item
    ]
    await ctx.populate(choices)

#evade is below

@bot.command(
    name="evade",
    description="48h. receive no damage from light normal or heavy attacks",
    scope=guildid,
)
async def evade_command(ctx: interactions.CommandContext):
    players = await getplayerdata()
    if str(ctx.author.id) in players:
        DelayDate_pull = players[str(ctx.author.id)]["DelayDate"]
        current_time = int(time.time())
        if DelayDate_pull > current_time:
            await ctx.send(f"You cannot act yet! You are delayed until <t:{DelayDate_pull}>.", ephemeral = True)
        else:
            players[str(ctx.author.id)]["Evade"] = True
            cooldown=int(86400*2) #seconds in two days
            current_time = int(time.time())
            players[str(ctx.author.id)]["DelayDate"] = current_time + cooldown
            DelayDate_pull = players[str(ctx.author.id)]["DelayDate"]
            with open("players.json","w") as f:
                json.dump(players,f, indent=4)
            await ctx.send(f"<@{ctx.author.id}> used evade! \n<@{ctx.author.id}> is on cooldown until <t:{DelayDate_pull}>", ephemeral=False)
            await asyncio.sleep(cooldown) #sleep
            players[str(ctx.author.id)]["DelayDate"] = current_time
            with open("players.json","w") as f:
                json.dump(players,f, indent=4)
            await ctx.send(f"<@{ctx.author.id}> Your cooldown is over and you are free to act!", ephemeral = True)
    else:
        await ctx.send(f"You need to join with /join before you can do that!" , ephemeral = True)

#rest is below

@bot.command(
    name="rest",
    description="48h. heal half your missing health rounded up",
    scope=guildid,
)
async def rest_command(ctx: interactions.CommandContext):
    players = await getplayerdata()
    if str(ctx.author.id) in players:
        DelayDate_pull = players[str(ctx.author.id)]["DelayDate"]
        current_time = int(time.time())
        if DelayDate_pull > current_time:
            await ctx.send(f"You cannot act yet! You are delayed until <t:{DelayDate_pull}>.", ephemeral = True)
        else:
            players[str(ctx.author.id)]["Rest"] = True
            hp_pull = players[str(ctx.author.id)]["HP"]
            heal = math.ceil(int(10000 - hp_pull))
            cooldown=int(86400*2) #seconds in two days
            current_time = int(time.time())
            players[str(ctx.author.id)]["DelayDate"] = current_time + cooldown
            DelayDate_pull = players[str(ctx.author.id)]["DelayDate"]
            with open("players.json","w") as f:
                json.dump(players,f, indent=4)
            await ctx.send(f"<@{ctx.author.id}> used rest! \n<@{ctx.author.id}> is on cooldown until <t:{DelayDate_pull}>", ephemeral=False)
            await asyncio.sleep(cooldown) #sleep
            players[str(ctx.author.id)]["DelayDate"] = current_time
            with open("players.json","w") as f:
                json.dump(players,f, indent=4)
            await ctx.send(f"<@{ctx.author.id}> Your cooldown is over and you are free to act!", ephemeral = True)
    else:
        await ctx.send(f"You need to join with /join before you can do that!" , ephemeral = True)

#travelfrom

@bot.command(
    name="travelfrom",
    description="24h. travel from the crossroads to any location.",
    scope = guildid ,
    options=[
        interactions.Option(
            type=interactions.OptionType.STRING,
            name="destination",
            description="where to travel to",
            required=True,
            autocomplete=True,
        )
    ]
)
async def travelfrom(ctx: interactions.CommandContext, destination: str):
    locations = await getlocationdata()
    players = await getplayerdata()
    #Rage_pull=players[str(ctx.author.id)]["Rage"]
    current_time = int(time.time())
    print(f"{destination} is the destination")
    for k,v in locations.items():
        if v['Name']==str(destination):
            destinationid=k
    print(f"{destinationid} is the player destination id")
    if str(ctx.author.id) in players:
        DelayDate_pull = players[str(ctx.author.id)]["DelayDate"]
        if DelayDate_pull > current_time:
            await ctx.send(f"You cannot act yet! You are delayed until <t:{DelayDate_pull}>.", ephemeral = True) #golive
        else:
            cooldown=86400*1 #seconds in one day
            players[str(ctx.author.id)]["DelayDate"] = current_time+cooldown
            DelayDate_pull=current_time+cooldown
            players[str(ctx.author.id)]["Lastaction"] = "travelfrom"
            players[str(ctx.author.id)]["Location"] = destination
            with open("players.json","w") as f:
                json.dump(players,f, indent=4)
            await ctx.author.remove_role(crossroads, guildid)
            await ctx.author.add_role(destinationid, guildid)
            await ctx.send(f"<@{ctx.author.id}> traveled to {destination}! \n<@{ctx.author.id}> is on cooldown until <t:{DelayDate_pull}>", ephemeral=False)
            await asyncio.sleep(cooldown)
            players[str(ctx.author.id)]["DelayDate"] = current_time
            with open("players.json","w") as f:
                json.dump(players,f, indent=4)
            await ctx.send(f"<@{ctx.author.id}> Your cooldown is over and you are free to act!", ephemeral = True)
    else:
        await ctx.send(f"You need to join with /join before you can do that!" , ephemeral = True)


@bot.autocomplete("travelfrom", "destination")
async def travelfrom_autocomplete(ctx: interactions.CommandContext, value: str = ""):
    players = await getplayerdata()
    locations = await getlocationdata()
    sameLocationUsernames = [v["Name"] for v in locations.values()]
    print (sameLocationUsernames)
    items = sameLocationUsernames
    choices = [
        interactions.Choice(name=item, value=item) for item in items if value in item
    ]
    await ctx.populate(choices)

#travelto

@bot.command(
    name="traveltocrossroads",
    description="24h. travel to the crossroads from any location.",
    scope = guildid ,
)
async def traveltocrossroads(ctx: interactions.CommandContext):
    locations = await getlocationdata()
    players = await getplayerdata()
    #Rage_pull=players[str(ctx.author.id)]["Rage"]
    current_time = int(time.time())
    if str(ctx.author.id) in players:
        DelayDate_pull = players[str(ctx.author.id)]["DelayDate"]
        if DelayDate_pull > current_time:
            await ctx.send(f"You cannot act yet! You are delayed until <t:{DelayDate_pull}>.", ephemeral = True) #golive
        else:
            cooldown=86400*1 #seconds in one day
            players[str(ctx.author.id)]["DelayDate"] = current_time+cooldown
            DelayDate_pull=current_time+cooldown
            players[str(ctx.author.id)]["Lastaction"] = "travelto"
            players[str(ctx.author.id)]["Location"] = "Crossroads"
            with open("players.json","w") as f:
                json.dump(players,f, indent=4)
            await ctx.author.remove_role(dungeon, guildid)
            await ctx.author.remove_role(farmland, guildid)
            await ctx.author.remove_role(keep, guildid)
            await ctx.author.remove_role(lichcastle, guildid)
            await ctx.author.remove_role(shop, guildid)
            await ctx.author.remove_role(tavern, guildid)
            await ctx.author.add_role(crossroads, guildid)
            await ctx.send(f"<@{ctx.author.id}> traveled to {destination}! \n<@{ctx.author.id}> is on cooldown until <t:{DelayDate_pull}>", ephemeral=False)
            await asyncio.sleep(cooldown)
            players[str(ctx.author.id)]["DelayDate"] = current_time
            with open("players.json","w") as f:
                json.dump(players,f, indent=4)
            await ctx.send(f"<@{ctx.author.id}> Your cooldown is over and you are free to act!", ephemeral = True)
    else:
        await ctx.send(f"You need to join with /join before you can do that!" , ephemeral = True)

bot.start ()

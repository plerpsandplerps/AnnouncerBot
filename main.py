import interactions
from interactions import Button, ButtonStyle, SelectMenu, SelectOption, ActionRow, spread_to_rows
import asyncio
import random
from datetime import datetime
import random
import time
import math
import json

#RoleIDs to replace with your server's roleids
crossroads = 1013916584642891898
dungeon = 1013916641177907242
farmland = 1013916731372216380
keep = 1013916770056278016
lichcastle = 1013916812695580693
shop = 1013916856333127690
tavern = 1013916898729140264
dead = 1014618473948786690
playing = 1015250670988828734

#general channel id
general = 1011380009568587878

#ServerID to replace with the serverID
guildid= 1011380009010724924

#Replace with the channel_id where you would like to send your poison pings
poisonchannel= 1011701650798424185

#Place your token here:
with open('.gitignore/config.json', 'r') as cfg:
  # Deserialize the JSON data (essentially turning it into a Python dictionary object so we can use it in our code)
  tokens = json.load(cfg)

bot = interactions.Client(token=tokens["token"], intents=interactions.Intents.DEFAULT | interactions.Intents.GUILD_MESSAGE_CONTENT)

#new poison
#poison to poison.json to keep it consistent between script reboots
@bot.event
async def on_ready():
    print(f"We're online! We've logged in as {bot.me.name}.")
    print(f"Our latency is {round(bot.latency)} ms.")
    current_time = int(time.time())
    loop = asyncio.get_running_loop()
    loop.create_task(pollfornext())
    print(f"Started at {current_time}")
    poison = await getpoisondata()
    channel = await interactions.get(bot, interactions.Channel, object_id=poisonchannel)
    if str("poisondate") in poison:
        print(f"poison date already exists!")
        with open("poison.json", "r") as h:
            poisondate_pull = poison["poisondate"]
            poisondamage_pull = poison["poisondamage"]
            poisontimer_pull = poison["poisontimer"]
        print (f"poison date pulled as {poisondate_pull}, poison timer pulled as {poisontimer_pull}, and poisondamage pulled as {poisondamage_pull}")
        if poisondate_pull < current_time :
            poisontimer_pull=max(math.ceil(poisontimer_pull*.9),86400)
            nextpoisontime=int(current_time+poisontimer_pull)
            print(f"{poisondamage_pull} poison damage at {nextpoisontime} and {poisontimer_pull} days till next poison")
            players = await getplayerdata ()
            print ("before")
            print (players)
            players = {key:{key2:value2-poisondamage_pull if key2=="HP" else value2 for (key2,value2) in value.items()} for (key,value) in players.items()}
            print ("after")
            print (players)
            with open("players.json","w") as f:
                json.dump(players,f, indent=4)
            await channel.send(f"Poison damage increased by 100 then dealt **{poisondamage_pull} damage** to everyone! \nThe time between poison damage decreases by 10%! \nThe next poison damage will occur on <t:{nextpoisontime}> (in {poisontimer_pull} seconds) to deal {min(poisondamage_pull +100, 1500)} damage." )
            poison["poisondate"] = nextpoisontime
            poison["poisondamage"] = poisondamage_pull
            poison["poisontimer"] = poisontimer_pull
            with open("poison.json","w") as h:
               json.dump(poison,h, indent=4)
        else:
            await channel.send(f"I have awoken! \n (@-everyone to go here) \n The next poison comes <t:{poisondate_pull}> ({int(poisondate_pull-current_time)} seconds) to deal {int(poisondamage_pull+100)} damage.")
    else:
        smalltime=int(86400) #set to 86400 (seconds in a day) when golive and blank poison.json
        smalltimeunit="days" #set to days on golive
        firstcountdown=int(7*smalltime)
        nextpoisontime=current_time+firstcountdown
        poison = {}
        poison["poisondate"] = nextpoisontime
        poison["poisondamage"] = 650
        poison["poisontimer"] = firstcountdown
        poisondamage_pull = poison["poisondamage"]
        poisontimer_pull = firstcountdown
        with open("poison.json","w") as h:
            json.dump(poison,h, indent=4)
        poison = await getpoisondata()
        poisondate_pull = poison["poisondate"]
        poisondamage_pull = poison["poisondamage"]
        poisontimer_pull = poison["poisontimer"]
        await channel.send(f"The first poison damage will occur on <t:{nextpoisontime}> (in {poisontimer_pull} seconds) to deal {min(poisondamage_pull +100, 1500)} damage." )
    await asyncio.sleep(int(poisondate_pull-current_time))
    while poisondamage_pull < 500000:
        #test successful!
        poisondamage_pull= min(poison["poisondamage"] +100, 1500)
        poisontimer_pull=max(math.ceil(poisontimer_pull*.9),86400)
        nextpoisontime=int(current_time+poisontimer_pull)
        print(f"{poisondamage_pull} poison damage at {nextpoisontime} and {poisontimer_pull} seconds till next poison")
        await channel.send(f"Poison damage increased by 100 then dealt **{poisondamage_pull} damage** to everyone! \nThe time between poison damage decreases by 10%! \nThe next poison damage will occur on <t:{nextpoisontime}> (in {poisontimer_pull} seconds) to deal {min(poisondamage_pull +100, 1500)} damage." )
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

async def gettaverndata():
    with open("tavern.json","r") as j:
        scores = json.load(j)
    return scores

async def pollfornext():
    #run forever
    while True:
        print('hi')
        players = await getplayerdata()
        locations = await getlocationdata()
        for k,v in players.items():
            if v['Nextaction'] != "":
                words = players[k]['Nextaction'].split()
                if v['DelayDate'] < int(time.time()):
                    #do the action
                    loop = asyncio.get_running_loop()
                    if len(words) == 1:
                        loop.create_task(functiondict[words[0]](**{'authorid': k}))
                        print(f"{v['Username']} is doing {words[0]}")
                    elif words[1] in players:
                        loop.create_task(functiondict[words[0]]( **{'authorid':k,'targetid':words[1],'channelid':general}))
                        print(f"{v['Username']} is doing {words[0]} {players[words[1]]['Username']}")
                    elif words[1] in locations:
                        loop.create_task(functiondict[words[0]]( **{'authorid':k,'targetid':words[1],'channelid':general}))
                        print(f"{v['Username']} is doing {words[0]} {locations[words[1]]['Name']}")
                    players[k]['Nextaction'] = ""
                    with open("players.json", "w") as f:
                        json.dump(players, f, indent=4)
                else:
                    if len(words) == 1:
                        print(f"{v['Username']} is not ready to {words[0]}")
                    elif words[1] in players:
                        print(f"{v['Username']} is not ready to {words[0]} {players[words[1]]['Username']}")
                    elif words[1] in locations:
                        print(f"{v['Username']} is not ready to {words[0]} {locations[words[1]]['Name']}")
        await asyncio.sleep(10)

async def send_message(message : str, **kwargs):
    if('user_id' in kwargs.keys()):
        for targetid in kwargs['user_id']:
            user = await interactions.get(bot, interactions.Member, object_id=targetid, guild_id=guildid, force='http')
            await user.send(message)
    if ('channel_id' in kwargs.keys()):
        for targetid in kwargs['channel_id']:
            channel = await interactions.get(bot, interactions.Channel, object_id=targetid, guild_id=guildid, force='http')
            await channel.send(message)

async def queuenext(ctx):
    players = await getplayerdata()
    locations = await getlocationdata()
    #separate strings for printing to player and what we use (id)
    saveaction = f"{ctx.data.name}"
    displayaction = f"{ctx.data.name}"
    if players[ctx.author.id]["Nextaction"] != "":
        words = players[ctx.author.id]['Nextaction'].split()
        if len(words) == 1:
            await ctx.send(f"You already have a queued action: {words[0]}\nThis will be replaced by Next action: {displayaction}")
        elif words[1] in players:
            await ctx.send(f"You already have a queued action: {words[0]} {players[words[1]]['Username']}\nThis will be replaced by Next action: {displayaction}")
        elif words[1] in locations:
            await ctx.send(f"You already have a queued action: {words[0]} {locations[words[1]]['Name']}\nThis will be replaced by Next action: {displayaction}")
    else:
        await ctx.send(f"Next action: {displayaction}")

    #write and dump the new playerdata
    #TODO combine this dump with into a single dump with the caller functions somehow
    players[ctx.author.id]["Nextaction"]=saveaction
    with open("players.json", "w") as f:
        json.dump(players, f, indent=4)

    return

async def queuenexttarget(ctx, actiontargetid):
    players = await getplayerdata()
    locations = await getlocationdata()
    #separate strings for printing to player and what we use (id)
    saveaction = f"{ctx.data.name} {actiontargetid}"
    displayaction = ""
    if actiontargetid in players:
        displayaction = f"{ctx.data.name} {players[actiontargetid]['Username']}"
    elif actiontargetid in locations:
        displayaction = f"{ctx.data.name} {locations[actiontargetid]['Name']}"
    else:
        #TODO make this more specific
        raise Exception()
    if players[ctx.author.id]["Nextaction"] != "":
        words = players[ctx.author.id]['Nextaction'].split()
        if len(words) == 1:
            await ctx.send(f"You already have a queued action: {words[0]} \nThis will be replaced by Next action: {displayaction}", ephemeral=True)
        else:
            await ctx.send(f"You already have a queued action: {words[0]} {players[words[1]]['Username']}\nThis will be replaced by Next action: {displayaction}", ephemeral = True)
    else:
        await ctx.send(f"Next action: {displayaction}", ephemeral = True)

    #write and dump the new playerdata
    #TODO combine this dump with into a single dump with the caller functions somehow
    players[ctx.author.id]["Nextaction"]=saveaction
    with open("players.json", "w") as f:
        json.dump(players, f, indent=4)

    return

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
        await ctx.author.add_role(playing, guildid)
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
        players[str(ctx.author.id)]["Nextaction"] = ""
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
async def dolightattack(authorid,targetid,channelid):
    players = await getplayerdata()
    current_time = int(time.time())
    if players[str(targetid)]["Evade"]:
        damage = 0
        targethp = players[str(targetid)]["HP"] - damage
        # targethpmoji = write code to convert hp to emojis?
        players[str(targetid)]["HP"] = targethp
        players[str(authorid)]["HP"] = max(players[str(authorid)]["HP"] + ((players[str(authorid)]["Rage"])*420),10000)
        players[str(authorid)]["Rage"] = min(players[str(authorid)]["Rage"] -1,0)
        players[str(authorid)]["Rage"] = players[str(authorid)]["Rage"] +1
        cooldown = 86400  # seconds in a day
        players[str(authorid)]["DelayDate"] = current_time + cooldown
        DelayDate_pull = current_time + cooldown
        players[str(authorid)]["Lastaction"] = "lightattack"
        players[str(authorid)]["Evade"] = False
        players[str(authorid)]["Rest"] = False
        with open("players.json", "w") as f:
            json.dump(players, f, indent=4)
        await send_message(f"<@{targetid}> evaded a light attack from <@{authorid}>! \nNew HP: {targethp} ", user_id=[authorid,targetid])
        await send_message(f"<@{authorid}> used a light attack on <@{targetid}>! \n<@{authorid}> is on cooldown until <t:{DelayDate_pull}>", channel_id=[channelid])
    else:
        UsedInventory_pull = players[str(authorid)]["UsedInventory"]
        damage = 950 + (UsedInventory_pull.count("drinkingchallengemedal") * 420)
        targethp = players[str(targetid)]["HP"] - damage
        # targethpmoji = write code to convert hp to emojis?
        players[str(targetid)]["HP"] = targethp
        players[str(authorid)]["HP"] = max(players[str(authorid)]["HP"] + ((players[str(authorid)]["Rage"])*420),10000)
        players[str(authorid)]["Rage"] = min(players[str(authorid)]["Rage"] -1,0)
        players[str(authorid)]["Rage"] = players[str(authorid)]["Rage"] +1
        cooldown = 86400  # seconds in a day
        players[str(authorid)]["DelayDate"] = current_time + cooldown
        DelayDate_pull = current_time + cooldown
        players[str(authorid)]["Lastaction"] = "lightattack"
        players[str(authorid)]["Evade"] = False
        players[str(authorid)]["Rest"] = False
        with open("players.json", "w") as f:
            json.dump(players, f, indent=4)
        await send_message(f"<@{targetid}> was hit by a light attack by <@{authorid}>! \nNew HP: {targethp} ", user_id=[authorid,targetid])
        await send_message( f"<@{authorid}> used a light attack on <@{targetid}>! \n<@{authorid}> is on cooldown until <t:{DelayDate_pull}>", channel_id=[channelid])

@bot.command(
    name="lightattack",
    description="24h.1rage. attack a player in your area for 950.",
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
    current_time = int(time.time())
    print(f"{playertarget} is the player target")
    for k,v in players.items():
        if v['Username']==str(playertarget):
            targetid=k
    print(f"{targetid} is the player target id")
    if str(ctx.author.id) in players:
        DelayDate_pull = players[str(ctx.author.id)]["DelayDate"]
        if DelayDate_pull > current_time:
            await queuenexttarget(ctx,targetid,)
            await ctx.send(f"You cannot act yet! You are delayed until <t:{DelayDate_pull}>.", ephemeral = True) #golive
        else:
            await dolightattack(ctx.author.id,targetid,general)
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
async def donormalattack(authorid,targetid,channelid):
    players = await getplayerdata()
    current_time = int(time.time())
    if players[str(targetid)]["Evade"]:
        damage = 0
        targethp = players[str(targetid)]["HP"] - damage
        # targethpmoji = write code to convert hp to emojis?
        players[str(targetid)]["HP"] = targethp
        players[str(authorid)]["HP"] = max(players[str(authorid)]["HP"] + ((players[str(authorid)]["Rage"])*420),10000)
        players[str(authorid)]["Rage"] = min(players[str(authorid)]["Rage"] -1,0)
        players[str(authorid)]["Rage"] = players[str(authorid)]["Rage"] +3
        cooldown = 86400  # seconds in a day
        players[str(authorid)]["DelayDate"] = current_time + cooldown
        DelayDate_pull = current_time + cooldown
        players[str(authorid)]["Lastaction"] = "normalattack"
        players[str(authorid)]["Evade"] = False
        players[str(authorid)]["Rest"] = False
        with open("players.json", "w") as f:
            json.dump(players, f, indent=4)
        await send_message(f"<@{targetid}> evaded a normal attack from <@{authorid}>! \nNew HP: {targethp} ", user_id=[authorid,targetid])
        await send_message(f"<@{authorid}> used a normal attack on <@{targetid}>! \n<@{authorid}> is on cooldown until <t:{DelayDate_pull}>", channel_id=[channelid])
    else:
        UsedInventory_pull = players[str(authorid)]["UsedInventory"]
        damage = 950 + (UsedInventory_pull.count("drinkingchallengemedal") * 420)
        targethp = players[str(targetid)]["HP"] - damage
        # targethpmoji = write code to convert hp to emojis?
        players[str(targetid)]["HP"] = targethp
        players[str(authorid)]["HP"] = max(players[str(authorid)]["HP"] + ((players[str(authorid)]["Rage"])*420),10000)
        players[str(authorid)]["Rage"] = min(players[str(authorid)]["Rage"] -1,0)
        players[str(authorid)]["Rage"] = players[str(authorid)]["Rage"] +3
        cooldown = 86400  # seconds in a day
        players[str(authorid)]["DelayDate"] = current_time + cooldown
        DelayDate_pull = current_time + cooldown
        players[str(authorid)]["Lastaction"] = "normalattack"
        players[str(authorid)]["Evade"] = False
        players[str(authorid)]["Rest"] = False
        with open("players.json", "w") as f:
            json.dump(players, f, indent=4)
        await send_message(f"<@{targetid}> was hit by a normal attack by <@{authorid}>! \nNew HP: {targethp} ", user_id=[authorid,targetid])
        await send_message( f"<@{authorid}> used a normal attack on <@{targetid}>! \n<@{authorid}> is on cooldown until <t:{DelayDate_pull}>", channel_id=[channelid])

@bot.command(
    name="normalattack",
    description="48h.3rage. attack a player in your area for 2300.",
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
    # Rage_pull=players[str(ctx.author.id)]["Rage"]
    current_time = int(time.time())
    print(f"{playertarget} is the player target")
    for k, v in players.items():
        if v['Username'] == str(playertarget):
            targetid = k
    print(f"{targetid} is the player target id")
    if str(ctx.author.id) in players:
        DelayDate_pull = players[str(ctx.author.id)]["DelayDate"]
        if DelayDate_pull > current_time:
            await queuenexttarget(ctx, targetid )
            await ctx.send(f"You cannot act yet! You are delayed until <t:{DelayDate_pull}>.", ephemeral=True)  # golive
        else:
            await donormalattack(ctx.author.id, targetid, general)
    else:
        await ctx.send(f"You need to join with /join before you can do that!", ephemeral=True)

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
async def doheavyattack(authorid,targetid,channelid):
    players = await getplayerdata()
    current_time = int(time.time())
    if players[str(targetid)]["Evade"]:
        damage = 0
        targethp = players[str(targetid)]["HP"] - damage
        # targethpmoji = write code to convert hp to emojis?
        players[str(targetid)]["HP"] = targethp
        players[str(authorid)]["HP"] = max(players[str(authorid)]["HP"] + ((players[str(authorid)]["Rage"])*420),10000)
        players[str(authorid)]["Rage"] = min(players[str(authorid)]["Rage"] -1,0)
        players[str(authorid)]["Rage"] = players[str(authorid)]["Rage"] +6
        cooldown = 86400  # seconds in a day
        players[str(authorid)]["DelayDate"] = current_time + cooldown
        DelayDate_pull = current_time + cooldown
        players[str(authorid)]["Lastaction"] = "heavyattack"
        players[str(authorid)]["Evade"] = False
        players[str(authorid)]["Rest"] = False
        with open("players.json", "w") as f:
            json.dump(players, f, indent=4)
        await send_message(f"<@{targetid}> evaded a heavy attack from <@{authorid}>! \nNew HP: {targethp} ", user_id=[authorid,targetid])
        await send_message(f"<@{authorid}> used a heavy attack on <@{targetid}>! \n<@{authorid}> is on cooldown until <t:{DelayDate_pull}>", channel_id=[channelid])
    else:
        UsedInventory_pull = players[str(authorid)]["UsedInventory"]
        damage = 950 + (UsedInventory_pull.count("drinkingchallengemedal") * 420)
        targethp = players[str(targetid)]["HP"] - damage
        # targethpmoji = write code to convert hp to emojis?
        players[str(targetid)]["HP"] = targethp
        players[str(authorid)]["HP"] = max(players[str(authorid)]["HP"] + ((players[str(authorid)]["Rage"])*420),10000)
        players[str(authorid)]["Rage"] = min(players[str(authorid)]["Rage"] -1,0)
        players[str(authorid)]["Rage"] = players[str(authorid)]["Rage"] +6
        cooldown = 86400  # seconds in a day
        players[str(authorid)]["DelayDate"] = current_time + cooldown
        DelayDate_pull = current_time + cooldown
        players[str(authorid)]["Lastaction"] = "heavyattack"
        players[str(authorid)]["Evade"] = False
        players[str(authorid)]["Rest"] = False
        with open("players.json", "w") as f:
            json.dump(players, f, indent=4)
        await send_message(f"<@{targetid}> was hit by a heavy attack by <@{authorid}>! \nNew HP: {targethp} ", user_id=[authorid,targetid])
        await send_message( f"<@{authorid}> used a heavy attack on <@{targetid}>! \n<@{authorid}> is on cooldown until <t:{DelayDate_pull}>", channel_id=[channelid])
@bot.command(
    name="heavyattack",
    description="72h.6rage. attack a player in your area for 3650.",
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
    # Rage_pull=players[str(ctx.author.id)]["Rage"]
    current_time = int(time.time())
    print(f"{playertarget} is the player target")
    for k, v in players.items():
        if v['Username'] == str(playertarget):
            targetid = k
    print(f"{targetid} is the player target id")
    if str(ctx.author.id) in players:
        DelayDate_pull = players[str(ctx.author.id)]["DelayDate"]
        if DelayDate_pull > current_time:
            await queuenexttarget(ctx, targetid )
            await ctx.send(f"You cannot act yet! You are delayed until <t:{DelayDate_pull}>.", ephemeral=True)  # golive
        else:
            await doheavyattack(ctx.author.id, targetid, general)
    else:
        await ctx.send(f"You need to join with /join before you can do that!", ephemeral=True)


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
async def dointerrupt(authorid,targetid,channelid):
    players = await getplayerdata()
    current_time = int(time.time())
    print(players[str(targetid)]["Evade"])
    print(players[str(targetid)]["Rest"])
    if players[str(targetid)]["Evade"] or players[str(targetid)]["Rest"]:
        targethp = players[str(targetid)]["HP"] - 4200
        players[str(targetid)]["HP"] = targethp
        players[str(authorid)]["HP"] = max(players[str(authorid)]["HP"] + ((players[str(authorid)]["Rage"])*420),10000)
        players[str(authorid)]["Rage"] = min(players[str(authorid)]["Rage"] -1,0)
        cooldown = 86400 * 1  # seconds in one day
        players[str(authorid)]["DelayDate"] = current_time + cooldown
        DelayDate_pull = current_time + cooldown
        players[str(authorid)]["Lastaction"] = "interrupt"
        players[str(authorid)]["Evade"] = False
        players[str(authorid)]["Rest"] = False
        with open("players.json", "w") as f:
            json.dump(players, f, indent=4)
        await send_message(f"<@{targetid}> was hit and damaged by an interrupt by <@{authorid}>! \nNew HP: {targethp} ", user_id=[authorid,targetid])
        await send_message(f"<@{authorid}> used an interrupt on <@{targetid}>! \n<@{authorid}> is on cooldown until <t:{DelayDate_pull}>",channel_id=channelid)
    else:
        # players[str(authorid)]["Rage"] = players[str(authorid)]["Rage"] +200
        cooldown = 86400 * 1  # seconds in one day
        players[str(authorid)]["DelayDate"] = current_time + cooldown
        players[str(authorid)]["HP"] = max(players[str(authorid)]["HP"] + ((players[str(authorid)]["Rage"])*420),10000)
        players[str(authorid)]["Rage"] = min(players[str(authorid)]["Rage"] -1,0)
        DelayDate_pull = current_time + cooldown
        players[str(authorid)]["Lastaction"] = "interrupt"
        players[str(authorid)]["Evade"] = False
        players[str(authorid)]["Rest"] = False
        with open("players.json", "w") as f:
            json.dump(players, f, indent=4)
        await send_message(f"<@{targetid}> was not damaged by an interrupt from <@{authorid}>!", user_id=[authorid,targetid])
        await send_message(f"<@{authorid}> used an interrupt on <@{targetid}>! \n<@{authorid}> is on cooldown until <t:{DelayDate_pull}>",channel_id=[channelid])

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
    # Rage_pull=players[str(ctx.author.id)]["Rage"]
    current_time = int(time.time())
    print(f"{playertarget} is the player target")
    for k, v in players.items():
        if v['Username'] == str(playertarget):
            targetid = k
    print(f"{targetid} is the player target id")
    if str(ctx.author.id) in players:
        DelayDate_pull = players[str(ctx.author.id)]["DelayDate"]
        if DelayDate_pull > current_time:
            await queuenexttarget(ctx, targetid )
            await ctx.send(f"You cannot act yet! You are delayed until <t:{DelayDate_pull}>.", ephemeral=True)  # golive
        else:
            await dointerrupt(ctx.author.id, targetid, general)
    else:
        await ctx.send(f"You need to join with /join before you can do that!", ephemeral=True)

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
async def doevade(authorid):
    players = await getplayerdata()
    players[str(authorid)]["Evade"] = True
    cooldown = int(86400 * 1)  # seconds in one days
    current_time = int(time.time())
    players[str(authorid)]["DelayDate"] = current_time + cooldown
    players[str(authorid)]["Lastaction"] = "evade"
    players[str(authorid)]["HP"] = max(players[str(authorid)]["HP"] + ((players[str(authorid)]["Rage"])*420),10000)
    players[str(authorid)]["Rage"] = min(players[str(authorid)]["Rage"] -1,0)
    DelayDate_pull = players[str(authorid)]["DelayDate"]
    with open("players.json", "w") as f:
        json.dump(players, f, indent=4)
    await send_message(f"<@{authorid}> used evade! \n<@{authorid}> is on cooldown until <t:{DelayDate_pull}>",user_id=[authorid])

@bot.command(
    name="evade",
    description="24h. receive no damage from light normal or heavy attacks",
    scope=guildid,
)
async def evade_command(ctx: interactions.CommandContext):
    players = await getplayerdata()
    if str(ctx.author.id) in players:
        DelayDate_pull = players[str(ctx.author.id)]["DelayDate"]
        current_time = int(time.time())
        if DelayDate_pull > current_time:
            await queuenext(ctx)
            await ctx.send(f"You cannot act yet! You are delayed until <t:{DelayDate_pull}>.", ephemeral = True)
        else:
            doevade(ctx.author.id)
    else:
        await ctx.send(f"You need to join with /join before you can do that!" , ephemeral = True)

#rest is below
async def dorest(authorid):
    players = await getplayerdata()
    players[str(authorid)]["Rest"] = True
    hp_pull = players[str(authorid)]["HP"]
    heal = math.ceil(int((10000 - hp_pull) / 2))
    cooldown = int(86400 * 1)  # seconds in one day
    current_time = int(time.time())
    players[str(authorid)]["DelayDate"] = current_time + cooldown
    players[str(authorid)]["Lastaction"] = "rest"
    players[str(authorid)]["HP"] = max(players[str(authorid)]["HP"] + ((players[str(authorid)]["Rage"])*420),10000)
    players[str(authorid)]["Rage"] = min(players[str(authorid)]["Rage"] -1,0)
    players[str(authorid)]["Rest"] = True
    DelayDate_pull = players[str(authorid)]["DelayDate"]
    players[str(authorid)]["HP"] = min(players[str(authorid)]["HP"] + heal, 10000)
    with open("players.json", "w") as f:
        json.dump(players, f, indent=4)
    await send_message(f"<@{authorid}> used rest! \n<@{authorid}> is on cooldown until <t:{DelayDate_pull}>", user_id=[authorid])

@bot.command(
    name="rest",
    description="24h. heal half your missing health rounded up unless you rested last action.",
    scope=guildid,
)
async def rest_command(ctx: interactions.CommandContext):
    players = await getplayerdata()
    if str(ctx.author.id) in players:
        DelayDate_pull = players[str(ctx.author.id)]["DelayDate"]
        current_time = int(time.time())
        Lastaction_pull=players[str(ctx.author.id)]["Lastaction"]
        if Lastaction_pull == "rest":
                await ctx.send(f"You cannot rest! You rested as your last action!", ephemeral = True)
        elif DelayDate_pull > current_time:
            await queuenext(ctx)
            await ctx.send(f"You cannot act yet! You are delayed until <t:{DelayDate_pull}>.", ephemeral = True)
        else:
             dorest(ctx.author.id)
    else:
        await ctx.send(f"You need to join with /join before you can do that!" , ephemeral = True)

#travelto
async def dotravelto(authorid,targetid,channelid):
    locations = await getlocationdata()
    destination = locations[targetid]['Name']
    players = await getplayerdata()
    current_time = int(time.time())
    cooldown = 86400 * 1  # seconds in one day
    players[str(authorid)]["DelayDate"] = current_time + cooldown
    DelayDate_pull = current_time + cooldown
    players[str(authorid)]["Lastaction"] = "travelto"
    players[str(authorid)]["Location"] = destination
    players[str(authorid)]["Evade"] = False
    players[str(authorid)]["Rest"] = False
    players[str(authorid)]["HP"] = max(players[str(authorid)]["HP"] + ((players[str(authorid)]["Rage"])*420),10000)
    players[str(authorid)]["Rage"] = min(players[str(authorid)]["Rage"] -1,0)
    with open("players.json", "w") as f:
        json.dump(players, f, indent=4)

    user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
    await user.remove_role(role=crossroads, guild_id=guildid)
    await user.add_role(role=targetid, guild_id=guildid)
    await send_message(f"<@{authorid}> traveled to {destination}! \n<@{authorid}> is on cooldown until <t:{DelayDate_pull}>",user_id=[authorid],channel_id=[channelid])

@bot.command(
    name="travelto",
    description="24h. travel to any location from the crossroads .",
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
async def travelto(ctx: interactions.CommandContext, destination: str):
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
            await queuenexttarget(ctx,destinationid)
            await ctx.send(f"You cannot act yet! You are delayed until <t:{DelayDate_pull}>.", ephemeral = True) #golive
        else:
            await dotravelto(ctx.author.id,destinationid)
    else:
        await ctx.send(f"You need to join with /join before you can do that!" , ephemeral = True)


@bot.autocomplete("travelto", "destination")
async def travelto_autocomplete(ctx: interactions.CommandContext, value: str = ""):
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
async def dotraveltocrossroads(authorid):
    players = await getplayerdata()
    current_time = int(time.time())
    cooldown = 86400 * 1  # seconds in one day
    players[str(authorid)]["DelayDate"] = current_time + cooldown
    DelayDate_pull = current_time + cooldown
    players[str(authorid)]["Evade"] = False
    players[str(authorid)]["Rest"] = False
    players[str(authorid)]["Lastaction"] = "travelto"
    players[str(authorid)]["Evade"] = False
    players[str(authorid)]["Rest"] = False
    players[str(authorid)]["Location"] = "Crossroads"
    players[str(authorid)]["HP"] = max(players[str(authorid)]["HP"] + ((players[str(authorid)]["Rage"])*420),10000)
    players[str(authorid)]["Rage"] = min(players[str(authorid)]["Rage"] -1,0)
    with open("players.json", "w") as f:
        json.dump(players, f, indent=4)
    user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
    await user.remove_role(role=dungeon, guild_id=guildid)
    await user.remove_role(role=farmland, guild_id=guildid)
    await user.remove_role(role=keep, guild_id=guildid)
    await user.remove_role(role=lichcastle, guild_id=guildid)
    await user.remove_role(role=shop, guild_id=guildid)
    await user.remove_role(role=tavern, guild_id=guildid)
    await user.add_role(role=crossroads, guild_id=guildid)
    await send_message(f"<@{authorid}> traveled to the Crossroads! \n<@{authorid}> is on cooldown until <t:{DelayDate_pull}>",user_id=[authorid])
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
            await queuenext(ctx)
            await ctx.send(f"You cannot act yet! You are delayed until <t:{DelayDate_pull}>.", ephemeral = True) #golive
        else:
            await dotraveltocrossroads(ctx.author.id)
    else:
        await ctx.send(f"You need to join with /join before you can do that!" , ephemeral = True)

@bot.command(
    name="status",
    description="check your status.",
    scope=guildid,
)
async def status (ctx: interactions.CommandContext):
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
    Nextaction_pull = players[str(ctx.author.id)]["Nextaction"]
    await ctx.send(f"{ctx.author}'s HP: {hp_pull} \nLocation: {location_pull} \nSC: {SC_pull} \nRage: {Rage_pull} \nInventory: \n    Ready: {ReadyInventory_pull} \n    Used:{UsedInventory_pull} \nCooldown: <t:{DelayDate_pull}>", ephemeral = True)

#exchange is below

@bot.command(
    name="exchange",
    description="24h. give a player in your area a ready item from your inventory.",
    scope = guildid ,
    options=[
        interactions.Option(
            type=interactions.OptionType.STRING,
            name="playertarget",
            description="who you want to give something to",
            required=True,
            autocomplete=True,
        ),
        interactions.Option(
            type=interactions.OptionType.STRING,
            name="readyitem",
            description="the item you want to give",
            required=True,
            autocomplete=True,
        )
    ]
)
async def exchange(ctx: interactions.CommandContext, playertarget: str, readyitem: str):
    players = await getplayerdata()
    #Rage_pull=players[str(ctx.author.id)]["Rage"]
    current_time = int(time.time())
    print(f"{playertarget} is the player target")
    print(f"{readyitem} is the item target")
    for k,v in players.items():
        if v['Username']==str(playertarget):
            targetid=k
    print(f"{targetid} is the player target id")
    if str(ctx.author.id) in players:
        DelayDate_pull = players[str(ctx.author.id)]["DelayDate"]
        if DelayDate_pull > current_time:
            await ctx.send(f"You cannot act yet! You are delayed until <t:{DelayDate_pull}>.", ephemeral = True) #golive
        else:
            ReadyInventory_pull = str(players[str(ctx.author.id)]["ReadyInventory"])
            if ReadyInventory_pull == "":
                await ctx.send(f"You don't have any items in your Ready Inventory!", ephemeral = True)
            else:
                cooldown=86400*1 #seconds in one day
                players[str(ctx.author.id)]["DelayDate"] = current_time+cooldown
                DelayDate_pull=current_time+cooldown
                players[str(ctx.author.id)]["HP"] = max(players[str(ctx.author.id)]["HP"] + ((players[str(ctx.author.id)]["Rage"])*420),10000)
                players[str(ctx.author.id)]["Rage"] = min(players[str(ctx.author.id)]["Rage"] -1,0)
                players[str(ctx.author.id)]["Lastaction"] = "exchange"
                players[str(ctx.author.id)]["Evade"] = False
                players[str(ctx.author.id)]["Rest"] = False
                players[str(targetid)]["ReadyInventory"] = players[str(targetid)]["ReadyInventory"]  + "\n        " + readyitem
                ReadyInventory_pull = str(players[str(ctx.author.id)]["ReadyInventory"])
                ReadyInventory_pull = ReadyInventory_pull.replace(str("\n        " +readyitem), "",1)
                players[str(ctx.author.id)]["ReadyInventory"] = ReadyInventory_pull
                with open("players.json","w") as f:
                    json.dump(players,f, indent=4)
                await ctx.send(f"<@{targetid}> was given {readyitem} from <@{ctx.author.id}>!", ephemeral=False)
                await ctx.send(f"<@{ctx.author.id}> gave an item to <@{targetid}>! \n<@{ctx.author.id}> is on cooldown until <t:{DelayDate_pull}>", ephemeral=False)

    else:
        await ctx.send(f"You need to join with /join before you can do that!" , ephemeral = True)


@bot.autocomplete("exchange", "playertarget")
async def exchange_autocomplete(ctx: interactions.CommandContext, value: str = ""):
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


@bot.autocomplete("exchange", "readyitem")
async def exchange_autocomplete(ctx: interactions.CommandContext, value: str = ""):
    players = await getplayerdata()
    ReadyInventory_pull = str(players[str(ctx.author.id)]["ReadyInventory"])
    print(ReadyInventory_pull)
    readyitems = list(filter(None, list(ReadyInventory_pull.split("\n        "))))
    print (readyitems)
    items = readyitems
    choices = [
        interactions.Choice(name=item, value=item) for item in items if value in item
    ]
    await ctx.populate(choices)

#farm is below
async def dofarm(authorid):
    players = await getplayerdata()
    current_time = int(time.time())
    farmSC = int(random.randint(0, 4))  # +randbuff
    SC_pull = players[str(authorid)]["SC"] + farmSC  # +randbuff
    cooldown = 86400 * 1  # seconds in one day
    players[str(authorid)]["SC"] = SC_pull
    players[str(authorid)]["DelayDate"] = current_time + cooldown
    DelayDate_pull = current_time + cooldown
    players[str(authorid)]["Lastaction"] = "farm"
    players[str(authorid)]["Evade"] = False
    players[str(authorid)]["Rest"] = False
    players[str(authorid)]["HP"] = max(players[str(authorid)]["HP"] + ((players[str(authorid)]["Rage"])*420),10000)
    players[str(authorid)]["Rage"] = min(players[str(authorid)]["Rage"] -1,0)
    with open("players.json", "w") as f:
        json.dump(players, f, indent=4)
    #TODO implement channel specific messages... I don't have permission->channel linking in my test env
    await send_message(f"<@{authorid}> farmed {farmSC} from farming", user_id=[authorid]) #channel_id=[farmland])
    await send_message(f"<@{authorid}> farmed! \n<@{authorid}> is on cooldown until <t:{DelayDate_pull}>", user_id=[authorid])

@bot.command(
    name="farm",
    description="24h. roll 1d4 gain that many seed coins.",
    scope = guildid ,
)
async def farm(ctx: interactions.CommandContext):
    players = await getplayerdata()
    current_time = int(time.time())
    if str(authorid) in players:
        DelayDate_pull = players[str(authorid)]["DelayDate"]
        if farmland not in ctx.author.roles:
            await ctx.send(f"You cannot farm when you are not in the farmland!", ephemeral=True)  # golive
        elif DelayDate_pull > current_time:
            await queuenext(ctx)
            await ctx.send(f"You cannot act yet! You are delayed until <t:{DelayDate_pull}>.", ephemeral = True) #golive
        else:
            dofarm(authorid)
    else:
        await ctx.send(f"You need to join with /join before you can do that!" , ephemeral = True)

#aid is below

@bot.command(
    name="aid",
    description="24h. heal chosen player 1/4 of their missing health.",
    scope = guildid ,
    options=[
        interactions.Option(
            type=interactions.OptionType.STRING,
            name="playertarget",
            description="who you want to aid",
            required=True,
            autocomplete=True,
        )
    ]
)
async def aid(ctx: interactions.CommandContext, playertarget: str):
    players = await getplayerdata()
    #Rage_pull=players[str(ctx.author.id)]["Rage"]
    current_time = int(time.time())
    print(f"{playertarget} is the player target")
    for k,v in players.items():
        if v['Username']==str(playertarget):
            targetid=k
    print(f"{targetid} is the player target id")
    if str(ctx.author.id) in players:
        DelayDate_pull = players[str(ctx.author.id)]["DelayDate"]
        if DelayDate_pull > current_time:
            await ctx.send(f"You cannot act yet! You are delayed until <t:{DelayDate_pull}>.", ephemeral = True) #golive
        else:
            #players[str(ctx.author.id)]["Rage"] = players[str(ctx.author.id)]["Rage"] +200
            targethp=players[str(targetid)]["HP"]
            heal = min(math.ceil(int((10000 - targethp)/4)),10000)
            cooldown=86400*1 #seconds in one day
            players[str(ctx.author.id)]["DelayDate"] = current_time+cooldown
            DelayDate_pull=current_time+cooldown
            players[str(ctx.author.id)]["Lastaction"] = "aid"
            players[str(ctx.author.id)]["Evade"] = False
            players[str(ctx.author.id)]["Rest"] = False
            players[str(targetid)]["HP"] = players[str(targetid)]["HP"] + heal
            players[str(ctx.author.id)]["HP"] = max(players[str(ctx.author.id)]["HP"] + ((players[str(ctx.author.id)]["Rage"])*420),10000)
            players[str(ctx.author.id)]["Rage"] = min(players[str(ctx.author.id)]["Rage"] -1,0)
            targethp=players[str(targetid)]["HP"]
            with open("players.json","w") as f:
                json.dump(players,f, indent=4)
            await ctx.send(f"<@{targetid}> was healed by aid from <@{ctx.author.id}>! \nNew HP: {targethp} ", ephemeral=True)
            await ctx.send(f"<@{ctx.author.id}> used aid on <@{targetid}> to heal them! \n<@{ctx.author.id}> is on cooldown until <t:{DelayDate_pull}>", ephemeral=False)
            await asyncio.sleep(cooldown)
            players[str(ctx.author.id)]["DelayDate"] = current_time
            with open("players.json","w") as f:
                json.dump(players,f, indent=4)
            await ctx.send(f"<@{ctx.author.id}> Your cooldown is over and you are free to act!", ephemeral = True)
    else:
        await ctx.send(f"You need to join with /join before you can do that!" , ephemeral = True)


@bot.autocomplete("aid", "playertarget")
async def aid_autocomplete(ctx: interactions.CommandContext, value: str = ""):
    players = await getplayerdata()
    Usernames = [v["Username"] for v in players.values()]
    print (Usernames)
    items = Usernames
    choices = [
        interactions.Choice(name=item, value=item) for item in items if value in item
    ]
    await ctx.populate(choices)

@bot.command(
    name="drinkingchallenge",
    description="24h. 1d4 high: used drinkingchallengemedal low: lose .25 currenthealth else: heal .25 missing health",
    scope = guildid ,
)
async def drinkingchallenge (ctx: interactions.CommandContext):
    players = await getplayerdata()
    #Rage_pull=players[str(ctx.author.id)]["Rage"]
    scores = await gettaverndata()
    current_time = int(time.time())
    playerroll = int(random.randint(1,4))
    print(f"playerroll = {playerroll}")
    print(f"scores = \n{scores}")
    cooldown=86400 #seconds in a day
    if str(ctx.author.id) in players:
        DelayDate_pull = players[str(ctx.author.id)]["DelayDate"]
        Username_pull = players[str(ctx.author.id)]["Username"]
        print(f"{Username_pull} is delayed until {DelayDate_pull}?{current_time} is currrenttime")
        if DelayDate_pull > current_time:
            await ctx.send(f"You cannot act yet! You are delayed until <t:{DelayDate_pull}>.", ephemeral = True) #golive
        else:
            if scores[str("NPC4")]["Scoreexpiry"] > current_time :
                highscore= max(x["Score"] for x in scores.values() if x["Scoreexpiry"] > current_time)
                lowscore= min(x["Score"] for x in scores.values() if x["Scoreexpiry"] > current_time)
                print("NPC4 score is not expired, and has not been rewritten")
                print(f"highscore is {highscore}")
            else:
                scores[str("NPC4")]["Score"] = int(random.randint(1,4)-1)
                scores[str("NPC4")]["Scoreexpiry"] = current_time +cooldown
                print("NPC4 score is expired, and has been rewritten")
                highscore= max(x["Score"] for x in scores.values() if x["Scoreexpiry"] > current_time)
                lowscore= min(x["Score"] for x in scores.values() if x["Scoreexpiry"] > current_time)
                print(f"highscore is {highscore}")
            if scores[str("NPC3")]["Scoreexpiry"] > current_time:
                highscore= max(x["Score"] for x in scores.values() if x["Scoreexpiry"] > current_time)
                lowscore= min(x["Score"] for x in scores.values() if x["Scoreexpiry"] > current_time)
                print("NPC3 score is not expired, and has not been rewritten")
                print(f"highscore is {highscore}")
            else:
                scores[str("NPC3")]["Score"] = int(random.randint(1,4)-1)
                scores[str("NPC3")]["Scoreexpiry"] = current_time +cooldown
                print("NPC3 score is expired, and has been rewritten")
                highscore= max(x["Score"] for x in scores.values() if x["Scoreexpiry"] > current_time)
                lowscore= min(x["Score"] for x in scores.values() if x["Scoreexpiry"] > current_time)
                print(f"highscore is {highscore}")
            if highscore > playerroll: #check if the max is greater than the player's roll
                await ctx.send(f"<@{ctx.author.id}>'s roll of {playerroll} failed to beat the high score of {highscore}" , ephemeral = False)
                scores[str(ctx.author.id)] = {}
                scores[str(ctx.author.id)]["Username"] = str(ctx.author.user)
                scores[str(ctx.author.id)]["Media"] = str(ctx.author.get_avatar_url(guildid))
                scores[str(ctx.author.id)]["Score"] = playerroll
                scores[str(ctx.author.id)]["Scoreexpiry"] = current_time+cooldown
                print(f"Highscore is {highscore} which is greater than player's {playerroll}")
                players[str(ctx.author.id)]["HP"] = max(players[str(ctx.author.id)]["HP"] + ((players[str(ctx.author.id)]["Rage"])*420),10000)
                players[str(ctx.author.id)]["Rage"] = min(players[str(ctx.author.id)]["Rage"] -1,0)
                with open("tavern.json","w") as j:
                    json.dump(scores,j, indent=4)
                hslist = '\n\n'.join('\n'.join((x["Username"], x["Media"])) for x in scores.values() if x["Score"] == highscore)
                print(f"{hslist}")
                await ctx.send(f"The highscore belongs to \n{hslist}" , ephemeral = False)
                if lowscore == playerroll: #check if the min is equal to the player's roll
                    hp_pull = players[str(ctx.author.id)]["HP"]
                    hp_pull=max(hp_pull - math.ceil(hp_pull/4),0)
                    await ctx.send(f"<@{ctx.author.id}> your roll of {playerroll} is the lowest roll. \nNew HP: {hp_pull}" , ephemeral = True )
                    await ctx.send(f"<@{ctx.author.id}>'s roll of {playerroll} is the lowest roll and they lose 1/4 of their current health!" , ephemeral = False )
                    players[str(ctx.author.id)]["HP"] = hp_pull
                    players[str(ctx.author.id)]["Lastaction"] = "drinkingchallenge"
                    players[str(ctx.author.id)]["Evade"] = False
                    players[str(ctx.author.id)]["Rest"] = False
                    players[str(ctx.author.id)]["DelayDate"] = current_time + cooldown
                    with open("players.json","w") as f:
                        json.dump(players,f, indent=4)
                    await asyncio.sleep(cooldown)
                    players[str(ctx.author.id)]["DelayDate"] = current_time
                    with open("players.json","w") as f:
                        json.dump(players,f, indent=4)
                    await ctx.send(f"<@{ctx.author.id}> Your cooldown is over and you are free to act!", ephemeral = True)
                else:
                    hp_pull = players[str(ctx.author.id)]["HP"]
                    hp_pull=min(hp_pull+math.ceil((10000-hp_pull)/4),10000)
                    await ctx.send(f"<@{ctx.author.id}> your roll of {playerroll} is neither the high nor low roll. \nNew HP: {hp_pull}" , ephemeral = True )
                    await ctx.send(f"<@{ctx.author.id}>'s roll of {playerroll} is neither the high nor low roll. They heal for 1/4 of their missing health!" , ephemeral = False )
                    players[str(ctx.author.id)]["HP"] = hp_pull
                    players[str(ctx.author.id)]["Lastaction"] = "drinkingchallenge"
                    players[str(ctx.author.id)]["Evade"] = False
                    players[str(ctx.author.id)]["Rest"] = False
                    players[str(ctx.author.id)]["DelayDate"] = current_time + cooldown
                    players[str(ctx.author.id)]["HP"] = max(players[str(ctx.author.id)]["HP"] + ((players[str(ctx.author.id)]["Rage"])*420),10000)
                    players[str(ctx.author.id)]["Rage"] = min(players[str(ctx.author.id)]["Rage"] -1,0)
                    with open("players.json","w") as f:
                        json.dump(players,f, indent=4)
                    await asyncio.sleep(cooldown)
                    players[str(ctx.author.id)]["DelayDate"] = current_time
                    with open("players.json","w") as f:
                        json.dump(players,f, indent=4)
                    await ctx.send(f"<@{ctx.author.id}> Your cooldown is over and you are free to act!", ephemeral = True)
            else:
                await ctx.send(f"You rolled the high roll of {playerroll}! gaining a drinkingchallengemedal in your used inventory!")
                UsedInventory_pull=players[str(ctx.author.id)]["UsedInventory"] + "\n        "+"drinkingchallengemedal"
                players[str(ctx.author.id)]["Lastaction"] = "drinkingchallenge"
                players[str(ctx.author.id)]["Evade"] = False
                players[str(ctx.author.id)]["Rest"] = False
                players[str(ctx.author.id)]["DelayDate"] = current_time + cooldown
                players[str(ctx.author.id)]["UsedInventory"] = UsedInventory_pull
                scores[str(ctx.author.id)] = {}
                scores[str(ctx.author.id)]["Username"] = str(ctx.author.user)
                scores[str(ctx.author.id)]["Media"] = "https://cdn.discordapp.com/avatars/"+str(ctx.author.id)+"/"+str(ctx.author.get_avatar_url(guildid))
                scores[str(ctx.author.id)]["Score"] = playerroll
                scores[str(ctx.author.id)]["Scoreexpiry"] = current_time+cooldown
                hp_pull=players[str(ctx.author.id)]["HP"]
                players[str(ctx.author.id)]["HP"] = max(players[str(ctx.author.id)]["HP"] + ((players[str(ctx.author.id)]["Rage"])*420),10000)
                players[str(ctx.author.id)]["Rage"] = min(players[str(ctx.author.id)]["Rage"] -1,0)
                with open("tavern.json","w") as j:
                    json.dump(scores,j, indent=4)
                with open("players.json","w") as f:
                    json.dump(players,f, indent=4)
                await ctx.send(f"<@{ctx.author.id}> your roll of {playerroll} is the high roll. \nNew HP: {hp_pull}" , ephemeral = True )
                await ctx.send(f"<@{ctx.author.id}>'s roll of {playerroll} is the high roll. They gain a **drinkingchallengemedal** that increases their light attack damage!" , ephemeral = False )
                await asyncio.sleep(cooldown)
                players[str(ctx.author.id)]["DelayDate"] = current_time
                with open("players.json","w") as f:
                    json.dump(players,f, indent=4)
                await ctx.send(f"<@{ctx.author.id}> Your cooldown is over and you are free to act!", ephemeral = True)
    else:
        await ctx.send(f"You need to join with /join before you can do that!" , ephemeral = True)

functiondict = {'lightattack' : dolightattack,
                'normalattack' : donormalattack,
                'heavyattack' : doheavyattack,
                'interrupt' : dointerrupt,
                'evade' : doevade,
                'rest' : dorest,
                'farm' : dofarm,
                'travelto' : dotravelto,
                'traveltocrossroads': dotraveltocrossroads}

bot.start ()

import interactions
from interactions import Button, ButtonStyle, SelectMenu, SelectOption, ActionRow, spread_to_rows
import asyncio
import random
from datetime import datetime
import random
import time
import math
import json
from typing import List

with open('.gitignore2/config.json', 'r') as cfg:
   tokens = json.load(cfg)

#load in location data
global locations
with open("locations.json", "r") as i:
    locations = json.load(i)

#how long the lowest cooldowns are
basecd = tokens["basecooldown"]

#channel ids
general = tokens["generalchannelid"]
guildid= tokens["guildid"]
poisonchannel= tokens["poisonchannelid"]

bot = interactions.Client(token=tokens["token"], intents=interactions.Intents.DEFAULT | interactions.Intents.GUILD_MESSAGE_CONTENT)

#new poison
#poison to poison.json to keep it consistent between script reboots
@bot.event
async def on_ready():
    print(f"We're online! We've logged in as {bot.me.name}.")
    print(f"Our latency is {round(bot.latency)} ms.")
    current_time = int(time.time())
    guild = await interactions.get(bot, interactions.Guild, object_id=guildid)
    members = await guild.get_all_members()
    print(members)
    loop = asyncio.get_running_loop()
    loop.create_task(pollfornext())
    loop.create_task(pollforready())
    loop.create_task(pollforqueue())
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
            poisontimer_pull=max(math.ceil(poisontimer_pull*.9),basecd)
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
            await channel.send(f"Poison damage increased by 100 then dealt **{poisondamage_pull} damage** to everyone! \nThe time between poison damage decreases by 10%! \nThe next poison damage occurs on <t:{nextpoisontime}> (in {poisontimer_pull} seconds) to deal {min(poisondamage_pull +100, 1500)} damage." )
            poison["poisondate"] = nextpoisontime
            poison["poisondamage"] = poisondamage_pull
            poison["poisontimer"] = poisontimer_pull
            with open("poison.json","w") as h:
               json.dump(poison,h, indent=4)
        else:
            print("hi")
            #await channel.send(f"I have awoken! \nThe next poison comes <t:{poisondate_pull}> ({int(poisondate_pull-current_time)} seconds) to deal {int(poisondamage_pull+100)} damage.")
    else:
        smalltime=int(basecd) #set to 86400 (seconds in a day) when golive and blank poison.json
        smalltimeunit="days" #set to days on golive
        firstcountdown=int(7*smalltime)
        nextpoisontime=current_time+firstcountdown
        poison = {}
        poison["poisondate"] = nextpoisontime
        poison["firstpoisondate"] = nextpoisontime
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
        await channel.send(f"The first poison damage occurs on <t:{nextpoisontime}> (in {poisontimer_pull} seconds) to deal {min(poisondamage_pull +100, 1500)} damage." )
    await asyncio.sleep(int(poisondate_pull-current_time))
    while poisondamage_pull < 500000:
        poisondamage_pull= min(poison["poisondamage"] +100, 1500)
        poisontimer_pull=max(math.ceil(poisontimer_pull*.9),basecd)
        nextpoisontime=int(current_time+poisontimer_pull)
        print(f"{poisondamage_pull} poison damage at {nextpoisontime} and {poisontimer_pull} seconds till next poison")
        await channel.send(f"Poison damage increased by 100 then dealt **{poisondamage_pull} damage** to everyone! \nThe time between poison damage decreases by 10%! \nThe next poison damage occurs on <t:{nextpoisontime}> (in {poisontimer_pull} seconds) to deal {min(poisondamage_pull +100, 1500)} damage." )
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
        f"We've received a message from {message.author.username} in {message.channel_id}. \nThe message is: \n\n{message.content}\n \nend content\n"
    )
    #if interactions.ChannelType.DM == True :
    #    print ("3")
    #    channel = message.channel_id
    #    await channel.send("join the test environment! \n test")
    #else:
    #    pass

async def deadcheck(targethp,targetid,authorid,players):
    print(f"\ndead?:{int(time.time())}")
    if targethp <= 0:
        print(f"\n the target died!")
        user = await interactions.get(bot, interactions.Member, object_id=targetid, guild_id=guildid, force='http')
        await send_message(f"<@{targetid}> died because of <@{authorid}>!", channel_id=[general])
        #give dead role
        await user.add_role(role=locations["Dead"]["Role_ID"], guild_id=guildid)
        #remove all location roles and playing roles to hopefully block all commands?
        await user.remove_role(role=locations["Dungeon"]["Role_ID"], guild_id=guildid)
        await user.remove_role(role=locations["Farmland"]["Role_ID"], guild_id=guildid)
        await user.remove_role(role=locations["Keep"]["Role_ID"], guild_id=guildid)
        await user.remove_role(role=locations["Lich's Castle"]["Role_ID"], guild_id=guildid)
        await user.remove_role(role=locations["Shop"]["Role_ID"], guild_id=guildid)
        await user.remove_role(role=locations["Tavern"]["Role_ID"], guild_id=guildid)
        await user.remove_role(role=locations["Playing"]["Role_ID"], guild_id=guildid)
        await user.remove_role(role=locations["Crossroads"]["Role_ID"], guild_id=guildid)
        #change players.json location to dead
        players[str(targetid)]["Location"] = "Dead"
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
    else:
        print(f"\n the target didn't die!")

#rage heals 420 for each rage stack then decreases by 1
async def rage(authorid):
    rageplayers = await getplayerdata()
    rageplayers[str(authorid)]["HP"] = min(rageplayers[str(authorid)]["HP"] + ((rageplayers[str(authorid)]["Rage"])*420),10000)
    rageplayers[str(authorid)]["Rage"] = max(rageplayers[str(authorid)]["Rage"] -1,0)
    with open("players.json","w") as f:
        json.dump(rageplayers,f, indent=4)
    return

#hpmojiconv function converts an hp number into a string of hp squares
async def hpmojiconv(hp):
    players = await getplayerdata()
    numofgreensqs = math.floor(hp/500)
    numofredsqs = math.floor((10000-hp)/500)
    yellowsq = math.ceil((hp-(numofgreensqs*500))/500)
    hpmoji = str(numofgreensqs*":green_square:")+(yellowsq*":yellow_square:")+str(numofredsqs*":red_square:")
    return hpmoji

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

async def gettaverndata():
    with open("tavern.json","r") as j:
        scores = json.load(j)
    return scores

async def getshopdata():
    with open("shop.json","r") as m:
        shop = json.load(m)
    return shop

async def getdungeondata():
    with open("dungeon.json","r") as o:
        scores = json.load(o)
    return scores

async def getlichdata():
    with open("lichcastle.json","r") as l:
        scores = json.load(l)
    return scores

async def pollfornext():
    #run forever
    while True:
        print(f"\npolling for next:{int(time.time())}")
        players = await getplayerdata()
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
                        loop.create_task(functiondict[words[0]]( **{'authorid':k,'destination':words[1]}))
                        print(f"{v['Username']} is doing {words[0]} {words[1]}")
                    players[k]['Nextaction'] = ""
                    with open("players.json", "w") as f:
                        json.dump(players, f, indent=4)
                else:
                    if len(words) == 1:
                        print(f"{v['Username']} is not ready to {words[0]}")
                    elif words[1] in players:
                        print(f"{v['Username']} is not ready to {words[0]} {players[words[1]]['Username']}")
                    elif words[1] in locations:
                        print(f"{v['Username']} is not ready to {words[0]} {words[1]}")
        await asyncio.sleep(120)

async def pollforready():
    #run forever
    while True:
        print(f"\npolling for ready:{int(time.time())}")
        players = await getplayerdata()
        readyplayers = [k for k, v in players.items() if v['DelayDate'] < int(time.time()) and v['Location'] != "Dead"]
        print(readyplayers)
        #don't turn this on until the bot is not relaunching often
        #await send_message(f"Your cooldown is over! You are ready to act!", user_id=readyplayers)
        await asyncio.sleep(int(1*60*60*48)) #48 hour reminder

async def pollforqueue():
    #run forever
    while True:
        print(f"\npolling for no queue:{int(time.time())}")
        players = await getplayerdata()
        noqueueplayers = [k for k, v in players.items() if v['Nextaction'] == "" and v['Location'] != "Dead"]
        print(noqueueplayers)
        #don't turn this on until the bot is not relaunching often
        #await send_message(f"You have no action queued! You can queue an action with a slash command!", user_id=noqueueplayers)
        await asyncio.sleep(int(1*60*60*48)) #48 hour reminder

async def lastactiontime(authorid):
    players = await getplayerdata()
    players[str(authorid)]["Lastactiontime"]=int(time.time())
    return players

async def send_message(message : str, **kwargs):
    if('user_id' in kwargs.keys()):
        for targetid in kwargs['user_id']:
            user = await interactions.get(bot, interactions.Member, object_id=targetid, guild_id=guildid, force='http')
            await user.send(message)
    if ('channel_id' in kwargs.keys()):
        for targetid in kwargs['channel_id']:
            channel = await interactions.get(bot, interactions.Channel, object_id=targetid, force='http')
            await channel.send(message)

async def queuenext(ctx):
    players = await getplayerdata()
    #separate strings for printing to player and what we use (id)
    saveaction = f"{ctx.data.name}"
    displayaction = f"{ctx.data.name}"
    if players[ctx.author.id]["Nextaction"] != "":
        words = players[ctx.author.id]['Nextaction'].split()
        if len(words) == 1:
            await ctx.send(f"You already have a queued action: \n{words[0]}\n\nThis has been replaced by Next action: {displayaction}", ephemeral=True)
        elif words[1] in players:
            await ctx.send(f"You already have a queued action: \n{words[0]} {players[words[1]]['Username']}\n\nThis has been replaced by Next action: {displayaction}", ephemeral=True)
        elif words[1] in locations:
            await ctx.send(f"You already have a queued action: \n{words[0]} {locations[words[1]]['Name']}\n\nThis has been replaced by Next action: {displayaction}", ephemeral=True)
    else:
        await ctx.send(f"Next action: {displayaction}", ephemeral=True)

    #write and dump the new playerdata
    #TODO combine this dump with into a single dump with the caller functions somehow
    players[ctx.author.id]["Nextaction"]=saveaction
    with open("players.json", "w") as f:
        json.dump(players, f, indent=4)

    return

async def queuenexttarget(ctx, actiontargetid):
    players = await getplayerdata()
    #separate strings for printing to player and what we use (id)
    saveaction = f"{ctx.data.name} {actiontargetid}"
    displayaction = ""
    if actiontargetid in players:
        displayaction = f"{ctx.data.name} {players[actiontargetid]['Username']}"
    #name here is a little misleading, but actiontargetid is actually the destination name in this context
    elif actiontargetid in locations:
        displayaction = saveaction

    if players[ctx.author.id]["Nextaction"] != "":
        words = players[ctx.author.id]['Nextaction'].split()
        if len(words) == 1:
            await ctx.send(f"You already have a queued action: {words[0]} \nThis has been replaced by Next action: {displayaction}", ephemeral=True)
        elif words[1] in players:
            await ctx.send(f"You already have a queued action: {words[0]} {players[words[1]]['Username']}\nThis has been replaced by Next action: {displayaction}", ephemeral = True)
        elif words[1] in locations:
            await ctx.send(f"You already have a queued action: {words[0]} {words[1]}\nThis has been replaced by Next action: {displayaction}", ephemeral = True)
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
    poison = await getpoisondata()
    if str(ctx.author.id) in players:
        print("player exists")
        await ctx.send(f"Failed to Join! {ctx.author} already exists as a player! ", ephemeral = True)
        return False
    elif  poison["firstpoisondate"] < int(time.time()) : #players who join late get reduced HP and SC
        print("player doesn't exist and first poison date has occurred")
        current_time = int(time.time())
        await ctx.author.add_role(locations["Crossroads"]["Role_ID"], guildid)
        await ctx.author.add_role(locations["Playing"]["Role_ID"], guildid)
        if str(ctx.author.id) in bounties:
            print("player exists in bounties")
            bounty_pull = bounties[str(ctx.author.id)]["Bounty"]
            await ctx.send(f"{ctx.author} has claimed prior bounties for {bounty_pull}!", ephemeral = True)
        else:
            print("player doesn't exists in bounties")
            bounty_pull = 0
        players[str(ctx.author.id)] = {}
        players[str(ctx.author.id)]["Username"] = str(ctx.author.user)
        players[str(ctx.author.id)]["Location"] = "Crossroads"
        players[str(ctx.author.id)]["HP"] = 10000
        players[str(ctx.author.id)]["SC"] = 10
        players[str(ctx.author.id)]["HP"] = min(10000,min(x["HP"] for x in players.values() if x["Location"] != "Dead")-1000)
        players[str(ctx.author.id)]["SC"] = min(10,min(x["SC"] for x in players.values() if x["Location"] != "Dead")-1) + bounty_pull
        players[str(ctx.author.id)]["Rage"] = 0
        players[str(ctx.author.id)]["ReadyInventory"] = ""
        players[str(ctx.author.id)]["UsedInventory"] = ""
        players[str(ctx.author.id)]["DelayDate"] = current_time
        players[str(ctx.author.id)]["Lastactiontime"] = int(time.time())
        players[str(ctx.author.id)]["Lastaction"] = "start"
        players[str(ctx.author.id)]["Nextaction"] = ""
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
        print(f"Created {ctx.author.id} player in players.json")
        players = await getplayerdata()
        hp_pull = players[str(ctx.author.id)]["HP"]
        location_pull = players[str(ctx.author.id)]["Location"]
        SC_pull = players[str(ctx.author.id)]["SC"]
        Rage_pull = players[str(ctx.author.id)]["Rage"]
        ReadyInventory_pull = players[str(ctx.author.id)]["ReadyInventory"]
        UsedInventory_pull = players[str(ctx.author.id)]["UsedInventory"]
        DelayDate_pull = players[str(ctx.author.id)]["DelayDate"]
        Lastaction_pull = players[str(ctx.author.id)]["Lastaction"]
        hpmoji = await hpmojiconv(hp_pull)
        playingroleid=locations["Playing"]["Role_ID"]
        row = interactions.ActionRow(
        components=[actionhelpbutton, locationhelpbutton, itemhelpbutton, Poisonhelpbutton, Ragehelpbutton ]
    )
        await ctx.send(f"{ctx.author}'s HP: {hpmoji} \nLocation: {location_pull} \nSC: {SC_pull} \nRage: {Rage_pull} \nInventory: \n    Ready: {ReadyInventory_pull} \n    Used:{UsedInventory_pull} \nCooldown: <t:{DelayDate_pull}>", ephemeral = True)
        await ctx.send(f"<@{ctx.author.id}> has entered the fray in the Crossroads!  \n\nThey may act immediately!! \n\nBeware <@&{playingroleid}>")
        await ctx.send(f"**Gameinfo buttons**:", components = row, ephemeral = True)
    else:
        print("player doesn't exist and first poison date has not occurred")
        current_time = int(time.time())
        await ctx.author.add_role(locations["Crossroads"]["Role_ID"], guildid)
        await ctx.author.add_role(locations["Playing"]["Role_ID"], guildid)
        if str(ctx.author.id) in bounties:
            print("player exists in bounties")
            bounty_pull = bounties[str(ctx.author.id)]["Bounty"]
            await ctx.send(f"{ctx.author} has claimed prior bounties for {bounty_pull}!", ephemeral = True)
        else:
            print("player doesn't exists in bounties")
            bounty_pull = 0
        players = await getplayerdata()
        players[str(ctx.author.id)] = {}
        players[str(ctx.author.id)]["Username"] = str(ctx.author.user)
        players[str(ctx.author.id)]["HP"] = 10000
        players[str(ctx.author.id)]["Location"] = "Crossroads"
        players[str(ctx.author.id)]["SC"] = 10 + bounty_pull
        players[str(ctx.author.id)]["Rage"] = 0
        players[str(ctx.author.id)]["ReadyInventory"] = ""
        players[str(ctx.author.id)]["UsedInventory"] = ""
        players[str(ctx.author.id)]["DelayDate"] = current_time
        players[str(ctx.author.id)]["Lastactiontime"] = current_time
        players[str(ctx.author.id)]["Lastaction"] = "start"
        players[str(ctx.author.id)]["Nextaction"] = ""
        print("writing to players.json")
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
        print(f"Created {ctx.author.id} player in players.json")
        hp_pull = players[str(ctx.author.id)]["HP"]
        hpmoji = await hpmojiconv(hp_pull)
        location_pull = players[str(ctx.author.id)]["Location"]
        SC_pull = players[str(ctx.author.id)]["SC"]
        Rage_pull = players[str(ctx.author.id)]["Rage"]
        ReadyInventory_pull = players[str(ctx.author.id)]["ReadyInventory"]
        UsedInventory_pull = players[str(ctx.author.id)]["UsedInventory"]
        DelayDate_pull = players[str(ctx.author.id)]["DelayDate"]
        Lastaction_pull = players[str(ctx.author.id)]["Lastaction"]
        playingroleid=locations["Playing"]["Role_ID"]
        row = interactions.ActionRow(
        components=[actionhelpbutton, locationhelpbutton, itemhelpbutton, Poisonhelpbutton, Ragehelpbutton ]
    )
        await ctx.send(f"{ctx.author}'s HP: {hpmoji} \nLocation: {location_pull} \nSC: {SC_pull} \nRage: {Rage_pull} \nInventory: \n    Ready: {ReadyInventory_pull} \n    Used:{UsedInventory_pull} \nCooldown: <t:{DelayDate_pull}>", ephemeral = True)
        await ctx.send(f"<@{ctx.author.id}> has entered the fray in the Crossroads! \n\nThey may act immediately!! \n\nBeware <@&{playingroleid}>")
        await ctx.send(f"**Gameinfo buttons**:", components = row, ephemeral = True)

#light attack is below
async def dolightattack(authorid,targetid,channelid):
    players = await getplayerdata()
    current_time = int(time.time())
    if players[str(targetid)]["Lastaction"] == "evade" and players[str(targetid)]["Lastactiontime"]+basecd<current_time:
        await rage(authorid)
        players = await getplayerdata()
        damage = 0
        targethp = players[str(targetid)]["HP"] - damage
        players[str(targetid)]["HP"] = targethp
        players[str(authorid)]["Rage"] = players[str(authorid)]["Rage"] +1
        cooldown = basecd  # seconds in a day
        players[str(authorid)]["DelayDate"] = current_time + cooldown
        DelayDate_pull = current_time + cooldown
        players[str(authorid)]["Lastaction"] = "lightattack"
        await lastactiontime(authorid)
        hpmoji = await hpmojiconv(targethp)
        with open("players.json", "w") as f:
            json.dump(players, f, indent=4)
        await send_message(f"<@{targetid}> evaded a light attack from <@{authorid}>! \nNew HP: {hpmoji} ", user_id=[authorid,targetid])
        await send_message(f"<@{authorid}> used a light attack on <@{targetid}>! \n<@{authorid}> is on cooldown until <t:{DelayDate_pull}>", channel_id=[channelid])
    else:
        await rage(authorid)
        players = await getplayerdata()
        UsedInventory_pull = players[str(authorid)]["UsedInventory"]
        damage = 950 + (UsedInventory_pull.count("drinkingmedal") * 420)
        targethp = players[str(targetid)]["HP"] - damage
        players[str(targetid)]["HP"] = targethp
        await deadcheck(targethp,targetid,authorid,players)
        players[str(authorid)]["Rage"] = players[str(authorid)]["Rage"] +1
        cooldown = basecd  # seconds in a day
        players[str(authorid)]["DelayDate"] = current_time + cooldown
        DelayDate_pull = current_time + cooldown
        players[str(authorid)]["Lastaction"] = "lightattack"
        await lastactiontime(authorid)
        hpmoji = await hpmojiconv(targethp)
        with open("players.json", "w") as f:
            json.dump(players, f, indent=4)
        await send_message(f"<@{targetid}> was hit by a light attack by <@{authorid}>! \nNew HP: {hpmoji} ", user_id=[authorid,targetid])
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
    channelid=ctx.channel_id
    if str(ctx.author.id) in players:
        DelayDate_pull = players[str(ctx.author.id)]["DelayDate"]
        if DelayDate_pull > current_time:
            await queuenexttarget(ctx,targetid,)
            await ctx.send(f"You cannot act yet! You are delayed until <t:{DelayDate_pull}>.", ephemeral = True) #golive
        else:
            await ctx.send(f"You light attack!",ephemeral=True)
            await dolightattack(ctx.author.id,targetid,channelid)
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
    if players[str(targetid)]["Lastaction"] == "evade" and players[str(targetid)]["Lastactiontime"]+basecd<current_time:
        await rage(authorid)
        players = await getplayerdata()
        damage = 0
        targethp = players[str(targetid)]["HP"] - damage
        players[str(targetid)]["HP"] = targethp
        players[str(authorid)]["Rage"] = players[str(authorid)]["Rage"] +3
        cooldown = basecd*2  # seconds in a day
        players[str(authorid)]["DelayDate"] = current_time + cooldown
        DelayDate_pull = current_time + cooldown
        players[str(authorid)]["Lastaction"] = "normalattack"
        await lastactiontime(authorid)
        hpmoji = await hpmojiconv(targethp)
        with open("players.json", "w") as f:
            json.dump(players, f, indent=4)
        await send_message(f"<@{targetid}> evaded a normal attack from <@{authorid}>! \nNew HP: {hpmoji} ", user_id=[authorid,targetid])
        await send_message(f"<@{authorid}> used a normal attack on <@{targetid}>! \n<@{authorid}> is on cooldown until <t:{DelayDate_pull}>", channel_id=[channelid])
    else:
        await rage(authorid)
        players = await getplayerdata()
        UsedInventory_pull = players[str(authorid)]["UsedInventory"]
        damage = 950 + (UsedInventory_pull.count("drinkingmedal") * 420)
        targethp = players[str(targetid)]["HP"] - damage
        players[str(targetid)]["HP"] = targethp
        await deadcheck(targethp,targetid,authorid,players)
        players[str(authorid)]["Rage"] = players[str(authorid)]["Rage"] +3
        cooldown = basecd  # seconds in a day
        players[str(authorid)]["DelayDate"] = current_time + cooldown
        DelayDate_pull = current_time + cooldown
        players[str(authorid)]["Lastaction"] = "normalattack"
        await lastactiontime(authorid)
        hpmoji = await hpmojiconv(targethp)
        with open("players.json", "w") as f:
            json.dump(players, f, indent=4)
        await send_message(f"<@{targetid}> was hit by a normal attack by <@{authorid}>! \nNew HP: {hpmoji} ", user_id=[authorid,targetid])
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
    current_time = int(time.time())
    print(f"{playertarget} is the player target")
    for k, v in players.items():
        if v['Username'] == str(playertarget):
            targetid = k
    print(f"{targetid} is the player target id")
    channelid=ctx.channel_id
    if str(ctx.author.id) in players:
        DelayDate_pull = players[str(ctx.author.id)]["DelayDate"]
        if DelayDate_pull > current_time:
            await queuenexttarget(ctx, targetid )
            await ctx.send(f"You cannot act yet! You are delayed until <t:{DelayDate_pull}>.", ephemeral=True)  # golive
        else:
            await ctx.send(f"You normal attack!",ephemeral=True)
            await donormalattack(ctx.author.id, targetid, channelid)
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
    if players[str(targetid)]["Lastaction"] == "evade" and players[str(targetid)]["Lastactiontime"]+basecd<current_time:
        await rage(authorid)
        players = await getplayerdata()
        damage = 0
        targethp = players[str(targetid)]["HP"] - damage
        players[str(targetid)]["HP"] = targethp
        players[str(authorid)]["Rage"] = players[str(authorid)]["Rage"] +6
        cooldown = max((basecd*3) - (UsedInventory_pull.count("aimtraining")*2*basecd),basecd)  # seconds in a day
        players[str(authorid)]["DelayDate"] = current_time + cooldown
        DelayDate_pull = current_time + cooldown
        players[str(authorid)]["Lastaction"] = "heavyattack"
        await lastactiontime(authorid)
        hpmoji = await hpmojiconv(targethp)
        with open("players.json", "w") as f:
            json.dump(players, f, indent=4)
        await send_message(f"<@{targetid}> evaded a heavy attack from <@{authorid}>! \nNew HP: {hpmoji} ", user_id=[authorid,targetid])
        await send_message(f"<@{authorid}> used a heavy attack on <@{targetid}>! \n<@{authorid}> is on cooldown until <t:{DelayDate_pull}>", channel_id=[channelid])
    else:
        await rage(authorid)
        players = await getplayerdata()
        UsedInventory_pull = players[str(authorid)]["UsedInventory"]
        damage = 950 + (UsedInventory_pull.count("drinkingmedal") * 420)
        targethp = players[str(targetid)]["HP"] - damage
        players[str(targetid)]["HP"] = targethp
        await deadcheck(targethp,targetid,authorid,players)
        players[str(authorid)]["Rage"] = players[str(authorid)]["Rage"] +6
        cooldown = max((basecd*3) - (UsedInventory_pull.count("aimtraining")*2*basecd),basecd)  # seconds in a day
        players[str(authorid)]["DelayDate"] = current_time + cooldown
        DelayDate_pull = current_time + cooldown
        players[str(authorid)]["Lastaction"] = "heavyattack"
        await lastactiontime(authorid)
        hpmoji = await hpmojiconv(targethp)
        with open("players.json", "w") as f:
            json.dump(players, f, indent=4)
        await send_message(f"<@{targetid}> was hit by a heavy attack by <@{authorid}>! \nNew HP: {hpmoji} ", user_id=[authorid,targetid])
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
    current_time = int(time.time())
    print(f"{playertarget} is the player target")
    for k, v in players.items():
        if v['Username'] == str(playertarget):
            targetid = k
    print(f"{targetid} is the player target id")
    channelid=ctx.channel_id
    if str(ctx.author.id) in players:
        DelayDate_pull = players[str(ctx.author.id)]["DelayDate"]
        if DelayDate_pull > current_time:
            await queuenexttarget(ctx, targetid )
            await ctx.send(f"You cannot act yet! You are delayed until <t:{DelayDate_pull}>.", ephemeral=True)  # golive
        else:
            await ctx.send(f"You heavy attack!",ephemeral=True)
            await doheavyattack(ctx.author.id, targetid, channelid)
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

#interrupt is below
async def dointerrupt(authorid,targetid,channelid):
    players = await getplayerdata()
    current_time = int(time.time())
    if (players[str(targetid)]["Lastaction"] == "evade" or players[str(targetid)]["Lastaction"] == "rest") and players[str(targetid)]["Lastactiontime"]+basecd<current_time:
        await rage(authorid)
        players = await getplayerdata()
        targethp = players[str(targetid)]["HP"] - 4200
        players[str(targetid)]["HP"] = targethp
        await deadcheck(targethp,targetid,authorid,players)
        cooldown = basecd * 1  # seconds in one day
        players[str(authorid)]["DelayDate"] = current_time + cooldown
        DelayDate_pull = current_time + cooldown
        players[str(authorid)]["Lastaction"] = "interrupt"
        await lastactiontime(authorid)
        hpmoji = await hpmojiconv(targethp)
        with open("players.json", "w") as f:
            json.dump(players, f, indent=4)
        await send_message(f"<@{targetid}> was hit and damaged by an interrupt by <@{authorid}>! \nNew HP: {hpmoji} ", user_id=[authorid,targetid])
        await send_message(f"<@{authorid}> used an interrupt on <@{targetid}>! \n<@{authorid}> is on cooldown until <t:{DelayDate_pull}>",channel_id=channelid)
    else:
        await rage(authorid)
        players = await getplayerdata()
        cooldown = basecd * 1  # seconds in one day
        players[str(authorid)]["DelayDate"] = current_time + cooldown
        DelayDate_pull = current_time + cooldown
        players[str(authorid)]["Lastaction"] = "interrupt"
        await lastactiontime(authorid)
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
    current_time = int(time.time())
    print(f"{playertarget} is the player target")
    for k, v in players.items():
        if v['Username'] == str(playertarget):
            targetid = k
    print(f"{targetid} is the player target id")
    channelid=ctx.channel_id
    if str(ctx.author.id) in players:
        DelayDate_pull = players[str(ctx.author.id)]["DelayDate"]
        if DelayDate_pull > current_time:
            await queuenexttarget(ctx, targetid )
            await ctx.send(f"You cannot act yet! You are delayed until <t:{DelayDate_pull}>.", ephemeral=True)  # golive
        else:
            await ctx.send(f"You interrupt!",ephemeral=True)
            await dointerrupt(ctx.author.id, targetid, channelid)
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
async def doevade(authorid,channelid):
    await rage(authorid)
    players = await getplayerdata()
    players = await getplayerdata()
    players[str(authorid)]["Evade"] = True
    cooldown = int(basecd * 1)  # seconds in one days
    current_time = int(time.time())
    players[str(authorid)]["DelayDate"] = current_time + cooldown
    players[str(authorid)]["Lastaction"] = "evade"
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
    channelid=ctx.channel_id
    if str(ctx.author.id) in players:
        DelayDate_pull = players[str(ctx.author.id)]["DelayDate"]
        current_time = int(time.time())
        if DelayDate_pull > current_time:
            await queuenext(ctx)
            await ctx.send(f"You cannot act yet! You are delayed until <t:{DelayDate_pull}>.", ephemeral = True)
        else:
            await ctx.send(f"You evade!",ephemeral=True)
            await doevade(ctx.author.id,channelid)
    else:
        await ctx.send(f"You need to join with /join before you can do that!" , ephemeral = True)

#rest is below
async def dorest(authorid,channelid):
    await rage(authorid)
    players = await getplayerdata()
    players = await getplayerdata()
    hp_pull = players[str(authorid)]["HP"]
    heal = math.ceil(int((10000 - hp_pull) / 2))
    cooldown = int(basecd * 1)  # seconds in one day
    current_time = int(time.time())
    players[str(authorid)]["DelayDate"] = current_time + cooldown
    players[str(authorid)]["Lastaction"] = "rest"
    DelayDate_pull = players[str(authorid)]["DelayDate"]
    players[str(authorid)]["HP"] = min(players[str(authorid)]["HP"] + heal, 10000)
    hpmoji = await hpmojiconv(players[str(authorid)]["HP"])
    with open("players.json", "w") as f:
        json.dump(players, f, indent=4)
    await send_message(f"<@{authorid}> used rest! \n<@{authorid}> is on cooldown until <t:{DelayDate_pull}> \nNew Hp: {hpmoji}", user_id=[authorid])

@bot.command(
    name="rest",
    description="24h. heal half your missing health rounded up unless you rested last action.",
    scope=guildid,
)
async def rest_command(ctx: interactions.CommandContext):
    players = await getplayerdata()
    channelid=ctx.channel_id
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
            await ctx.send(f"You rest!",ephemeral=True)
            await dorest(ctx.author.id,channelid)
    else:
        await ctx.send(f"You need to join with /join before you can do that!" , ephemeral = True)

#travelto
async def dotravelto(authorid,destination):
    await rage(authorid)
    players = await getplayerdata()
    players = await getplayerdata()
    current_time = int(time.time())
    cooldown = basecd * 1  # seconds in one day
    players[str(authorid)]["DelayDate"] = current_time + cooldown
    DelayDate_pull = current_time + cooldown
    players[str(authorid)]["Lastaction"] = "travelto"
    players[str(authorid)]["Location"] = destination
    await lastactiontime(authorid)
    with open("players.json", "w") as f:
        json.dump(players, f, indent=4)
    user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
    await user.remove_role(role=locations["Crossroads"]["Role_ID"], guild_id=guildid)
    await user.add_role(role=locations[destination]["Role_ID"], guild_id=guildid)
    await send_message(f"<@{authorid}> traveled to {destination}! \n<@{authorid}> is on cooldown until <t:{DelayDate_pull}>",user_id=[authorid],channel_id=[locations[destination]["Channel_ID"]])

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
    players = await getplayerdata()
    current_time = int(time.time())
    print(f"{destination} is the destination")
    channelid=ctx.channel_id
    if str(ctx.author.id) in players:
        DelayDate_pull = players[str(ctx.author.id)]["DelayDate"]
        if DelayDate_pull > current_time:
            await queuenexttarget(ctx,destination)
            await ctx.send(f"You cannot act yet! You are delayed until <t:{DelayDate_pull}>.", ephemeral = True) #golive
        else:
            await ctx.send(f"You travel!",ephemeral=True)
            await dotravelto(ctx.author.id,destination)
    else:
        await ctx.send(f"You need to join with /join before you can do that!" , ephemeral = True)


@bot.autocomplete("travelto", "destination")
async def travelto_autocomplete(ctx: interactions.CommandContext, value: str = ""):
    sameLocationUsernames = [k for k in locations.keys()]
    print (sameLocationUsernames)
    items = filter(lambda x: x!="Dead",sameLocationUsernames)
    items = filter(lambda x: x!="Playing",items)
    choices = [
        interactions.Choice(name=item, value=item) for item in items if value in item
    ]
    await ctx.populate(choices)

#travelto
async def dotraveltocrossroads(authorid):
    await rage(authorid)
    players = await getplayerdata()
    players = await getplayerdata()
    current_time = int(time.time())
    cooldown = basecd * 1  # seconds in one day
    players[str(authorid)]["DelayDate"] = current_time + cooldown
    DelayDate_pull = current_time + cooldown
    players[str(authorid)]["Lastaction"] = "travelto"
    await lastactiontime(authorid)
    players[str(authorid)]["Location"] = "Crossroads"
    with open("players.json", "w") as f:
        json.dump(players, f, indent=4)
    user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
    await user.remove_role(role=locations["Dungeon"]["Role_ID"], guild_id=guildid)
    await user.remove_role(role=locations["Farmland"]["Role_ID"], guild_id=guildid)
    await user.remove_role(role=locations["Keep"]["Role_ID"], guild_id=guildid)
    await user.remove_role(role=locations["Lich's Castle"]["Role_ID"], guild_id=guildid)
    await user.remove_role(role=locations["Shop"]["Role_ID"], guild_id=guildid)
    await user.remove_role(role=locations["Tavern"]["Role_ID"], guild_id=guildid)
    await user.add_role(role=locations["Crossroads"]["Role_ID"], guild_id=guildid)
    await send_message(f"<@{authorid}> traveled to the Crossroads! \n<@{authorid}> is on cooldown until <t:{DelayDate_pull}>",user_id=[authorid])
    await send_message(f"<@{authorid}> traveled to the Crossroads! \n<@{authorid}> is on cooldown until <t:{DelayDate_pull}>",user_id=[authorid],channel_id=[locations["Crossroads"]["Channel_ID"]])

@bot.command(
    name="traveltocrossroads",
    description="24h. travel to the crossroads from any location.",
    scope = guildid ,
)
async def traveltocrossroads(ctx: interactions.CommandContext):
    players = await getplayerdata()
    current_time = int(time.time())
    channelid=ctx.channel_id
    if str(ctx.author.id) in players:
        DelayDate_pull = players[str(ctx.author.id)]["DelayDate"]
        if DelayDate_pull > current_time:
            await queuenext(ctx)
            await ctx.send(f"You cannot act yet! You are delayed until <t:{DelayDate_pull}>.", ephemeral = True) #golive
        else:
            await ctx.send(f"You travel!",ephemeral=True)
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
    location_pull = players[str(ctx.author.id)]["Location"]
    SC_pull = players[str(ctx.author.id)]["SC"]
    Rage_pull = players[str(ctx.author.id)]["Rage"]
    ReadyInventory_pull = players[str(ctx.author.id)]["ReadyInventory"]
    UsedInventory_pull = players[str(ctx.author.id)]["UsedInventory"]
    DelayDate_pull = players[str(ctx.author.id)]["DelayDate"]
    Lastaction_pull = players[str(ctx.author.id)]["Lastaction"]
    Nextaction_pull = players[str(ctx.author.id)]["Nextaction"]
    hpmoji = await hpmojiconv(hp_pull)
    await ctx.send(f"**{ctx.author}'s HP:** {hpmoji} \n**Location:** {location_pull} \n**SC:** {SC_pull} \n**Rage:** {Rage_pull} \n**Inventory:** \n    **Ready:** {ReadyInventory_pull} \n    **Used:**{UsedInventory_pull} \n**Cooldown:** <t:{DelayDate_pull}>\n**Nextaction:** {Nextaction_pull}", ephemeral = True)

#exchange is below
async def doexchange(authorid, playertarget, readyitem, channelid):
    await rage(authorid)
    players = await getplayerdata()
    current_time = int(time.time())
    print(f"{playertarget} is the player target")
    print(f"{readyitem} is the item target")
    for k,v in players.items():
        if v['Username']==str(playertarget):
            targetid=k
    print(f"{targetid} is the player target id")
    ReadyInventory_pull = str(players[str(authorid)]["ReadyInventory"])
    cooldown=basecd*1 #seconds in one day
    players[str(authorid)]["DelayDate"] = current_time+cooldown
    DelayDate_pull=current_time+cooldown
    players[str(authorid)]["Lastaction"] = "exchange"
    players[str(authorid)]["SC"] = players[str(authorid)]["SC"] + (UsedInventory_pull.count("crookedabacus") * 1)
    await lastactiontime(authorid)
    players[str(targetid)]["ReadyInventory"] = players[str(targetid)]["ReadyInventory"]  + "\n        " + readyitem
    ReadyInventory_pull = str(players[str(authorid)]["ReadyInventory"])
    ReadyInventory_pull = ReadyInventory_pull.replace(str("\n        " +readyitem), "",1)
    players[str(authorid)]["ReadyInventory"] = ReadyInventory_pull
    with open("players.json","w") as f:
        json.dump(players,f, indent=4)
    await send_message(f"<@{targetid}> was given {readyitem} from <@{authorid}>!", user_id=authorid)
    await send_message(f"<@{targetid}> was given {readyitem} from <@{authorid}>!", user_id=targetid)
    await send_message(f"<@{authorid}> gave an item to <@{targetid}>! \n<@{authorid}> is on cooldown until <t:{DelayDate_pull}>", channel_id=[channelid], ephemeral=False)


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
    current_time = int(time.time())
    channelid=ctx.channel_id
    authorid=ctx.author.id
    if str(authorid) in players:
        DelayDate_pull = players[str(authorid)]["DelayDate"]
        ReadyInventory_pull = str(players[str(ctx.author.id)]["ReadyInventory"])
        if locations["Crossroads"]["Role_ID"] not in ctx.author.roles:
            await ctx.send(f"You cannot exchange when you are not in the crossroads!", ephemeral=True)  # golive
        elif ReadyInventory_pull=="":
            await ctx.send(f"You don't have any items in your Ready Inventory!", ephemeral = True)
        elif DelayDate_pull > current_time:
            await queuenext(ctx)
            await ctx.send(f"You cannot act yet! You are delayed until <t:{DelayDate_pull}>.", ephemeral = True) #golive
        else:
            await ctx.send(f"You exchange!",ephemeral=True)
            await doexchange(ctx.author.id, playertarget,readyitem,channelid)
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
    await rage(authorid)
    players = await getplayerdata()
    current_time = int(time.time())
    UsedInventory_pull=players[str(authorid)]["UsedInventory"]
    Lastaction_pull=players[str(authorid)]["Lastaction"]
    farmSC = int(random.randint(0, 4)) + (UsedInventory_pull.count("tractor") * 1) + (Lastaction_pull.count("farm") * 1)
    SC_pull = players[str(authorid)]["SC"] + farmSC  # +randbuff
    cooldown = basecd * 1  # seconds in one day
    players[str(authorid)]["SC"] = SC_pull
    players[str(authorid)]["DelayDate"] = current_time + cooldown
    DelayDate_pull = current_time + cooldown
    players[str(authorid)]["Lastaction"] = "farm"
    await lastactiontime(authorid)
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
    channelid=ctx.channel_id
    authorid=ctx.author.id
    if str(authorid) in players:
        DelayDate_pull = players[str(authorid)]["DelayDate"]
        if locations["Farmland"]["Role_ID"] not in ctx.author.roles:
            await ctx.send(f"You cannot farm when you are not in the farmland!", ephemeral=True)  # golive
        elif DelayDate_pull > current_time:
            await queuenext(ctx)
            await ctx.send(f"You cannot act yet! You are delayed until <t:{DelayDate_pull}>.", ephemeral = True) #golive
        else:
            await ctx.send(f"You farm!",ephemeral=True)
            await dofarm(ctx.author.id,channelid)
    else:
        await ctx.send(f"You need to join with /join before you can do that!" , ephemeral = True)

#aid is below

async def doaid(authorid, playertarget,channelid):
    await rage(authorid)
    players = await getplayerdata()
    current_time = int(time.time())
    print(f"{playertarget} is the player target")
    for k,v in players.items():
        if v['Username']==str(playertarget):
            targetid=k
    print(f"{targetid} is the player target id")
    targethp=players[str(targetid)]["HP"]
    heal = min(math.ceil(int((10000 - targethp)/4)),10000)
    cooldown=basecd*1 #seconds in one day
    players[str(authorid)]["DelayDate"] = current_time+cooldown
    DelayDate_pull=current_time+cooldown
    players[str(authorid)]["Lastaction"] = "aid"
    await lastactiontime(authorid)
    players[str(targetid)]["HP"] = players[str(targetid)]["HP"] + heal
    targethp=players[str(targetid)]["HP"]
    hpmoji = await hpmojiconv(targethp)
    with open("players.json","w") as f:
        json.dump(players,f, indent=4)
    await send_message(f"<@{targetid}> was healed by aid from <@{authorid}>! \nNew HP: {hpmoji} ", channel_id=[channelid])
    await send_message(f"<@{authorid}> used aid on <@{targetid}> to heal them! \n<@{authorid}> is on cooldown until <t:{DelayDate_pull}>", channel_id=[channelid])


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
    current_time = int(time.time())
    channelid=ctx.channel_id
    authorid=ctx.author.id
    if str(ctx.author.id) in players:
        DelayDate_pull = players[str(authorid)]["DelayDate"]
        if locations["Keep"]["Role_ID"] not in ctx.author.roles:
            await ctx.send(f"You cannot aid when you are not in the keep!", ephemeral=True)  # golive
        elif DelayDate_pull > current_time:
            await queuenext(ctx)
            await ctx.send(f"You cannot act yet! You are delayed until <t:{DelayDate_pull}>.", ephemeral = True) #golive
        else:
            await ctx.send(f"You aid!",ephemeral=True)
            await doaid(ctx.author.id, playertarget,channelid)
    else:
        await ctx.send(f"You need to join with /join before you can do that!" , ephemeral = True)

@bot.autocomplete("aid", "playertarget")
async def aid_autocomplete(ctx: interactions.CommandContext, value: str = ""):
    players = await getplayerdata()
    Usernames = [v["Username"] for v in players.values() if v['Location'] != "Dead"]
    print (Usernames)
    items = Usernames
    choices = [
        interactions.Choice(name=item, value=item) for item in items if value in item
    ]
    await ctx.populate(choices)

#trade is below

async def dotrade(authorid, itemtarget,channelid):
    await rage(authorid)
    players = await getplayerdata()
    shop = await getshopdata()
    current_time = int(time.time())
    print(f"{itemtarget} is the player target")
    cooldown=basecd*1 #seconds in one day
    players[str(authorid)]["DelayDate"] = current_time+cooldown
    DelayDate_pull=current_time+cooldown
    players[str(authorid)]["Lastaction"] = "trade"
    #spend SC and gain abacus money
    UsedInventory_pull = players[str(authorid)]["UsedInventory"]
    cost = shop[str(itemtarget)]["Cost"]
    players[str(authorid)]["SC"] = players[str(authorid)]["SC"] - cost + (UsedInventory_pull.count("crookedabacus") * 1)
    #add item to inventory
    players[str(authorid)]["ReadyInventory"] = players[str(authorid)]["ReadyInventory"] + "\n        "+itemtarget
    await lastactiontime(authorid)
    with open("players.json","w") as f:
        json.dump(players,f, indent=4)
    await send_message(f"One {itemtarget} was purchased by <@{authorid}> from the shop!", channel_id=[channelid])
    await send_message(f"<@{authorid}> purchased an item from the shop! \n<@{authorid}> is on cooldown until <t:{DelayDate_pull}>", channel_id=[channelid])


@bot.command(
    name="trade",
    description="24h. exchange seed coins for a shop item.",
    scope = guildid ,
    options=[
        interactions.Option(
            type=interactions.OptionType.STRING,
            name="itemtarget",
            description="what you want to buy",
            required=True,
            autocomplete=True,
        )
    ]
)
async def trade(ctx: interactions.CommandContext, itemtarget: str):
    players = await getplayerdata()
    shop = await getshopdata()
    current_time = int(time.time())
    channelid=ctx.channel_id
    authorid=ctx.author.id
    SC_pull=players[str(authorid)]["SC"]
    cost = shop[str(itemtarget)]["Cost"]
    if str(ctx.author.id) in players:
        DelayDate_pull = players[str(authorid)]["DelayDate"]
        if locations["Shop"]["Role_ID"] not in ctx.author.roles:
            await ctx.send(f"You cannot trade when you are not in the Shop!", ephemeral=True)  # golive
        elif players[str(authorid)]["SC"] <= shop[str(itemtarget)]["Cost"]:
            await ctx.send(f"Your {SC_pull} seed coins are not able to purchase an item that costs {cost} seed coins! ", ephemeral = True)
        elif DelayDate_pull > current_time:
            await queuenext(ctx)
            await ctx.send(f"You cannot act yet! You are delayed until <t:{DelayDate_pull}>.", ephemeral = True) #golive
        else:
            await ctx.send(f"You trade!",ephemeral=True)
            await dotrade(ctx.author.id, itemtarget,channelid)
    else:
        await ctx.send(f"You need to join with /join before you can do that!" , ephemeral = True)

@bot.autocomplete("trade", "itemtarget")
async def trade_autocomplete(ctx: interactions.CommandContext, value: str = ""):
    print("tradetest")
    shop = await getshopdata()
    itemnames = [v for v in shop.keys()]
    print (itemnames)
    items = itemnames
    choices = [
        interactions.Choice(name=item, value=item) for item in items if value in item
    ]
    await ctx.populate(choices)

#drinkingchallenge is below

async def dodrinkingchallenge(authorid):
    await rage(authorid)
    players = await getplayerdata()
    scores = await gettaverndata()
    Lastaction_pull = players[str(authorid)]["Lastaction"]
    playerroll = int(int(random.randint(1,4)) + (Lastaction_pull.count("drinkingchallenge") * 1))
    print(f"playerroll = {playerroll}")
    print(f"scores = \n{scores}\n")
    current_time = int(time.time())
    cooldown=basecd*1 #seconds in one day
    players[str(authorid)]["DelayDate"] = current_time+cooldown
    DelayDate_pull=current_time+cooldown
    players[str(authorid)]["Lastaction"] = "drinkingchallenge"
    with open("players.json","w") as f:
        json.dump(players,f, indent=4)
    if scores[str("NPC4")]["Scoreexpiry"] > current_time :
        highscore= max(x["Score"] for x in scores.values() if x["Scoreexpiry"] > current_time)
        lowscore= min(x["Score"] for x in scores.values() if x["Scoreexpiry"] > current_time)
        print("NPC4 score is not expired, and has not been rewritten")
        print(f"highscore is {highscore}")
        print(f"lowscore is {lowscore}")
    else:
        scores[str("NPC4")]["Score"] = int(random.randint(1,4)-1)
        scores[str("NPC4")]["Scoreexpiry"] = current_time +cooldown
        print("NPC4 score is expired, and has been rewritten")
        highscore= max(x["Score"] for x in scores.values() if x["Scoreexpiry"] > current_time)
        lowscore= min(x["Score"] for x in scores.values() if x["Scoreexpiry"] > current_time)
        print(f"highscore is {highscore}")
        print(f"lowscore is {lowscore}")
    if scores[str("NPC3")]["Scoreexpiry"] > current_time:
        highscore= max(x["Score"] for x in scores.values() if x["Scoreexpiry"] > current_time)
        lowscore= min(x["Score"] for x in scores.values() if x["Scoreexpiry"] > current_time)
        print("NPC3 score is not expired, and has not been rewritten")
        print(f"highscore is {highscore}")
        print(f"lowscore is {lowscore}")
    else:
        scores[str("NPC3")]["Score"] = int(random.randint(1,4)-1)
        scores[str("NPC3")]["Scoreexpiry"] = current_time +cooldown
        print("NPC3 score is expired, and has been rewritten")
        highscore= max(x["Score"] for x in scores.values() if x["Scoreexpiry"] > current_time)
        lowscore= min(x["Score"] for x in scores.values() if x["Scoreexpiry"] > current_time)
        print(f"highscore is {highscore}")
        print(f"lowscore is {lowscore}")
    scores[str(authorid)] = {}
    scores[str(authorid)]["Username"] = players[str(authorid)]["Username"]
    scores[str(authorid)]["Media"] = ""
    scores[str(authorid)]["Score"] = playerroll
    scores[str(authorid)]["Scoreexpiry"] = current_time+cooldown
    with open("tavern.json","w") as t:
        json.dump(scores,t, indent=4)
    print("Player Tavern Score Saved")
    #check if the max is greater than the player's roll
    if highscore > playerroll:
        print(f"playerscore is lower than highscore")
        await send_message(f"<@{authorid}>'s roll of {playerroll} failed to beat the high score of {highscore}" , channel_id=[locations["Tavern"]["Channel_ID"]])
    else:
        print(f"playerscore is the highscore")
        await send_message(f"<@{authorid}>'s roll of {playerroll} beat the high score of {highscore} and got the drinkingmedal." , channel_id=[locations["Tavern"]["Channel_ID"]])
        players[str(authorid)]["UsedInventory"]=players[str(authorid)]["UsedInventory"] + "\n        "+"drinkingmedal"
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
    if lowscore == playerroll: #check if the min is equal to the player's roll
        print(f"lowscore is equal to playerscore")
        hp_pull = players[str(authorid)]["HP"]
        hp_pull=max(hp_pull - math.ceil(hp_pull/4),0)
        hpmoji = await hpmojiconv(hp_pull)
        await send_message(f"<@{authorid}> your roll of {playerroll} is the lowest roll. \nNew HP: {hpmoji}" , user_id=[authorid] )
        await send_message(f"<@{authorid}>'s roll of {playerroll} is the lowest roll and they lose 1/4 of their current health!" , channel_id=[locations["Tavern"]["Channel_ID"]] )
        players[str(authorid)]["HP"] = hp_pull
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
    else :
        print(f"lowscore is not equal to playerscore")
        hp_pull = players[str(authorid)]["HP"]
        hp_pull=min(hp_pull+math.ceil((10000-hp_pull)/4),10000)
        hpmoji = await hpmojiconv(hp_pull)
        await send_message(f"<@{authorid}> your roll of {playerroll} is not the low roll. \nNew HP: {hpmoji}" , user_id=[authorid] )
        await send_message(f"<@{authorid}>'s roll of {playerroll} is not the low roll. They heal for 1/4 of their missing health!" , channel_id=[locations["Tavern"]["Channel_ID"]])
        players[str(authorid)]["HP"] = hp_pull
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
    with open("players.json","w") as f:
        json.dump(players,f, indent=4)

@bot.command(
    name="drinkingchallenge",
    description="24h.score 1d4.high:gain drinkingmedal. heal 1/4 missing hp except low score loses 1/4hp.",
    scope = guildid ,
)
async def drinkingchallenge(ctx: interactions.CommandContext):
    players = await getplayerdata()
    current_time = int(time.time())
    channelid=ctx.channel_id
    if str(ctx.author.id) in players:
        DelayDate_pull = players[str(ctx.author.id)]["DelayDate"]
        if locations["Tavern"]["Role_ID"] not in ctx.author.roles:
            await ctx.send(f"You cannot drinkingchallenge when you are not in the tavern!", ephemeral=True)  # golive
        elif DelayDate_pull > current_time:
            await queuenext(ctx)
            await ctx.send(f"You cannot act yet! You are delayed until <t:{DelayDate_pull}>.", ephemeral = True) #golive
        else:
            await ctx.send(f"You drink!",ephemeral=True)
            await dodrinkingchallenge(ctx.author.id)
    else:
        await ctx.send(f"You need to join with /join before you can do that!" , ephemeral = True)

#loot is below

async def doloot(authorid):
    await rage(authorid)
    players = await getplayerdata()
    scores = await getdungeondata()
    Lastaction_pull = players[str(authorid)]["Lastaction"]
    playerroll = int(int(random.randint(1,4)) + (Lastaction_pull.count("loot") * 1))
    print(f"playerroll = {playerroll}")
    print(f"scores = \n{scores}\n")
    current_time = int(time.time())
    cooldown=basecd*1 #seconds in one day
    players[str(authorid)]["DelayDate"] = current_time+cooldown
    DelayDate_pull=current_time+cooldown
    players[str(authorid)]["Lastaction"] = "loot"
    with open("players.json","w") as f:
        json.dump(players,f, indent=4)
    if scores[str("NPC4")]["Scoreexpiry"] > current_time :
        highscore= max(x["Score"] for x in scores.values() if x["Scoreexpiry"] > current_time)
        lowscore= min(x["Score"] for x in scores.values() if x["Scoreexpiry"] > current_time)
        print("NPC4 score is not expired, and has not been rewritten")
        print(f"highscore is {highscore}")
        print(f"lowscore is {lowscore}")
    else:
        scores[str("NPC4")]["Score"] = int(random.randint(1,4)-1)
        scores[str("NPC4")]["Scoreexpiry"] = current_time +cooldown
        print("NPC4 score is expired, and has been rewritten")
        highscore= max(x["Score"] for x in scores.values() if x["Scoreexpiry"] > current_time)
        lowscore= min(x["Score"] for x in scores.values() if x["Scoreexpiry"] > current_time)
        print(f"highscore is {highscore}")
        print(f"lowscore is {lowscore}")
    if scores[str("NPC3")]["Scoreexpiry"] > current_time:
        highscore= max(x["Score"] for x in scores.values() if x["Scoreexpiry"] > current_time)
        lowscore= min(x["Score"] for x in scores.values() if x["Scoreexpiry"] > current_time)
        print("NPC3 score is not expired, and has not been rewritten")
        print(f"highscore is {highscore}")
        print(f"lowscore is {lowscore}")
    else:
        scores[str("NPC3")]["Score"] = int(random.randint(1,4)-1)
        scores[str("NPC3")]["Scoreexpiry"] = current_time +cooldown
        print("NPC3 score is expired, and has been rewritten")
        highscore= max(x["Score"] for x in scores.values() if x["Scoreexpiry"] > current_time)
        lowscore= min(x["Score"] for x in scores.values() if x["Scoreexpiry"] > current_time)
        print(f"highscore is {highscore}")
        print(f"lowscore is {lowscore}")
    scores[str(authorid)] = {}
    scores[str(authorid)]["Username"] = players[str(authorid)]["Username"]
    scores[str(authorid)]["Media"] = ""
    scores[str(authorid)]["Score"] = playerroll
    scores[str(authorid)]["Scoreexpiry"] = current_time+cooldown
    with open("tavern.json","w") as t:
        json.dump(scores,t, indent=4)
    print("Player dungeon Score Saved")
    #check if the max is greater than the player's roll
    if highscore > playerroll:
        print(f"playerscore is lower than highscore")
        await send_message(f"<@{authorid}>'s roll of {playerroll} failed to beat the high score of {highscore}" , channel_id=[locations["Dungeon"]["Channel_ID"]])
    else:
        print(f"playerscore is the highscore")
        await send_message(f"<@{authorid}>'s roll of {playerroll} beat the high score of {highscore} and got a randomitem." , channel_id=[locations["Dungeon"]["Channel_ID"]])
        shop = await getshopdata()
        randomitem = random.choice(list(shop))
        await send_message(f"<@{authorid}> you gained {randomitem} as a randomitem.", user_id=[authorid])
        players[str(authorid)]["ReadyInventory"]=players[str(authorid)]["ReadyInventory"] + "\n        "+randomitem
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
    if lowscore == playerroll: #check if the min is equal to the player's roll
        print(f"lowscore is equal to playerscore")
        hp_pull = players[str(authorid)]["HP"]
        hp_pull=max(hp_pull - math.ceil(hp_pull/4),0)
        hpmoji = await hpmojiconv(hp_pull)
        await send_message(f"<@{authorid}> your roll of {playerroll} is the lowest roll. \nNew HP: {hpmoji}" , user_id=[authorid] )
        await send_message(f"<@{authorid}>'s roll of {playerroll} is the lowest roll and they lose 1/4 of their current health!" , channel_id=[locations["Dungeon"]["Channel_ID"]] )
        players[str(authorid)]["HP"] = hp_pull
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
    else :
        print(f"lowscore is not equal to playerscore")
        await send_message(f"<@{authorid}> your roll of {playerroll} is not the low roll.", user_id=[authorid] )
        await send_message(f"<@{authorid}>'s roll of {playerroll} is not the low roll." , channel_id=[locations["Dungeon"]["Channel_ID"]])
        players[str(authorid)]["HP"] = hp_pull
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
    with open("players.json","w") as f:
        json.dump(players,f, indent=4)

@bot.command(
    name="loot",
    description="24h. score 1d4. on 4+ gain two items at random. lowest score: lose 1/4 of your current health.",
    scope = guildid ,
)
async def loot(ctx: interactions.CommandContext):
    players = await getplayerdata()
    current_time = int(time.time())
    channelid=ctx.channel_id
    if str(ctx.author.id) in players:
        DelayDate_pull = players[str(ctx.author.id)]["DelayDate"]
        if locations["Dungeon"]["Role_ID"] not in ctx.author.roles:
            await ctx.send(f"You cannot /loot when you are not in the Dungeon!", ephemeral=True)  # golive
        elif DelayDate_pull > current_time:
            await queuenext(ctx)
            await ctx.send(f"You cannot act yet! You are delayed until <t:{DelayDate_pull}>.", ephemeral = True) #golive
        else:
            await ctx.send(f"You loot!",ephemeral=True)
            await doloot(ctx.author.id)
    else:
        await ctx.send(f"You need to join with /join before you can do that!" , ephemeral = True)

#battlelich is below

async def dobattlelich(authorid):
    await rage(authorid)
    players = await getplayerdata()
    scores = await getlichdata()
    Lastaction_pull = players[str(authorid)]["Lastaction"]
    playerroll = int(int(random.randint(1,4)) + (Lastaction_pull.count("battlelich") * 1))
    print(f"playerroll = {playerroll}")
    print(f"scores = \n{scores}\n")
    current_time = int(time.time())
    cooldown=basecd*1 #seconds in one day
    players[str(authorid)]["DelayDate"] = current_time+cooldown
    DelayDate_pull=current_time+cooldown
    players[str(authorid)]["Lastaction"] = "battlelich"
    await lastactiontime(authorid)
    with open("players.json","w") as f:
        json.dump(players,f, indent=4)
    if scores[str("NPC2")]["Scoreexpiry"] > current_time :
        highscore= max(x["Score"] for x in scores.values() if x["Scoreexpiry"] > current_time)
        lowscore= min(x["Score"] for x in scores.values() if x["Scoreexpiry"] > current_time)
        print("NPC2 score is not expired, and has not been rewritten")
        print(f"highscore is {highscore}")
        print(f"lowscore is {lowscore}")
    else:
        scores[str("NPC2")]["Score"] = int(random.randint(1,4)-1)
        scores[str("NPC2")]["Scoreexpiry"] = current_time +cooldown
        print("NPC2 score is expired, and has been rewritten")
        highscore= max(x["Score"] for x in scores.values() if x["Scoreexpiry"] > current_time)
        lowscore= min(x["Score"] for x in scores.values() if x["Scoreexpiry"] > current_time)
        print(f"highscore is {highscore}")
        print(f"lowscore is {lowscore}")
    if scores[str("NPC1")]["Scoreexpiry"] > current_time:
        highscore= max(x["Score"] for x in scores.values() if x["Scoreexpiry"] > current_time)
        lowscore= min(x["Score"] for x in scores.values() if x["Scoreexpiry"] > current_time)
        print("NPC1 score is not expired, and has not been rewritten")
        print(f"highscore is {highscore}")
        print(f"lowscore is {lowscore}")
    else:
        scores[str("NPC1")]["Score"] = int(random.randint(1,4)-1)
        scores[str("NPC1")]["Scoreexpiry"] = current_time +cooldown
        print("NPC1 score is expired, and has been rewritten")
        highscore= max(x["Score"] for x in scores.values() if x["Scoreexpiry"] > current_time)
        lowscore= min(x["Score"] for x in scores.values() if x["Scoreexpiry"] > current_time)
        print(f"highscore is {highscore}")
        print(f"lowscore is {lowscore}")
    scores[str(authorid)] = {}
    scores[str(authorid)]["Username"] = players[str(authorid)]["Username"]
    scores[str(authorid)]["Media"] = ""
    scores[str(authorid)]["Score"] = playerroll
    scores[str(authorid)]["Scoreexpiry"] = current_time+cooldown
    with open("lichcastle.json","w") as l:
        json.dump(scores,l, indent=4)
    print("Player Lich Score Saved")
    #check if the max is greater than the player's roll
    if highscore > playerroll:
        print(f"playerscore is lower than highscore")
        await send_message(f"<@{authorid}>'s roll of {playerroll} failed to beat the high score of {highscore}" , channel_id=[general])
    else:
        print(f"playerscore is the highscore")
        await send_message(f"<@{authorid}>'s roll of {playerroll} beat the high score of {highscore} and got the lichitem." , channel_id=[general])
        players[str(authorid)]["ReadyInventory"]=players[str(authorid)]["ReadyInventory"] + "\n        "+"lichitem"
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
    if lowscore == playerroll: #check if the min is equal to the player's roll
        print(f"lowscore is equal to playerscore")
        hp_pull = players[str(authorid)]["HP"]
        hp_pull=max(hp_pull - math.ceil(hp_pull/4),0)
        hpmoji = await hpmojiconv(hp_pull)
        await send_message(f"<@{authorid}> your roll of {playerroll} is the lowest roll. \nNew HP: {hpmoji}" , user_id=[authorid] )
        await send_message(f"<@{authorid}>'s roll of {playerroll} is the lowest roll and they lose 1/4 of their current health!" , channel_id=[general] )
        players[str(authorid)]["HP"] = hp_pull
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
    else :
        return
    with open("players.json","w") as f:
        json.dump(players,f, indent=4)

@bot.command(
    name="battlelich",
    description="24h. score 1d4. high score=5+: gain Lich's Item. low score: lose 1/4 current health.",
    scope = guildid ,
)
async def battlelich(ctx: interactions.CommandContext):
    players = await getplayerdata()
    current_time = int(time.time())
    channelid=ctx.channel_id
    if str(ctx.author.id) in players:
        DelayDate_pull = players[str(ctx.author.id)]["DelayDate"]
        if locations["Lich's Castle"]["Role_ID"] not in ctx.author.roles:
            await ctx.send(f"You cannot battlelich when you are not in the Lich's Castle!", ephemeral=True)  # golive
        elif DelayDate_pull > current_time:
            await queuenext(ctx)
            await ctx.send(f"You cannot act yet! You are delayed until <t:{DelayDate_pull}>.", ephemeral = True) #golive
        else:
            await ctx.send(f"You battle the lich!",ephemeral=True)
            await dobattlelich(ctx.author.id)
    else:
        await ctx.send(f"You need to join with /join before you can do that!" , ephemeral = True)

#lichitem is below

async def dolichitem(authorid, playertarget,channelid):
    await rage(authorid)
    players = await getplayerdata()
    current_time = int(time.time())
    print(f"{playertarget} is the player target")
    for k,v in players.items():
        if v['Username']==str(playertarget):
            targetid=k
    print(f"{targetid} is the player target id")
    players[str(targetid)]["HP"]=4200
    cooldown=basecd*1 #seconds in one day
    players[str(authorid)]["DelayDate"] = current_time+cooldown
    DelayDate_pull=current_time+cooldown
    players[str(authorid)]["Lastaction"] = "lichitem"
    await lastactiontime(authorid)
    targethp=players[str(targetid)]["HP"]
    hpmoji = await hpmojiconv(targethp)
    user = await interactions.get(bot, interactions.Member, object_id=targetid, guild_id=guildid, force='http')
    await user.remove_role(role=locations["Dead"]["Role_ID"], guild_id=guildid)
    userreadyinventory=str(players[str(authorid)]["ReadyInventory"])
    #replace first instance of item in user's readyinventory
    players[str(authorid)]["ReadyInventory"]=userreadyinventory.replace('\n        lichitem','',1)
    #add the item to the user's usedinventory
    players[str(authorid)]["UsedInventory"]=players[str(authorid)]["UsedInventory"] + "\n        "+"lichitem"
    if players[str(targetid)]["Location"] == "Dead":
        players[str(targetid)]["Location"] = "Crossroads"
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
    else:
        players[str(targetid)]["Location"] = players[str(targetid)]["Location"]
    with open("players.json","w") as f:
        json.dump(players,f, indent=4)
    await send_message(f"<@{targetid}> was affected by a lichitem from <@{authorid}>! \nNew HP: {hpmoji} ", channel_id=[channelid])
    await send_message(f"<@{authorid}> used lichitem on <@{targetid}> to set their hp to 4200! \n<@{authorid}> is on cooldown until <t:{DelayDate_pull}>", channel_id=[channelid])


@bot.command(
    name="lichitem",
    description="24h. set target player's HP to 4200. if the target is dead, resurrect them.",
    scope = guildid ,
    options=[
        interactions.Option(
            type=interactions.OptionType.STRING,
            name="playertarget",
            description="who you want to set to 4200",
            required=True,
            autocomplete=True,
        )
    ]
)
async def lichitem(ctx: interactions.CommandContext, playertarget: str):
    players = await getplayerdata()
    current_time = int(time.time())
    channelid=ctx.channel_id
    authorid=ctx.author.id
    if str(ctx.author.id) in players:
        DelayDate_pull = players[str(authorid)]["DelayDate"]
        if str("lichitem") not in players[str(authorid)]["ReadyInventory"]:
            await ctx.send(f"You cannot use /lichitem without a lichitem!", ephemeral=True)  # golive
        elif DelayDate_pull > current_time:
            await queuenext(ctx)
            await ctx.send(f"You cannot act yet! You are delayed until <t:{DelayDate_pull}>.", ephemeral = True) #golive
        else:
            await ctx.send(f"You use the lichitem!",ephemeral=True)
            await dolichitem(ctx.author.id, playertarget,channelid)
    else:
        await ctx.send(f"You need to join with /join before you can do that!" , ephemeral = True)

@bot.autocomplete("lichitem", "playertarget")
async def aid_autocomplete(ctx: interactions.CommandContext, value: str = ""):
    players = await getplayerdata()
    Usernames = [v["Username"] for v in players.values()]
    print (Usernames)
    items = Usernames
    choices = [
        interactions.Choice(name=item, value=item) for item in items if value in item
    ]
    await ctx.populate(choices)

#drinkingmedal is below

async def dodrinkingmedal(authorid,channelid):
    await rage(authorid)
    players = await getplayerdata()
    current_time = int(time.time())
    cooldown=basecd*2 #seconds in one day
    players[str(authorid)]["DelayDate"] = current_time+cooldown
    DelayDate_pull=current_time+cooldown
    players[str(authorid)]["Lastaction"] = "drinkingmedal"
    await lastactiontime(authorid)
    userreadyinventory=str(players[str(authorid)]["ReadyInventory"])
    #replace first instance of item in user's readyinventory
    players[str(authorid)]["ReadyInventory"]=userreadyinventory.replace('\n        drinkingmedal','',1)
    #add the item to the user's usedinventory
    players[str(authorid)]["UsedInventory"]=players[str(authorid)]["UsedInventory"] + "\n        "+"drinkingmedal"
    with open("players.json","w") as f:
        json.dump(players,f, indent=4)
    await send_message(f"<@{authorid}> used drinkingmedal to increase their lightattack damage by 420! \n<@{authorid}> is on cooldown until <t:{DelayDate_pull}>", channel_id=[channelid])


@bot.command(
    name="drinkingmedal",
    description="48h. increase the damage of your light attack by 420 for the rest of the game.",
    scope = guildid ,
)

async def drinkingmedal(ctx: interactions.CommandContext):
    players = await getplayerdata()
    current_time = int(time.time())
    channelid=ctx.channel_id
    authorid=ctx.author.id
    if str(ctx.author.id) in players:
        DelayDate_pull = players[str(authorid)]["DelayDate"]
        if str("drinkingmedal") not in players[str(authorid)]["ReadyInventory"]:
            await ctx.send(f"You cannot use /drinkingmedal without a drinkingmedal!", ephemeral=True)  # golive
        elif DelayDate_pull > current_time:
            await queuenext(ctx)
            await ctx.send(f"You cannot act yet! You are delayed until <t:{DelayDate_pull}>.", ephemeral = True) #golive
        else:
            await ctx.send(f"You use the drinkingmedal!",ephemeral=True)
            await dodrinkingmedal(ctx.author.id, channelid)
    else:
        await ctx.send(f"You need to join with /join before you can do that!" , ephemeral = True)

#goodiebag is below

async def dogoodiebag(authorid,channelid):
    await rage(authorid)
    players = await getplayerdata()
    current_time = int(time.time())
    cooldown=basecd*1 #seconds in one day
    players[str(authorid)]["DelayDate"] = current_time+cooldown
    DelayDate_pull=current_time+cooldown
    players[str(authorid)]["Lastaction"] = "goodiebag"
    await lastactiontime(authorid)
    userreadyinventory=str(players[str(authorid)]["ReadyInventory"])
    #get a randomitem
    shop = await getshopdata()
    randomitem = random.choice(list(shop))
    await send_message(f"<@{authorid}> you gained {randomitem} as a randomitem.", user_id=[authorid])
    players[str(authorid)]["ReadyInventory"]=players[str(authorid)]["ReadyInventory"] + "\n        "+randomitem
    #replace first instance of item in user's readyinventory
    players[str(authorid)]["ReadyInventory"]=userreadyinventory.replace('\n        goodiebag','',1)
    #add the item to the user's usedinventory
    players[str(authorid)]["UsedInventory"]=players[str(authorid)]["UsedInventory"] + "\n        "+"goodiebag"
    with open("players.json","w") as f:
        json.dump(players,f, indent=4)
    await send_message(f"<@{authorid}> used goodiebag to gain a random item! \n<@{authorid}> is on cooldown until <t:{DelayDate_pull}>", channel_id=[channelid])

@bot.command(
    name="goodiebag",
    description="24h. add a random ready item to your inventory.",
    scope = guildid ,
)

async def goodiebag(ctx: interactions.CommandContext):
    players = await getplayerdata()
    current_time = int(time.time())
    channelid=ctx.channel_id
    authorid=ctx.author.id
    if str(ctx.author.id) in players:
        DelayDate_pull = players[str(authorid)]["DelayDate"]
        if str("goodiebag") not in players[str(authorid)]["ReadyInventory"]:
            await ctx.send(f"You cannot use /goodiebag without a goodiebag!", ephemeral=True)  # golive
        elif DelayDate_pull > current_time:
            await queuenext(ctx)
            await ctx.send(f"You cannot act yet! You are delayed until <t:{DelayDate_pull}>.", ephemeral = True) #golive
        else:
            await ctx.send(f"You use the goodiebag!",ephemeral=True)
            await dogoodiebag(ctx.author.id, channelid)
    else:
        await ctx.send(f"You need to join with /join before you can do that!" , ephemeral = True)

#tractor is below

async def dotractor(authorid,channelid):
    await rage(authorid)
    players = await getplayerdata()
    current_time = int(time.time())
    cooldown=basecd*2 #seconds in one day
    players[str(authorid)]["DelayDate"] = current_time+cooldown
    DelayDate_pull=current_time+cooldown
    players[str(authorid)]["Lastaction"] = "tractor"
    await lastactiontime(authorid)
    userreadyinventory=str(players[str(authorid)]["ReadyInventory"])
    #replace first instance of item in user's readyinventory
    players[str(authorid)]["ReadyInventory"]=userreadyinventory.replace('\n        tractor','',1)
    #add the item to the user's usedinventory
    players[str(authorid)]["UsedInventory"]=players[str(authorid)]["UsedInventory"] + "\n        "+"tractor"
    with open("players.json","w") as f:
        json.dump(players,f, indent=4)
    await send_message(f"<@{authorid}> used tractor to increase their farm profit by 1! \n<@{authorid}> is on cooldown until <t:{DelayDate_pull}>", channel_id=[channelid])


@bot.command(
    name="tractor",
    description="48h. whenever you farm, gain an additional seed coin for the rest of the game.",
    scope = guildid ,
)

async def tractor(ctx: interactions.CommandContext):
    players = await getplayerdata()
    current_time = int(time.time())
    channelid=ctx.channel_id
    authorid=ctx.author.id
    if str(ctx.author.id) in players:
        DelayDate_pull = players[str(authorid)]["DelayDate"]
        if str("tractor") not in players[str(authorid)]["ReadyInventory"]:
            await ctx.send(f"You cannot use /tractor without a tractor!", ephemeral=True)  # golive
        elif DelayDate_pull > current_time:
            await queuenext(ctx)
            await ctx.send(f"You cannot act yet! You are delayed until <t:{DelayDate_pull}>.", ephemeral = True) #golive
        else:
            await ctx.send(f"You use the tractor!",ephemeral=True)
            await dotractor(ctx.author.id, channelid)
    else:
        await ctx.send(f"You need to join with /join before you can do that!" , ephemeral = True)

#beer-bandolier is below

async def dobeerbando(authorid,channelid):
    await rage(authorid)
    players = await getplayerdata()
    current_time = int(time.time())
    cooldown=basecd*1
    players[str(authorid)]["DelayDate"] = current_time+cooldown
    DelayDate_pull=current_time+cooldown
    players[str(authorid)]["Lastaction"] = "beerbando"
    await lastactiontime(authorid)
    #increase user's rage by 3
    players[str(authorid)]["Rage"]=players[str(authorid)]["Rage"]+3
    userreadyinventory=str(players[str(authorid)]["ReadyInventory"])
    #replace first instance of item in user's readyinventory
    players[str(authorid)]["ReadyInventory"]=userreadyinventory.replace('\n        beerbando','',1)
    #add the item to the user's usedinventory
    players[str(authorid)]["UsedInventory"]=players[str(authorid)]["UsedInventory"] + "\n        "+"beerbando"
    with open("players.json","w") as f:
        json.dump(players,f, indent=4)
    await send_message(f"<@{authorid}> used beerbando to increase their rage by 3! \n<@{authorid}> is on cooldown until <t:{DelayDate_pull}>", channel_id=[channelid])


@bot.command(
    name="beerbando",
    description="24h. you gain three rage.",
    scope = guildid ,
)

async def beerbando(ctx: interactions.CommandContext):
    players = await getplayerdata()
    current_time = int(time.time())
    channelid=ctx.channel_id
    authorid=ctx.author.id
    if str(ctx.author.id) in players:
        DelayDate_pull = players[str(authorid)]["DelayDate"]
        if str("beerbando") not in players[str(authorid)]["ReadyInventory"]:
            await ctx.send(f"You cannot use /beerbando without a beerbando!", ephemeral=True)  # golive
        elif DelayDate_pull > current_time:
            await queuenext(ctx)
            await ctx.send(f"You cannot act yet! You are delayed until <t:{DelayDate_pull}>.", ephemeral = True) #golive
        else:
            await ctx.send(f"You use the beerbando!",ephemeral=True)
            await dobeerbando(ctx.author.id, channelid)
    else:
        await ctx.send(f"You need to join with /join before you can do that!" , ephemeral = True)

#aimtraining is below

async def doaimtrain(authorid,channelid):
    await rage(authorid)
    players = await getplayerdata()
    current_time = int(time.time())
    cooldown=basecd*3
    players[str(authorid)]["DelayDate"] = current_time+cooldown
    DelayDate_pull=current_time+cooldown
    players[str(authorid)]["Lastaction"] = "aimtrain"
    await lastactiontime(authorid)
    userreadyinventory=str(players[str(authorid)]["ReadyInventory"])
    #replace first instance of item in user's readyinventory
    players[str(authorid)]["ReadyInventory"]=userreadyinventory.replace('\n        aimtraining','',1)
    #add the item to the user's usedinventory
    players[str(authorid)]["UsedInventory"]=players[str(authorid)]["UsedInventory"] + "\n        "+"aimtraining"
    with open("players.json","w") as f:
        json.dump(players,f, indent=4)
    await send_message(f"<@{authorid}> used aimtraining to decrease the time cost of their heavy attacks to 24h! \n<@{authorid}> is on cooldown until <t:{DelayDate_pull}>", channel_id=[channelid])


@bot.command(
    name="aimtrain",
    description="72h. reduce heavy attacks to 24h cooldown. doesn't stack.",
    scope = guildid ,
)

async def aimtrain(ctx: interactions.CommandContext):
    players = await getplayerdata()
    current_time = int(time.time())
    channelid=ctx.channel_id
    authorid=ctx.author.id
    if str(ctx.author.id) in players:
        DelayDate_pull = players[str(authorid)]["DelayDate"]
        if str("aimtraining") not in players[str(authorid)]["ReadyInventory"]:
            await ctx.send(f"You cannot use /aimtrain without an aimtraining!", ephemeral=True)  # golive
        elif DelayDate_pull > current_time:
            await queuenext(ctx)
            await ctx.send(f"You cannot act yet! You are delayed until <t:{DelayDate_pull}>.", ephemeral = True) #golive
        else:
            await ctx.send(f"You use the aimtraining!",ephemeral=True)
            await doaimtrain(ctx.author.id, channelid)
    else:
        await ctx.send(f"You need to join with /join before you can do that!" , ephemeral = True)

#Crooked Abacus is below

async def docrookedabacus(authorid,channelid):
    await rage(authorid)
    players = await getplayerdata()
    current_time = int(time.time())
    cooldown=basecd*2
    players[str(authorid)]["DelayDate"] = current_time+cooldown
    DelayDate_pull=current_time+cooldown
    players[str(authorid)]["Lastaction"] = "crookedabacus"
    await lastactiontime(authorid)
    userreadyinventory=str(players[str(authorid)]["ReadyInventory"])
    #replace first instance of item in user's readyinventory
    players[str(authorid)]["ReadyInventory"]=userreadyinventory.replace('\n        crookedabacus','',1)
    #add the item to the user's usedinventory
    players[str(authorid)]["UsedInventory"]=players[str(authorid)]["UsedInventory"] + "\n        "+"crookedabacus"
    with open("players.json","w") as f:
        json.dump(players,f, indent=4)
    await send_message(f"<@{authorid}> used a crookedabacus to gain a seedcoin whenever they /trade or /exchange for the rest of the game! \n<@{authorid}> is on cooldown until <t:{DelayDate_pull}>", channel_id=[channelid])


@bot.command(
    name="crookedabacus",
    description="48h. whenever you exchange or trade, gain a seed coin for the rest of the game.",
    scope = guildid ,
)

async def crookedabacus(ctx: interactions.CommandContext):
    players = await getplayerdata()
    current_time = int(time.time())
    channelid=ctx.channel_id
    authorid=ctx.author.id
    if str(ctx.author.id) in players:
        DelayDate_pull = players[str(authorid)]["DelayDate"]
        if str("crookedabacus") not in players[str(authorid)]["ReadyInventory"]:
            await ctx.send(f"You cannot use /crookedabacus without a crookedabacus!", ephemeral=True)  # golive
        elif DelayDate_pull > current_time:
            await queuenext(ctx)
            await ctx.send(f"You cannot act yet! You are delayed until <t:{DelayDate_pull}>.", ephemeral = True) #golive
        else:
            await ctx.send(f"You use the crookedabacus!",ephemeral=True)
            await docrookedabacus(ctx.author.id, channelid)
    else:
        await ctx.send(f"You need to join with /join before you can do that!" , ephemeral = True)

#adventuringgear is below

async def doadventuringgear(authorid,channelid):
    await rage(authorid)
    players = await getplayerdata()
    current_time = int(time.time())
    cooldown=basecd*2
    players[str(authorid)]["DelayDate"] = current_time+cooldown
    DelayDate_pull=current_time+cooldown
    players[str(authorid)]["Lastaction"] = "adventuringgear"
    await lastactiontime(authorid)
    userreadyinventory=str(players[str(authorid)]["ReadyInventory"])
    #replace first instance of item in user's readyinventory
    players[str(authorid)]["ReadyInventory"]=userreadyinventory.replace('\n        adventuringgear','',1)
    #add the item to the user's usedinventory
    players[str(authorid)]["UsedInventory"]=players[str(authorid)]["UsedInventory"] + "\n        "+"adventuringgear"
    with open("players.json","w") as f:
        json.dump(players,f, indent=4)
    await send_message(f"<@{authorid}> used adventuringgear to score one higher whenever they /loot for the rest of the game! \n<@{authorid}> is on cooldown until <t:{DelayDate_pull}>", channel_id=[channelid])


@bot.command(
    name="adventuringgear",
    description="48h. increase your loot score by 1 for the rest of the game.",
    scope = guildid ,
)

async def adventuringgear(ctx: interactions.CommandContext):
    players = await getplayerdata()
    current_time = int(time.time())
    channelid=ctx.channel_id
    authorid=ctx.author.id
    if str(ctx.author.id) in players:
        DelayDate_pull = players[str(authorid)]["DelayDate"]
        if str("adventuringgear") not in players[str(authorid)]["ReadyInventory"]:
            await ctx.send(f"You cannot use /adventuringgear without adventuringgear!", ephemeral=True)  # golive
        elif DelayDate_pull > current_time:
            await queuenext(ctx)
            await ctx.send(f"You cannot act yet! You are delayed until <t:{DelayDate_pull}>.", ephemeral = True) #golive
        else:
            await ctx.send(f"You use the adventuringgear!",ephemeral=True)
            await doadventuringgear(ctx.author.id, channelid)
    else:
        await ctx.send(f"You need to join with /join before you can do that!" , ephemeral = True)

actionhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="Actions",
    custom_id="Actions",
)

@bot.component("Actions")
async def button_response(ctx):
    row = interactions.spread_to_rows(joinhelpbutton, lightattackhelpbutton, normalattackhelpbutton, heavyattackhelpbutton, interrupthelpbutton, evadehelpbutton, resthelpbutton, areactionhelpbutton,useitemhelpbutton)
    await ctx.send(f"**Actions**\nActions are what players do!\n\nTo get started take the **/join** action!\n\nMost actions place players on a cooldown (such as 24hours). The player can't take any actions that would place them on cooldown until they are off cooldown.\n\nWhen you attempt to perform an action and you are on cooldown, you will instead queue that action. The bot will make you perform that action after you are off cooldown.\n\nFind out more:", components=row, ephemeral=True)

joinhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="Join",
    custom_id="Join",
)

@bot.component("Join")
async def button_response(ctx):
    await ctx.send(f"**Join**\n/Join\nJoin the game!", ephemeral=True)

lightattackhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.DANGER,
    label="Lightattack",
    custom_id="Lightattack",
)

@bot.component("Lightattack")
async def button_response(ctx):
    await ctx.send(f"**Light Attack**\n/lightattack\n 24h cooldown. gain 1 rage. attack a player in your area for 950 damage.", ephemeral=True)

normalattackhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.DANGER,
    label="Normalattack",
    custom_id="Normalattack",
)

@bot.component("Normalattack")
async def button_response(ctx):
    await ctx.send(f"**Normal Attack**\n/normalattack\n 48h cooldown. gain 3 rage. attack a player in your area for 2300 damage.", ephemeral=True)

heavyattackhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.DANGER,
    label="Heavyattack",
    custom_id="Heavyattack",
)

@bot.component("Heavyattack")
async def button_response(ctx):
    await ctx.send(f"**Heavy Attack**\n/heavyattack\n 72h cooldown. gain 6 rage. attack a player in your area for 3650 damage.", ephemeral=True)

interrupthelpbutton = interactions.Button(
    style=interactions.ButtonStyle.DANGER,
    label="Interrupt",
    custom_id="Interrupt",
)

@bot.component("Interrupt")
async def button_response(ctx):
    await ctx.send(f"**Interrupt**\n/interrupt\n 24h cooldown. hit a player in your area for 4200 if they are resting or evading.", ephemeral=True)


evadehelpbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Evade",
    custom_id="Evade",
)

@bot.component("Evade")
async def button_response(ctx):
    await ctx.send(f"**Evade**\n/evade\n 24h cooldown. Receive no damage from light, normal, or heavy attacks while you are on cooldown from evading.", ephemeral=True)


resthelpbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Rest",
    custom_id="Rest",
)

@bot.component("Rest")
async def button_response(ctx):
    await ctx.send(f"**Rest**\n/rest\n 24h cooldown. Heal half of your missing health rounded up unless you used rest as your last action.", ephemeral=True)

areactionhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="AreaAction",
    custom_id="AreaAction",
)

@bot.component("AreaAction")
async def button_response(ctx):
    row = interactions.spread_to_rows(crossroadshelpbutton, dungeonhelpbutton, farmlandhelpbutton, keephelpbutton, lichcastlehelpbutton, shophelpbutton, tavernhelpbutton)
    await ctx.send(f"**Locations** \nYou can travel from any location to the crossroads using /traveltocrossroads \n\nYou can travel from the crossroads to any area using /travelto \nLocations each have their own unique area action!\n\nArea actions always have a 24 hour cooldown, but have a variety of effects. \n\nUse the buttons below to learn more about the area actions:", components = row, ephemeral=True)

useitemhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="Use an Item",
    custom_id="useitem",
)

@bot.component("useitem")
async def button_response(ctx):
    row = interactions.spread_to_rows(adventuringgearhelpbutton, aimtraininghelpbutton, crookedabacushelpbutton, goodiebaghelpbutton, tractorhelpbutton, drinkingmedalhelpbutton, lichitemhelpbutton, beerbandohelpbutton)
    await ctx.send(f"**Items** \nItems fall into two broad categories: \n\n**Ready Items**\nItems you can use for benefits that can be instantaneous, duration, or permanent in nature.\nWhen you use a Ready Item it moves to your Used Items.\n**Used items**\nItems you have used in the past that may or may not be providing you a benefit.\n\nFind out more about the items below:", components = row, ephemeral=True)

locationhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="Locations",
    custom_id="Locations",
)

@bot.component("Locations")
async def button_response(ctx):
    row = interactions.spread_to_rows(crossroadshelpbutton, dungeonhelpbutton, farmlandhelpbutton, keephelpbutton, lichcastlehelpbutton, shophelpbutton, tavernhelpbutton)
    await ctx.send(f"**Locations** \nYou can travel from any location to the crossroads using /traveltocrossroads \n\nYou can travel from the crossroads to any area using /travelto \nLocations each have their own unique area action!\n\nArea actions always have a 24 hour cooldown, but have a variety of effects. \n\nUse the buttons below to learn more about the area actions:", components = row, ephemeral=True)

crossroadshelpbutton = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="Crossroads",
    custom_id="Crossroads",
)

@bot.component("Crossroads")
async def button_response(ctx):
    await ctx.send(f"**Crossroads**\n/exchange\n 24h cooldown. give a player in your area a ready item from your inventory.", ephemeral=True)

dungeonhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="Dungeon",
    custom_id="Dungeon",
)

@bot.component("Dungeon")
async def button_response(ctx):
    await ctx.send(f"**Dungeon**\n/loot\n 24h cooldown. score 1d4. on 4+ gain two items at random. lowest score: lose 1/4 of your current health.", ephemeral=True)

farmlandhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="Farmland",
    custom_id="Farmland",
)

@bot.component("Farmland")
async def button_response(ctx):
    await ctx.send(f"**Farmland**\n/farm\n 24h cooldown. score 1d4. gain your score seed coins.", ephemeral=True)


keephelpbutton = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="Keep",
    custom_id="Keep",
)

@bot.component("Keep")
async def button_response(ctx):
    await ctx.send(f"**Keep**\n/aid\n 24h cooldown. heal the chosen player 1/4 of their missing health.", ephemeral=True)


lichcastlehelpbutton = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="Lich's Castle",
    custom_id="lichcastle",
)

@bot.component("lichcastle")
async def button_response(ctx):
    await ctx.send(f"**Lich's Castle**\n/battlelich\n 24h cooldown. score 1d4. high score of 5+: gain Lich's Item. low score: lose 1/4 current health.", ephemeral=True)

shophelpbutton = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="Shop",
    custom_id="Shop",
)

@bot.component("Shop")
async def button_response(ctx):
    await ctx.send(f"**Shop**\n/trade\n 24h cooldown. exchange seed coins for a shop item.", ephemeral=True)

tavernhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="Tavern",
    custom_id="Tavern",
)

@bot.component("Tavern")
async def button_response(ctx):
    await ctx.send(f"**Tavern**\n/drinkingchallenge\n 24h cooldown. score 1d4. high score: gain a used drinking challenge medal. low score: loses 1/4 current health otherwise: heal 1/4 missing health.", ephemeral=True)

itemhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="Items",
    custom_id="Items",
)

@bot.component("Items")
async def button_response(ctx):
    row = interactions.spread_to_rows(adventuringgearhelpbutton, aimtraininghelpbutton, crookedabacushelpbutton, goodiebaghelpbutton, tractorhelpbutton, drinkingmedalhelpbutton, lichitemhelpbutton, beerbandohelpbutton)
    await ctx.send(f"**Items** \nItems fall into two broad categories: \n\n**Ready Items**\nItems you can use for benefits that can be instantaneous, duration, or permanent in nature.\nWhen you use a Ready Item it moves to your Used Items.\n**Used items**\nItems you have used in the past that may or may not be providing you a benefit.\n\nFind out more about the items below:", components = row, ephemeral=True)

adventuringgearhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Adventuring Gear",
    custom_id="adventuringgear",
)

@bot.component("adventuringgear")
async def button_response(ctx):
    await ctx.send(f"**Adventuring Gear**\n5 SC cost \n48 hour cooldown. increase your loot score by 1 for the rest of the game.", ephemeral=True)

aimtraininghelpbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Aim Training",
    custom_id="aimtraining",
)

@bot.component("aimtraining")
async def button_response(ctx):
    await ctx.send(f"**Aim Training**\n8 SC cost\n72 hour cooldown. Reduce heavy attacks to 24h cooldown for the rest of the game. doesn't stack.", ephemeral=True)

crookedabacushelpbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Crooked Abacus",
    custom_id="crookedabacus",
)

@bot.component("crookedabacus")
async def button_response(ctx):
    await ctx.send(f"**Crooked Abacus**\n5 SC cost\n48 hour cooldown. Whenever you exchange or trade, gain a seed coin for the rest of the game.", ephemeral=True)

goodiebaghelpbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Goodie Bag",
    custom_id="goodiebag",
)

@bot.component("goodiebag")
async def button_response(ctx):
    await ctx.send(f"**Goodie Bag**\n8 SC cost\n24 hour cooldown. Add a random ready item to your inventory.", ephemeral=True)

tractorhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Tractor",
    custom_id="tractor",
)

@bot.component("tractor")
async def button_response(ctx):
    await ctx.send(f"**Tractor**\n5 SC cost\n48 hour cooldown. Whenever you farm, gain an additional seed coin for the rest of the game.", ephemeral=True)

drinkingmedalhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Drinking Medal ",
    custom_id="drinkingmedal",
)

@bot.component("drinkingmedal")
async def button_response(ctx):
    await ctx.send(f"**Drinking Medal**\n6 SC cost\n48 hour cooldown. Increase the damage of your light attack by 420 for the rest of the game.", ephemeral=True)

lichitemhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Lich's Item ",
    custom_id="lichitem",
)

@bot.component("lichitem")
async def button_response(ctx):
    await ctx.send(f"**Lich's Item**\n15 SC cost\n24 hour cooldown. Set target player's HP to 4200. If the target is dead, resurrect them.", ephemeral=True)

beerbandohelpbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Beer Bandolier",
    custom_id="beerbando",
)

@bot.component("beerbando")
async def button_response(ctx):
    await ctx.send(f"**Beer Bandolier**\n3 SC cost\n24 hour cooldown. You gain three rage.", ephemeral=True)

Poisonhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Poison",
    custom_id="Poison",
)

@bot.component("Poison")
async def button_response(ctx):
    await ctx.send(f"**Poison**\n\nWhen the game starts A 7 day poison timer starts and the poison damage is set to 650.\n\n Whenever the poison timer ends, the poison damage increases by 100 then every player is damaged by the poison.\n\n Then the poison timer restarts with 10% less time.", ephemeral=True)

Ragehelpbutton = interactions.Button(
    style=interactions.ButtonStyle.DANGER,
    label="Rage",
    custom_id="Rage",
)

@bot.component("Rage")
async def button_response(ctx):
    await ctx.send(f"**Rage**\n\n Whenever you take an action, you heal equal to your Rage times 420hp. Then you lose one Rage.", ephemeral=True)

@bot.command(
    name="help",
    description="get info on a topic",
    scope = guildid ,
)
async def help(ctx: interactions.CommandContext,):
    players = await getplayerdata()
    current_time = int(time.time())
    channelid=ctx.channel_id
    row = interactions.ActionRow(
    components=[actionhelpbutton, locationhelpbutton, itemhelpbutton, Poisonhelpbutton, Ragehelpbutton ]
)
    await ctx.send(f"What would you like help with?", components = row, ephemeral = True)


functiondict = {'lightattack' : dolightattack,
                'normalattack' : donormalattack,
                'heavyattack' : doheavyattack,
                'interrupt' : dointerrupt,
                'evade' : doevade,
                'rest' : dorest,
                'farm' : dofarm,
                'travelto' : dotravelto,
                'traveltocrossroads': dotraveltocrossroads,
                'aid': doaid,
                'drinkingchallenge': dodrinkingchallenge,
                'battlelich': dobattlelich,
                'lichitem': dolichitem,
                'drinkingmedal': dodrinkingmedal,
                'tractor':dotractor,
                'beerbando':dobeerbando,
                'aimtrain':doaimtrain,
                'crookedabacus':docrookedabacus,
                'loot':doloot,
                'adventuringgear':doadventuringgear,
                'goodiebag':dogoodiebag,
                'trade':dotrade}



bot.start ()

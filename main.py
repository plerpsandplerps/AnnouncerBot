import interactions
from interactions import Button, ButtonStyle, SelectMenu, SelectOption, ActionRow, spread_to_rows
import asyncio
import random
from datetime import datetime
import random
import time
import math
import json
import pprint as pp
import re
from typing import List
from interactions.ext.paginator import Page, Paginator
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger()
logger.addHandler(logging.FileHandler('test.log', 'a'))
print = logger.info


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
ligmachannel= tokens["ligmachannelid"]

bot = interactions.Client(token=tokens["token"], intents=interactions.Intents.DEFAULT | interactions.Intents.GUILD_MESSAGE_CONTENT)

#new ligma
#ligma to ligma.json to keep it consistent between script reboots
@bot.event
async def on_ready():
    print(f"We're online! We've logged in as {bot.me.name}.")
    print(f"Our latency is {round(bot.latency)} ms.")
    current_time = int(time.time())
    guild = await interactions.get(bot, interactions.Guild, object_id=guildid)
    memberslist = await guild.get_all_members()
    membersdict = {Member.id: Member for Member in memberslist}
    membersdict = str(membersdict)
    membersdict = re.sub(re.escape("Snowflake("),"",membersdict)
    membersdict = re.sub(re.escape("Member(user=User("),"",membersdict)
    membersdict = re.sub(re.escape(")"),"",membersdict)
    membersdict = str(membersdict)
    membersdictfind = r"(\d+):\s*id=\d+\s*,\s*username='(.*?)',\sdiscriminator='\d+',\sbot=(\w+),\snick=(.*?.),"
    membersdict = re.findall(membersdictfind, membersdict)
    membersdict = dict([(a, (b, c, d)) for a, b, c, d in membersdict])
    membersdict = {k: {'Username': v[0]+" ("+v[2]+")", 'Mana': 3, 'HP': 10000, 'Location': "Crossroads", 'SC': 10, 'Rage': 0, 'InitManaDate': current_time + basecd,'NextMana': current_time + basecd,'ReadyInventory': "\n        goodiebag",'EquippedInventory': ' ','ReadyDate': current_time,'Lastactiontime': current_time, 'Lastaction':"start",'Nextaction':"", 'RestTimer': current_time,'EvadeTimer': current_time,'Team': "No Team",'NewTeam':"No Team",'BountyReward': 7, 'Orders':"",'OrderDate': 0, "OptOutOrder": "", "ResetHealCap": 0, "ResetDamageCap": 0, "DamageCap": 6900, "HealCap": 4200,} for k, v in membersdict.items() if v[1] != 'True'}
    for key in membersdict.keys():
        origstr = str(membersdict[key]['Username'])
        if origstr[-7:] == " (None)" :
            membersdict[key]["Username"] = origstr[:-7]
        else:
            membersdict[key]["Username"]
    players = await getplayerdata()
    bounty = await getbountydata()
    for key in bounty.keys():
      if key in membersdict.keys():
        membersdict[key]['SC']+=bounty[key]['SC']
    newplayers = membersdict | players
    with open("players.json","w") as f:
        json.dump(newplayers,f, indent=4)
    for key in newplayers.keys():
        if key not in players.keys():
            user = await interactions.get(bot, interactions.Member, object_id=key, guild_id=guildid, force='http')
            await user.remove_role(locations["Dead"]["Role_ID"], guildid)
            await user.add_role(locations["Crossroads"]["Role_ID"], guildid)
            await user.add_role(locations["Playing"]["Role_ID"], guildid)
    loop = asyncio.get_running_loop()
    loop.create_task(pollfornext())
    loop.create_task(pollfororders())
    loop.create_task(pollclock())
    loop.create_task(pollformanagain())
    loop.create_task(pollforcaps())
    loop.create_task(pollformana())
    loop.create_task(pollforqueue())
    loop.create_task(pollforbackup())
    print(f"Started at {current_time}")
    ligma = await getligmadata()
    channel = await interactions.get(bot, interactions.Channel, object_id=ligmachannel)
    if str("ligmadate") in ligma:
        print(f"ligma date already exists!")
        loop.create_task(pollforligma())
    else:
        smalltime=int(86400)
        smalltimeunit="days"
        firstcountdown=int(7*smalltime)
        nextligmatime=current_time+firstcountdown
        ligma = {}
        ligma["ligmadate"] = nextligmatime
        ligma["firstligmadate"] = nextligmatime
        locs = list(locations)
        reallocs = []
        for location in locs:
            if location != "Dead" and location != "Playing":
                reallocs.append(location)
        randomloc = random.choice(reallocs)
        print (randomloc)
        ligma["nextlocation"] = randomloc
        ligma["ligmatimer"] = firstcountdown
        ligma["Crossroads"] = 0
        ligma["Dungeon"] = 0
        ligma["Farmland"] = 0
        ligma["Keep"] = 0
        ligma["Lich's Castle"] = 0
        ligma["Shop"] = 0
        ligma["Tavern"] = 0
        ligma[randomloc] = ligma[randomloc]+1
        ligmadamage_pull = (ligma[str(randomloc)]*250)
        ligmatimer_pull = firstcountdown
        with open("ligma.json","w") as h:
            json.dump(ligma,h, indent=4)
        ligma = await getligmadata()
        ligmadate_pull = ligma["ligmadate"]
        ligmalocation = str(randomloc)
        ligmatimer_pull = ligma["ligmatimer"]
        await channel.send(f"The first ligma outbreak will deal 250 on <t:{nextligmatime}> at the **{randomloc}**!")
        loop.create_task(pollforligma())

async def ligmaiterate():
    print(f"iterating ligma at:{int(time.time())}")
    ligma = await getligmadata()
    current_time = int(time.time())
    channel = await interactions.get(bot, interactions.Channel, object_id=ligmachannel)
    ligmadate_pull = ligma["ligmadate"]
    ligmalocation_pull = ligma["nextlocation"]

    #find all of the locations with ligma
    locs = list(locations)
    ligmalocs = []
    for location in locs:
        if location != "Dead" and location != "Playing":
            if ligma[location] > 0:
                ligmalocs.append(location)
    print (ligmalocs)

    #find all of the reallocations and pick a random one
    locs = list(locations)
    reallocs = []
    for location in locs:
        if location != "Dead" and location != "Playing":
            reallocs.append(location)
    randomloc = random.choice(reallocs)

    #update timer
    ligmatimer_pull = ligma["ligmatimer"]
    ligmatimer_pull = max(math.ceil(ligmatimer_pull*.9), basecd)

    #update next ligma time
    nextligmatime= int(current_time + ligmatimer_pull)

    # damage players in ligmalocations
    players = await getplayerdata ()
    ligmaplayers = []
    for k,v in players.items():
        if v['Location'] in ligmalocs:
            location = v['Location']
            ligmadamage_pull = (ligma[location]*250)
            v["HP"] = v["HP"] - ligmadamage_pull
            user = v["Username"]
            ligmaplayers.append(k)
    print (ligmaplayers)
    with open("players.json","w") as f:
        json.dump(players,f, indent=4)

    # write new ligma stuff
    ligma["ligmadate"] = nextligmatime
    ligma["nextlocation"] = randomloc
    ligma[randomloc] = 1+ ligma[randomloc]
    ligma["ligmadamage"] = ligmadamage_pull
    ligma["ligmatimer"] = ligmatimer_pull
    with open("ligma.json","w") as h:
       json.dump(ligma, h, indent=4)

    # check for dead?
    print(f"\ndead?:{int(time.time())}")
    for k,v in players.items():
        if v['HP'] <= 0 and v['Location'] != "Dead":
            EquippedInventory_pull = v["EquippedInventory"]
            targetlichprot = EquippedInventory_pull.count("lichitem")
            print(f"\nthe target died!")
            if str("Wight - ") in str(k):
                await send_message(f"{k} died because of ||LIGMA BALLS||!", channel_id=[general])
                players[str(k)]["Location"] = "Dead"
                with open("players.json","w") as f:
                    json.dump(players,f, indent=4)
            else:
                user = await interactions.get(bot, interactions.Member, object_id=k, guild_id=guildid, force='http')
                if targetlichprot > 0:
                    v["HP"] = 4200
                    #replace first instance of item in user's readyinventory
                    players[str(k)]["EquippedInventory"]=EquippedInventory_pull.replace('\n        lichitem',' ',1)
                    await send_message(f"<@{k}> would have died because of ||LIGMA BALLS||, but they were protected by their equipped lich item! \n\nThat lichitem has since broken.", channel_id=[general])
                else:
                    await send_message(f"<@{k}> died because of ||LIGMA BALLS||!", channel_id=[general])
                    #give dead role
                    await user.add_role(role=locations ["Dead"]["Role_ID"], guild_id=guildid)
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
                    players[str(k)]["Location"] = "Dead"
                    players[str(k)]["Team"] = "Dead"
                    players[str(k)]["Nextaction"] = ""
                with open("players.json","w") as f:
                    json.dump(players,f, indent=4)
    crossroadsdamage = 0
    if ligma["Crossroads"] > 0:
        crossroadsdamage = (ligma["Crossroads"]*250)
    dungeondamage = 0
    if ligma["Dungeon"] > 0:
        dungeondamage = (ligma["Dungeon"]*250)
    farmlanddamage = 0
    if ligma["Farmland"] > 0:
        farmlanddamage = (ligma["Farmland"]*250)
    keepdamage = 0
    if ligma["Keep"] > 0:
        keepdamage = (ligma["Keep"]*250)
    lichdamage = 0
    if ligma["Lich's Castle"] > 0:
        lichdamage = (ligma["Lich's Castle"]*250)
    taverndamage = 0
    if ligma["Tavern"] > 0:
        taverndamage = (ligma["Tavern"]*250)
    shopdamage = 0
    if ligma["Shop"] >0:
        shopdamage = (ligma["Shop"]*250)

    ligmaurl="https://media.tenor.com/K9s5fCvjG4AAAAAM/average-ligma-member-ligma.gif"
    ligmaimg = interactions.EmbedImageStruct(
                        url=ligmaurl,
                        height = 512,
                        width = 512,
                        )
    ligmaemb = interactions.api.models.message.Embed(
        title = f"Oh no a Ligma outbreak!",
        color = 0x5764EF,
        description = f"\n||LIGMA BALLS|| damage increased at the {ligmalocation_pull} then ||LIGMA BALLS|| dealt damage at all ligma outbreak locations! \n\n",
        image = ligmaimg,
        fields = [interactions.EmbedField(name="Next Ligma Time",value=f"<t:{nextligmatime}>",inline=False),interactions.EmbedField(name="Next Ligma Outbreak Location",value=randomloc,inline=False),interactions.EmbedField(name="Crossroads",value=crossroadsdamage,inline=False),interactions.EmbedField(name="Dungeon",value=dungeondamage,inline=False),interactions.EmbedField(name="Farmland",value=farmlanddamage,inline=False),interactions.EmbedField(name="Keep",value=keepdamage,inline=False),interactions.EmbedField(name="Lich's Castle",value=lichdamage,inline=False),interactions.EmbedField(name="Shop",value=shopdamage,inline=False),interactions.EmbedField(name="Tavern",value=taverndamage,inline=False)],
    )
    await channel.send(embeds=ligmaemb)


@bot.command(
    name="wightspawn",
    description="create a 1hp Wight you can order around.",
    scope = guildid
)
async def wightspawn(ctx: interactions.CommandContext):
    players = await getplayerdata ()
    current_time = int(time.time())
    if players[str(ctx.author.id)]['Location'] == "Dead":
        if players[str(ctx.author.id)]['Mana'] == 3:
            players["Wight - "+str(ctx.author.id)] ={}
            players["Wight - "+str(ctx.author.id)]["Username"] = "Wight - "+str(players[str(ctx.author.id)]['Username'])
            players["Wight - "+str(ctx.author.id)]["Mana"] = 3
            players["Wight - "+str(ctx.author.id)]["HP"] = 1
            players["Wight - "+str(ctx.author.id)]["Location"] = "Crossroads"
            players["Wight - "+str(ctx.author.id)]["SC"] = 0
            players["Wight - "+str(ctx.author.id)]["Rage"] = 0
            players["Wight - "+str(ctx.author.id)]["InitManaDate"] = current_time + basecd
            players["Wight - "+str(ctx.author.id)]["NextMana"] = current_time + basecd
            players["Wight - "+str(ctx.author.id)]["ReadyInventory"] = " "
            players["Wight - "+str(ctx.author.id)]["EquippedInventory"] = " "
            players["Wight - "+str(ctx.author.id)]["ReadyDate"] = current_time
            players["Wight - "+str(ctx.author.id)]["Lastactiontime"] = current_time
            players["Wight - "+str(ctx.author.id)]["Lastaction"] = "start"
            players["Wight - "+str(ctx.author.id)]["Nextaction"] = ""
            players["Wight - "+str(ctx.author.id)]["RestTimer"] = current_time
            players["Wight - "+str(ctx.author.id)]["EvadeTimer"] = current_time
            players["Wight - "+str(ctx.author.id)]["Team"] = players["Wight - "+str(ctx.author.id)]["Username"]+"'s team"
            players["Wight - "+str(ctx.author.id)]["NewTeam"] = "No Team"
            players["Wight - "+str(ctx.author.id)]["BountyReward"] = 3
            players["Wight - "+str(ctx.author.id)]["Orders"] = ""
            players["Wight - "+str(ctx.author.id)]["OrderDate"] = 0
            players["Wight - "+str(ctx.author.id)]["OptOutOrder"] = "No"
            players["Wight - "+str(ctx.author.id)]["ResetHealCap"] = 0
            players["Wight - "+str(ctx.author.id)]["ResetDamageCap"] = 0
            players["Wight - "+str(ctx.author.id)]["HealCap"] = 4200
            players["Wight - "+str(ctx.author.id)]["DamageCap"] = 6900
            username = players["Wight - "+str(ctx.author.id)]["Username"]
            players[str(ctx.author.id)]['Mana'] = 0
            with open("players.json","w") as f:
                json.dump(players,f, indent=4)
            wightspawnimage = interactions.EmbedImageStruct(
                                url="https://thumbs.gfycat.com/IdioticAbleLeafbird-max-1mb.gif",
                                height = 512,
                                width = 512,
                                )
            wightspawnemb = interactions.api.models.message.Embed(
                title = f"{players[str(ctx.author.id)]['Username']} has spawned a wight in the Crossroads!",
                color = 0x34b7eb,
                description = f"<@{ctx.author.id}> spent three undead mana to spawn a wight!!",
                image = wightspawnimage,
            )
            crosschannel = await interactions.get(bot, interactions.Channel, object_id=1044668622829797406 , force='http')
            await crosschannel.send(embeds = wightspawnemb)
            await ctx.send(f"You have spent three of your undead mana to create **{username}**! \n\nOrder it with `/wightattack` or `/wighttravel`", ephemeral=True)
        else:
            mana = players[str(ctx.author.id)]['Mana']
            username = "Wight - "+players[str(ctx.author.id)]['Username']
            await ctx.send(f"You only have {mana} undead mana. You need three to create **{username}**!", ephemeral=True)
    else:
        await ctx.send("You must be dead to use this command!", ephemeral=True)

@bot.command(
    name="wightattack",
    description="1 mana. attack a player in the wight's area for 69 damage.",
    scope = guildid,
    options=[
        interactions.Option(
            type=interactions.OptionType.STRING,
            name="playertarget",
            description="start typing who you want to attack",
            required=True,
            autocomplete=True,
        )
    ]
)
async def wightattack(ctx: interactions.CommandContext, playertarget: str):
    players = await getplayerdata()
    current_time = int(time.time())
    print(f"{playertarget} is the player target")
    for k,v in players.items():
        if v['Username']==str(playertarget):
            targetid=k
    print(f"{targetid} is the player target id")
    channelid=ctx.channel_id
    authorid = ctx.author.id
    wightid = "Wight - "+str(authorid)
    if wightid in players:
        cost = 1
        Mana_pull = players[wightid]["Mana"]
        nextmana = players[wightid]["NextMana"]
        if cost-Mana_pull > 0:
            await ctx.send(f"Your wight doesn't have the mana for that!\n\n The wight will have mana at <t:{nextmana}>", ephemeral = True)
        elif players[wightid]["HP"] <= 0:
            await ctx.send(f"Your wight is dead resurrect it with `/wightspawn`!", ephemeral = True)
        else:
            manamoji = await manamojiconv(Mana_pull- cost)
            wightattackemb = interactions.api.models.message.Embed(
                title = f"Your wight attacks {players[str(targetid)]['Username']}!",
                color = 0x34b7eb,
                fields = [interactions.EmbedField(name="Mana Remaining",value=manamoji,inline=True)],
            )
            await ctx.send(embeds=wightattackemb,ephemeral = True)
            #dowightattack
            wightattackurl = "https://icallbushwa.files.wordpress.com/2016/05/giphy-4.gif?w=316"
            players = await getplayerdata()
            players[wightid]["Nextaction"] = ""
            current_time = int(time.time())
            user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
            location = players[wightid]["Location"]
            channelid = locations[str(location)]["Channel_ID"]
            evading = False
            TeamPull = players[wightid]["Team"]
            if TeamPull == "No Team":
                TeamPull = "Null"
            if (players[str(targetid)]["Location"] == players[wightid]["Location"]) and (players[str(targetid)]["Team"] != TeamPull):
                if "EvadeTimer" in players[str(targetid)] :
                    if current_time < players[str(targetid)]["EvadeTimer"]:
                        evading = True
                        print("evading")
                if evading:
                    players = await getplayerdata()
                    damage = 0
                    targethp = players[str(targetid)]["HP"] - damage
                    critroll = 0
                    players[str(targetid)]["HP"] = targethp
                    players[wightid]["Mana"] = players[wightid]["Mana"] -1
                    players[wightid]["Lastaction"] = "wightattack"
                    hpmoji = await hpmojiconv(targethp)
                    with open("players.json", "w") as f:
                        json.dump(players, f, indent=4)
                else:
                    players = await getplayerdata()
                    damage = 69
                    targethp = players[str(targetid)]["HP"] - damage
                    players[str(targetid)]["HP"] = targethp
                    players[str(wightid)]["Mana"] = players[str(wightid)]["Mana"] -1
                    players[str(wightid)]["Lastaction"] = "wightattack"
                    hpmoji = await hpmojiconv(targethp)
                    with open("players.json", "w") as f:
                        json.dump(players, f, indent=4)
                wightattackimage = interactions.EmbedImageStruct(
                                    url=wightattackurl,
                                    height = 512,
                                    width = 512,
                                    )
                wightattackemb = interactions.api.models.message.Embed(
                    title = f"{players[str(authorid)]['Username']} wight attacks {players[str(targetid)]['Username']}!",
                    color = 0x34b7eb,
                    description = f"<@{authorid}> threw a quick wight attack at <@{targetid}>!",
                    image = wightattackimage,
                )
                attackerchannel=str(locations[players[wightid]["Location"]]["Channel_ID"])
                channel = await interactions.get(bot, interactions.Channel, object_id=attackerchannel , force='http')
                await channel.send(embeds=wightattackemb)
                wightattackprivemb = interactions.api.models.message.Embed(
                    title = f"{players[str(authorid)]['Username']} wight attacked {players[str(targetid)]['Username']}!",
                    color = 0x34b7eb,
                    description = f"<@{authorid}> throws a quick wight attack at <@{targetid}>!",
                    image = wightattackimage,
                )
                try:
                    user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
                    await user.send(embeds=wightattackprivemb)
                except:
                    print(f"{authorid} not valid user to DM")
                try:
                    user2 = await interactions.get(bot, interactions.Member, object_id=targetid, guild_id=guildid, force='http')
                    await user2.send(embeds=wightattackprivemb)
                except:
                    print(f"{targetid} not valid user to DM")
                await deadcheck(targethp,targetid,authorid,players)
            else:
                try:
                    user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
                    await user.send(f"Your Wight did not attack <@{targetid}> they are no longer a valid target!", ephemeral = True)
                except:
                    print(f"{authorid} not valid user to DM")
    else:
        await ctx.send(f"You don't have a wight to command!" , ephemeral = True)


@bot.autocomplete("wightattack", "playertarget")
async def wight_autocomplete(ctx: interactions.CommandContext, value: str = ""):
    players = await getplayerdata()
    authorid = ctx.author.id
    wightid = "Wight - "+str(authorid)
    LocationPull = players[str(wightid)]["Location"]
    sameLocationUserIDs = {k: v for k, v in players.items() if v['Location'] == LocationPull}
    if players[wightid]["Team"] == "No Team":
        TeamPull = "Null"
    else:
        TeamPull = players[wightid]["Team"]
    sameLocationUsernames = [v["Username"] for v in players.values() if v['Location'] == LocationPull and v['Team'] != TeamPull]
    print (LocationPull)
    print (sameLocationUsernames)
    items = sameLocationUsernames
    choices = [
        interactions.Choice(name=item, value=item) for item in items if value.lower() in item.lower()
    ]
    await ctx.populate(choices)

@bot.command(
    name="wighttravel",
    description="1 mana. your wight travels.",
    scope = guildid,
    options=[
        interactions.Option(
            type=interactions.OptionType.STRING,
            name="traveltarget",
            description="start typing where you want your wight to travel to",
            required=True,
            autocomplete=True,
        )
    ]
)
async def wighttravel(ctx: interactions.CommandContext, traveltarget: str):
    players = await getplayerdata()
    current_time = int(time.time())
    print(f"{traveltarget} is the player target id")
    channelid=ctx.channel_id
    authorid = ctx.author.id
    wightid = "Wight - "+str(authorid)
    destination = traveltarget
    if wightid in players:
        cost = 1
        Mana_pull = players[wightid]["Mana"]
        if cost-Mana_pull > 0:
            nextmana =players[wightid]["NextMana"]
            await ctx.send(f"Your wight doesn't have the mana for that! \n\nThe wight will have mana at <t:{nextmana}>", ephemeral = True)
        elif players[wightid]["HP"] <= 0:
            await ctx.send(f"Your wight is dead resurrect it with `/wightspawn`!", ephemeral = True)
        else:
            travelurl = "https://media.tenor.com/Wm6TRmkD-_IAAAAC/juggernaut-xmen.gif"
            players[wightid]["Nextaction"] = ""
            current_time = int(time.time())
            user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
            travelimg = interactions.EmbedImageStruct(
                                url=travelurl,
                                height = 512,
                                width = 512,
                                )
            if players[wightid]["Location"] == "Crossroads" or destination == "Crossroads":
                oldtravelerchannel=str(locations[players[wightid]["Location"]]["Channel_ID"])
                oldlocation = players[wightid]["Location"]
                newlocation = destination
                players[wightid]["Mana"] = players[wightid]["Mana"] -1
                players[wightid]["Lastaction"] = "travelto"
                players[wightid]["Location"] = destination
                with open("players.json", "w") as f:
                    json.dump(players, f, indent=4)
                newtravelerchannel=str(locations[players[wightid]["Location"]]["Channel_ID"])
                travelemb = interactions.api.models.message.Embed(
                    title = f"{players[wightid]['Username']} arrives at the {newlocation}!",
                    color = 0xad7205,
                    description = f"{players[wightid]['Username']} saunters over from the {oldlocation}!",
                    image = travelimg,
                    fields = [interactions.EmbedField(name="Old Location",value=oldlocation,inline=True),interactions.EmbedField(name="New Location",value=newlocation,inline=True)],
                )
                newchannel = await interactions.get(bot, interactions.Channel, object_id=newtravelerchannel , force='http')
                oldchannel = await interactions.get(bot, interactions.Channel, object_id=oldtravelerchannel , force='http')
                await newchannel.send(embeds=travelemb)
                travelurl = "https://media.tenor.com/IvLly3CfFLIAAAAC/juggernaut-xmen.gif"
                travelimg = interactions.EmbedImageStruct(
                                    url=travelurl,
                                    height = 512,
                                    width = 512,
                                    )
                travelemb = interactions.api.models.message.Embed(
                    title = f"{players[wightid]['Username']} leaves the {oldlocation}!",
                    color = 0xad7205,
                    description = f"{players[wightid]['Username']} saunters over to the {newlocation}!",
                    image = travelimg,
                    fields = [interactions.EmbedField(name="Old Location",value=oldlocation,inline=True),interactions.EmbedField(name="New Location",value=newlocation,inline=True)],
                )
                await oldchannel.send(embeds=travelemb)
            else:
                user = await interactions.get(bot, interactions.Member, object_id=authorid, force='http')
                await send_message(f"You must travel to the Crossroads before you can travel there!", user_id=[user])
    else:
        await ctx.send(f"You don't have a wight to command!" , ephemeral = True)


@bot.autocomplete("wighttravel", "traveltarget")
async def wight_autocomplete(ctx: interactions.CommandContext, value: str = ""):
    players = await getplayerdata()
    authorid = ctx.author.id
    wightid = "Wight - "+str(authorid)
    if players[str(wightid)]["Location"] != "Crossroads":
        alloptions = ["Crossroads"]
    else:
        alloptions = ["Dungeon", "Farmland", "Keep", "Lich's Castle", "Shop", "Tavern"]
    items = alloptions
    choices = [
        interactions.Choice(name=item, value=item) for item in items if value.lower() in item.lower()
    ]
    await ctx.populate(choices)

@bot.event(name="on_message_create")
async def listen(message: interactions.Message):
    print(
        f"\nWe've received a message from {message.author.username} in {message.channel_id}. \nThe message is: \n\n{message.content}\n\nend content\n"
    )

async def deadcheck(targethp,targetid,authorid,players):
    print(f"\ndead?:{int(time.time())}")
    EquippedInventory_pull = players[targetid]["EquippedInventory"]
    targetlichprot = EquippedInventory_pull.count("lichitem")
    targetid = targetid
    if targethp <= 0:
        print(f"\nthe target died!")
        user = await interactions.get(bot, interactions.Member, object_id=targetid, guild_id=guildid, force='http')
        if targetlichprot > 0:
            players[targetid]["HP"] = 4200
            #replace first instance of item in user's readyinventory
            players[str(targetid)]["EquippedInventory"]=EquippedInventory_pull.replace('\n        lichitem',' ',1)
            await send_message(f"<@{targetid}> would have died because of <@{authorid}>, but they were protected by their equipped lich item! \n\nThat lichitem has since broken.", channel_id=[general])
        else:
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
            players[str(targetid)]["Team"] = "Dead"
            players[str(targetid)]["Nextaction"] = ""
            players[str(authorid)]["SC"] = players[str(authorid)]["SC"] + players[str(targetid)]["BountyReward"]
            print("BountyReward")
            print(players[str(targetid)]["BountyReward"])
            players[str(targetid)]["BountyReward"] = 0
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
    else:
        print(f"\nthe target didn't die!")

#rage heals 420 for each rage stack then decreases by 1
async def rage(authorid):
    current_time = int(time.time())
    rageplayers = await getplayerdata()
    heal = ((rageplayers[str(authorid)]["Rage"])*420)
    if rageplayers[str(authorid)]["ResetHealCap"] == 0:
        rageplayers[str(authorid)]["ResetHealCap"] = current_time + basecd
    heal = min(rageplayers[str(authorid)]["ResetHealCap"], heal)
    rageplayers[str(authorid)]["ResetHealCap"] = max(0,rageplayers[str(authorid)]["ResetHealCap"] - heal)
    rageplayers[str(authorid)]["HP"] = min(rageplayers[str(authorid)]["HP"] + heal,10000)
    #await send_message(f"You healed {ragehealing} from :fire: **Rage**!", user_id=authorid)
    rageplayers[str(authorid)]["Rage"] = max(rageplayers[str(authorid)]["Rage"] -1,0)
    with open("players.json","w") as f:
        json.dump(rageplayers,f, indent=4)
    return

#hpmojiconv function converts an hp number into a string of hp squares
async def hpmojiconv(hp):
    players = await getplayerdata()
    numofgreensqs = math.floor(hp/1000)
    numofredsqs = math.floor((10000-hp)/1000)
    yellowsq = math.ceil((hp-(numofgreensqs*1000))/1000)
    hpmoji = str(numofgreensqs*":green_square:")+(yellowsq*":yellow_square:")+str(numofredsqs*":red_square:")+f"({max(min((numofgreensqs*1000)+1,10000),0)}-{max(min((numofgreensqs*1000)+999,10000),0)})"
    return hpmoji

#manamojiconv
async def manamojiconv(mana):
    players = await getplayerdata()
    numofbluesq = math.floor(mana/1)
    numofpurpsq = math.floor((3-mana)/1)
    manamoji = str(numofbluesq*":blue_square:")+str(numofpurpsq*":purple_square:")+f"({numofbluesq}/3)"
    return manamoji

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

#pulls ligma.json into dict
async def getligmadata():
    with open("ligma.json","r") as h:
        ligma = json.load(h)
    return ligma

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

async def getreminderdata():
    with open("reminders.json","r") as m:
        reminders = json.load(m)
    return reminders

async def pollfornext():
    #run forever
    while True:
        print(f"\npolling for next:{int(time.time())}")
        players = await getplayerdata()
        shop = await getshopdata()
        for k,v in players.items():
            if v['Nextaction'] != "":
                words = players[k]['Nextaction'].split()
                if v['ReadyDate'] < int(time.time()):
                    #do the action
                    loop = asyncio.get_running_loop()
                    if len(words) == 1:
                        await loop.create_task(functiondict[words[0]](**{'authorid': k}))
                        print(f"{v['Username']} is doing {words[0]}")
                    elif words[0] == "use":
                        await loop.create_task(functiondict[words[0]](**{'authorid': k,'readyitem':words[1]}))
                        print(f"{v['Username']} is doing {words[0]} {words[1]}")
                    elif words[1] in players:
                        if len(words) == 3:
                            await loop.create_task(functiondict[words[0]]( **{'authorid':k,'targetid':words[1],'readyitem':words[2]}))
                            print(f"{v['Username']} is doing {words[0]} {players[words[1]]['Username']} {words[2]}")
                        else:
                            print(f"{v['Username']} is doing {words[0]} {players[words[1]]['Username']}")
                            await loop.create_task(functiondict[words[0]]( **{'authorid':k,'targetid':words[1]}))
                    elif words[1] in locations:
                        await loop.create_task(functiondict[words[0]]( **{'authorid':k,'destination':words[1]}))
                        print(f"{v['Username']} is doing {words[0]} {words[1]}")
                    elif words[1] in shop:
                        await loop.create_task(functiondict[words[0]]( **{'authorid':k,'itemtarget':words[1]}))
                        print(f"{v['Username']} is doing {words[0]} {words[1]}")
                    players = await getplayerdata()
                    players[k]['Nextaction'] = ""
                    with open("players.json", "w") as f:
                        json.dump(players, f, indent=4)
                else:
                    if len(words) == 1:
                        print(f"{v['Username']} is not ready to {words[0]}")
                    elif words[0] == "use":
                        print(f"{v['Username']} is not ready to {words[0]} {words[1]}")
                    elif words[1] in players:
                        if len(words) == 3:
                            print(f"{v['Username']} is not ready to {words[0]} {players[words[1]]['Username']} {words[2]}")
                        else:
                            print(f"{v['Username']} is not ready to {words[0]} {players[words[1]]['Username']}")
                    elif words[1] in locations:
                        print(f"{v['Username']} is not ready to {words[0]} {words[1]}")
                    elif words[1] in shop:
                        print(f"{v['Username']} is not ready to {words[0]} {words[1]}")
        await asyncio.sleep(60)

async def pollclock():
    #run forever
    while True:
        date_time = datetime.fromtimestamp(int(time.time()))
        print(f"\n\ncleantime: {date_time}")
        print(int(time.time()))
        await asyncio.sleep(15)

async def pollfororders():
    #run forever
    while True:
        print(f"\npolling for orders:{int(time.time())}")
        players = await getplayerdata()
        shop = await getshopdata()
        for k,v in players.items():
            if v['Orders'] != "" and v['Mana'] < 3:
                #clear orders if they have don't have 3 mana
                print(f"{v['Username']} has less than 3 mana and had their orders cleared")
                v['Orders'] = ""
                with open("players.json", "w") as f:
                    json.dump(players, f, indent=4)
            elif v['OptOutOrder'] == "Yes" or v['Location'] == "Dead":
                print(f"{v['Username']} is dead and or opted out of orders")
                v['Orders'] = ""
                with open("players.json", "w") as f:
                    json.dump(players, f, indent=4)
            elif v['Orders'] != "" and v['OrderDate'] == 0:
                #set an OrderDate if they don't have one
                v['OrderDate'] = v['NextMana'] - 600
                with open("players.json", "w") as f:
                    json.dump(players, f, indent=4)
            elif v['Orders'] != "":
                words = players[k]['Orders'].split()
                if v['OrderDate'] < int(time.time()):
                    #do the action
                    loop = asyncio.get_running_loop()
                    if len(words) == 1:
                        await loop.create_task(functiondict[words[0]](**{'authorid': k}))
                        print(f"{v['Username']} is doing {words[0]}")
                    elif words[0] == "use":
                        await loop.create_task(functiondict[words[0]](**{'authorid': k,'readyitem':words[1]}))
                        print(f"{v['Username']} is doing {words[0]} {words[1]}")
                    elif words[1] in players:
                        if len(words) == 3:
                            await loop.create_task(functiondict[words[0]]( **{'authorid':k,'targetid':words[1],'readyitem':words[2]}))
                            print(f"{v['Username']} is doing {words[0]} {players[words[1]]['Username']} {words[2]}")
                        else:
                            print(f"{v['Username']} is doing {words[0]} {players[words[1]]['Username']}")
                            await loop.create_task(functiondict[words[0]]( **{'authorid':k,'targetid':words[1]}))
                    elif words[1] in locations:
                        await loop.create_task(functiondict[words[0]]( **{'authorid':k,'destination':words[1]}))
                        print(f"{v['Username']} is doing {words[0]} {words[1]}")
                    elif words[1] in shop:
                        await loop.create_task(functiondict[words[0]]( **{'authorid':k,'itemtarget':words[1]}))
                        print(f"{v['Username']} is doing {words[0]} {words[1]}")
                    players = await getplayerdata()
                    players[k]['Orders'] = ""
                    players[k]['OrderDate']= 0
                    with open("players.json", "w") as f:
                        json.dump(players, f, indent=4)
                else:
                    if len(words) == 1:
                        print(f"{v['Username']} is not ready to {words[0]}")
                    elif words[0] == "use":
                        print(f"{v['Username']} is not ready to {words[0]} {words[1]}")
                    elif words[1] in players:
                        if len(words) == 3:
                            print(f"{v['Username']} is not ready to {words[0]} {players[words[1]]['Username']} {words[2]}")
                        else:
                            print(f"{v['Username']} is not ready to {words[0]} {players[words[1]]['Username']}")
                    elif words[1] in locations:
                        print(f"{v['Username']} is not ready to {words[0]} {words[1]}")
                    elif words[1] in shop:
                        print(f"{v['Username']} is not ready to {words[0]} {words[1]}")
        await asyncio.sleep(60)

async def pollformanagain():
    #run forever
    while True:
        print(f"\npolling for managain:{int(time.time())}")
        players = await getplayerdata()
        for k,v in players.items():
                if v['NextMana'] < int(time.time()):
                    #give mana
                    print(f"{v['Username']} is ready to gain a mana! {v['Mana']}/3")
                    v['NextMana'] = v['NextMana'] + basecd
                    v['Mana'] = min(v['Mana']+1,3)
                    with open("players.json","w") as f:
                        json.dump(players,f, indent=4)
        await asyncio.sleep(60)

async def pollforcaps():
    #run forever
    while True:
        print(f"\npolling for caps:{int(time.time())}")
        players = await getplayerdata()
        for k,v in players.items():
            if v['ResetHealCap'] == 0 :
                v['ResetHealCap'] = 0
            else:
                if v['ResetHealCap'] < int(time.time()):
                    print(f"{v['Username']} heal cap has been set to 4200")
                    v['HealCap'] = 4200
                    v['ResetHealCap'] = 0
                    with open("players.json","w") as f:
                        json.dump(players,f, indent=4)
            if v['ResetDamageCap'] == 0:
                v['ResetDamageCap'] = 0
            else:
                if v['ResetDamageCap'] < int(time.time()):
                    print(f"{v['Username']} damage cap has been set to 6900")
                    v['DamageCap'] = 6900
                    v['ResetDamageCap'] = 0
                    with open("players.json","w") as f:
                        json.dump(players,f, indent=4)
        await asyncio.sleep(60)

async def pollforligma():
    #run forever
    while True:
        print(f"\npolling for ligma:{int(time.time())}")
        ligma = await getligmadata()
        current_time = int(time.time())
        if current_time > ligma["ligmadate"]:
            await ligmaiterate()
        else:
            print ("no ligma iteration")
        await asyncio.sleep(60)

async def pollforbackup():
    #run forever
    while True:#wait 24h
        await asyncio.sleep(basecd*2)
        print(f"\nbacking up:{int(time.time())}")
        players = await getplayerdata()
        current_time = int(time.time())
        with open("playersbackup.json","w") as z:
            json.dump(players,z, indent=4)

async def pollformana():
    #run forever
    while True:
        current_time = int(time.time())
        currenttimeofday = (current_time % 86400) -14400 #seconds since midnight - timezone (eastern)
        print(f"currenttimeofday={currenttimeofday}")
        announcementtime = int((1*60*60*10.5)) #9:30am
        print(f"announcementtime={announcementtime}")
        timeuntilannounce = announcementtime - currenttimeofday
        print(f"timeuntilannounce={timeuntilannounce}")
        if announcementtime < currenttimeofday:
            await asyncio.sleep(int(timeuntilannounce+86400))
        else:
            await asyncio.sleep(int(timeuntilannounce))
        print(f"\npolling for mana:{int(time.time())}")
        players = await getplayerdata()
        readyplayers = [k for k, v in players.items() if v['Mana'] > 0 and v['Location'] != "Dead" and v["Nextaction"] == ""]
        reminders = await getreminderdata()
        for key in readyplayers:
          if key not in reminders:
            try:
                user = await interactions.get(bot, interactions.Member, object_id=key, guild_id=guildid, force='http')
                await user.send(f"You have mana to spend! \n\nStop receiving reminders with /reminders \n\nPlay the game and view prizes here:\nhttps://discord.gg/pZD2XTm7ye")
            except:
                print(f"{key} not valid user to DM for mana")
        #don't turn this on until the bot is not relaunching often
        await asyncio.sleep(int(1*60*60*10)) #timer


async def pollforqueue():
    #run forever
    while True:
        current_time = int(time.time())
        currenttimeofday = (current_time % 86400) -14400 #seconds since midnight - timezone
        print(f"currenttimeofday={currenttimeofday}")
        announcementtime = int((1*60*60*10.5)) #9:30am
        print(f"announcementtime={announcementtime}")
        timeuntilannounce = announcementtime - currenttimeofday
        print(f"timeuntilannounce={timeuntilannounce}")
        if announcementtime < currenttimeofday:
            await asyncio.sleep(int(timeuntilannounce+86400))
        else:
            await asyncio.sleep(int(timeuntilannounce))
        print(f"\npolling for no queue:{int(time.time())}")
        players = await getplayerdata()
        noqueueplayers = [k for k, v in players.items() if v['Nextaction'] == "" and v['Location'] != "Dead"]
        reminders = await getreminderdata()
        for key in noqueueplayers:
          if key not in reminders:
            print(key)
            try:
                user = await interactions.get(bot, interactions.Member, object_id=key, guild_id=guildid, force='http')
                await user.send(f"You have no queued action! \n\nStop receiving reminders with /reminders \n\nPlay the game and view prizes here:\nhttps://discord.gg/pZD2XTm7ye")
            except:
                print(f"{key} not valid user to DM for queue")
        await asyncio.sleep(int(1*60*60*10)) #timer

async def send_message(message : str, **kwargs):
    if('user_id' in kwargs.keys()):
        for targetid in kwargs['user_id']:
            try:
                user = await interactions.get(bot, interactions.Member, object_id=targetid, guild_id=guildid, force='http')
                await user.send(message)
            except:
                print(f"{targetid} not valid user to DM")
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
            await ctx.send(f"You already have a queued action: \n**{words[0]}**\n\nThis has been replaced by:\n**{displayaction}**", ephemeral=True)
        elif words[1] in players:
            await ctx.send(f"You already have a queued action: \n**{words[0]} {players[words[1]]['Username']}**\n\nThis has been replaced by:\n**{displayaction}**", ephemeral=True)
        elif words[1] in locations:
            await ctx.send(f"You already have a queued action: \n**{words[0]} {words[1]}**\n\nThis has been replaced by:\n**{displayaction}**", ephemeral=True)
    else:
        await ctx.send(f"Next action: {displayaction}", ephemeral=True)

    #write and dump the new playerdata
    #TODO combine this dump with into a single dump with the caller functions somehow
    players[ctx.author.id]["Nextaction"]=saveaction
    with open("players.json", "w") as f:
        json.dump(players, f, indent=4)

    return

async def queuenexttarget(commandname,ctx, actiontargetid, *argv):
    players = await getplayerdata()
    shop = await getshopdata ()
    print(argv)
    print(len(argv))
    #separate strings for printing to player and what we use (id)
    if len(argv) == 1:
        print("len argv = 1")
        print(argv[0])
        saveaction = f"{commandname} {actiontargetid} {argv[0]}"
    else:
        saveaction = f"{commandname} {actiontargetid}"
    displayactionnew = "displayerror"
    if actiontargetid in players:
        if len(argv) == 1:
            print("len argv = 1")
            print(argv[0])
            displayactionnew = f"{commandname} <@{actiontargetid}> {argv[0]}"
        else:
            displayactionnew = f"{commandname} <@{actiontargetid}>"
    #name here is a little misleading, but actiontargetid is actually the destination name in this context
    elif actiontargetid in locations:
        displayactionnew = saveaction
    elif actiontargetid in shop:
        displayactionnew = saveaction
    if players[ctx.author.id]["Nextaction"] != "":
        words = players[ctx.author.id]['Nextaction'].split()
        displayactionold = "displayactionolderror"
        print(f"New action is {displayactionnew}")
        if len(words) == 1:
            displayactionold = words[0]
            await ctx.send(f"You already have a queued action:\n**{displayactionold}** \n\nThis has been replaced by:\n**{displayactionnew}**", ephemeral=True)
        elif words[1] in players:

            if len(words) == 3:
                print(f"words len = 3 {words}")
                displayactionold = words[0] + " " + f"<@{words[1]}>" + " " + words[2]
                await ctx.send(f"You already have a queued action:\n**{displayactionold}** \n\nThis has been replaced by:\n**{displayactionnew}**", ephemeral=True)
            else:
                displayactionold = words[0] + " " + f"<@{words[1]}>"
                await ctx.send(f"You already have a queued action:\n**{displayactionold}** \n\nThis has been replaced by:\n**{displayactionnew}**", ephemeral=True)
        elif words[1] in locations:
                displayactionold = words[0] + " " + words[1]
                await ctx.send(f"You already have a queued action:\n**{displayactionold}** \n\nThis has been replaced by:\n**{displayactionnew}**", ephemeral=True)
        elif words[1] in shop:
                displayactionold = words[0] + " " + words[1]
                await ctx.send(f"You already have a queued action:\n**{displayactionold}** \n\nThis has been replaced by:\n**{displayactionnew}**", ephemeral=True)
    else:
        await ctx.send(f"Next action:\n**{displayactionnew}**", ephemeral = True)
    #write and dump the new playerdata
    #TODO combine this dump with into a single dump with the caller functions somehow
    players[ctx.author.id]["Nextaction"]=saveaction
    with open("players.json", "w") as f:
        json.dump(players, f, indent=4)
    return


@bot.command(
    name="order",
    description="give a teammate an order to execute before they fail to generate mana (due to the max mana).",
    scope = guildid,
    options=[
        interactions.Option(
            type=interactions.OptionType.STRING,
            name="orderee",
            description="start typing an `orderee` to order",
            required=True,
            autocomplete=True,
        ),
        interactions.Option(
            type=interactions.OptionType.STRING,
            name="action",
            description="start typing an `action` after you've input an orderee",
            required=True,
            autocomplete=True,
        ),
        interactions.Option(
            type=interactions.OptionType.STRING,
            name="target",
            description="start typing a `target` after you've input an orderee and an action",
            required=False,
            autocomplete=True,
        ),
        interactions.Option(
            type=interactions.OptionType.STRING,
            name="readyitem",
            description="start typing a `readyitem` after you've input an orderee, an exchange,and a target",
            required=False,
            autocomplete=True,
        )
    ]
)
async def order(ctx: interactions.CommandContext, orderee: str, action: str, target: str ="", readyitem: str =""):
    players = await getplayerdata()
    current_time = int(time.time())
    locationdict = {"Crossroads": "exchange","Dungeon":"loot", "Farmland":"farm", "Keep":"aid", "Lich's Castle":"battlelich", "Shop":"trade", "Tavern":"drink"}
    orders = action
    for k,v in players.items():
        if v['Username']==str(target):
            targetid = k
    for k,v in players.items():
        if v['Username']==str(orderee):
            ordereeid = k
    if players[str(ctx.author.id)]["Team"] == "No Team":
        TeamPull = "Null"
    else:
        TeamPull = players[str(ctx.author.id)]["Team"]

    #verify orderee
    if players[ordereeid]["Team"] != TeamPull:
        await ctx.send(f"Your orderee isn't on your team!", ephemeral = True)

    #verify locationaction
    elif (str(orders) in locationdict.values()) and (str(orders) not in locationdict[players[str(ordereeid)]["Location"]]) :
            print("orders fall outside of location action")
            print(locationdict[players[str(ordereeid)]["Location"]])
            await ctx.send(f"Your ordered a location action for a location where the orderee isn't!", ephemeral = True)

    #write loot
    elif action == "loot":
        players[str(ordereeid)]["Orders"] = "loot"
        with open("players.json", "w") as f:
            json.dump(players, f, indent=4)
        await ctx.send(f"Your ordered <@{ordereeid}> to {orders}!", ephemeral = True)

    #write farm
    elif action == "farm":
        players[str(ordereeid)]["Orders"] = "farm"
        with open("players.json", "w") as f:
            json.dump(players, f, indent=4)
        await ctx.send(f"Your ordered <@{ordereeid}> to {orders}!", ephemeral = True)

    #write battlelich
    elif action == "battlelich":
        players[str(ordereeid)]["Orders"] = "battlelich"
        with open("players.json", "w") as f:
            json.dump(players, f, indent=4)
        await ctx.send(f"Your ordered <@{ordereeid}> to {orders}!", ephemeral = True)

    #write drink
    elif action == "drink":
        players[str(ordereeid)]["Orders"] = "drink"
        with open("players.json", "w") as f:
            json.dump(players, f, indent=4)
        await ctx.send(f"Your ordered <@{ordereeid}> to {orders}!", ephemeral = True)

    #write rest
    elif action == "rest":
        players[str(ordereeid)]["Orders"] = "rest"
        with open("players.json", "w") as f:
            json.dump(players, f, indent=4)
        await ctx.send(f"Your ordered <@{ordereeid}> to {orders}!", ephemeral = True)

    #write evade
    elif action == "evade":
        players[str(ordereeid)]["Orders"] = "evade"
        with open("players.json", "w") as f:
            json.dump(players, f, indent=4)
        await ctx.send(f"Your ordered <@{ordereeid}> to {orders}!", ephemeral = True)

    #write trade
    elif action == "trade":
        SC_pull = players[str(ordereeid)]["SC"]
        cost = shop[str(target)]["Cost"]
        #verify item is affordable
        if cost > SC_Pull:
            await ctx.send(f"Your ordered <@{ordereeid}> to purchase {target}, but they can't afford it!\n It costs {cost} and they have {SC_Pull}!", ephemeral = True)
        else:
            players[str(ordereeid)]["Orders"] = "trade "+target
            with open("players.json", "w") as f:
                json.dump(players, f, indent=4)
            await ctx.send(f"Your ordered <@{ordereeid}> to {orders} <@{targetid}>!", ephemeral = True)

    #write lightattack
    elif action == "lightattack":
        players[str(ordereeid)]["Orders"] = "lightattack "+targetid
        with open("players.json", "w") as f:
            json.dump(players, f, indent=4)
        await ctx.send(f"Your ordered <@{ordereeid}> to {orders} <@{targetid}>!", ephemeral = True)

    #write heavyattack
    elif action == "heavyattack":
        players[str(ordereeid)]["Orders"] = "heavyattack "+targetid
        with open("players.json", "w") as f:
            json.dump(players, f, indent=4)
        await ctx.send(f"Your ordered <@{ordereeid}> to {orders} <@{targetid}>!", ephemeral = True)

    #write interrupt
    elif action == "interrupt":
        players[str(ordereeid)]["Orders"] = "interrupt "+targetid
        with open("players.json", "w") as f:
            json.dump(players, f, indent=4)
        await ctx.send(f"Your ordered <@{ordereeid}> to {orders} <@{targetid}>!", ephemeral = True)

    #write travel
    elif action == "travel":
        players[str(ordereeid)]["Orders"] = "travel "+target
        with open("players.json", "w") as f:
            json.dump(players, f, indent=4)
        await ctx.send(f"Your ordered <@{ordereeid}> to {orders} to {target}!", ephemeral = True)

    #write use
    elif action == "use":
        players[str(ordereeid)]["Orders"] = "use "+target
        with open("players.json", "w") as f:
            json.dump(players, f, indent=4)
        await ctx.send(f"Your ordered <@{ordereeid}> to {orders} use their {target}!", ephemeral = True)

    #write aid
    elif action == "aid":
        players[str(ordereeid)]["Orders"] = "aid "+targetid
        with open("players.json", "w") as f:
            json.dump(players, f, indent=4)
        await ctx.send(f"Your ordered <@{ordereeid}> to {orders} <@{targetid}>!", ephemeral = True)

    #write exchange
    elif action == "exchange":
        players[str(ordereeid)]["Orders"] = "exchange "+targetid
        with open("players.json", "w") as f:
            json.dump(players, f, indent=4)
        await ctx.send(f"Your ordered <@{ordereeid}> to {orders} with <@{targetid}> and give them a {readyitem} !", ephemeral = True)


@bot.autocomplete("order", "orderee")
async def order_autocomplete(ctx: interactions.CommandContext, value: str = ""):
    players = await getplayerdata()
    if players[str(ctx.author.id)]["Team"] == "No Team":
        TeamPull = "Null"
    else:
        TeamPull = players[str(ctx.author.id)]["Team"]
    potentialorderees = [v["Username"] for v in players.values() if v['Team'] == TeamPull and v['Location'] != 'Dead']
    print("ordereeoptions")
    print(potentialorderees)
    ordereeoptions = potentialorderees
    alloptions = ordereeoptions
    items = alloptions
    choices = [
        interactions.Choice(name=item, value=item) for item in items if value.lower() in item.lower()
    ]
    await ctx.populate(choices)

@bot.autocomplete("order", "action")
async def order_autocomplete(ctx: interactions.CommandContext, value: str = ""):
    players = await getplayerdata()
    orderee = ctx.data.options[0].value
    orders = (o for o in ctx.data.options if o.name == "orders")
    ordereeid=""
    print(orderee)
    for k,v in players.items():
        if v['Username']==str(orderee):
            ordereeid=k
    if str(ordereeid) not in players:
        print("failed orderee")
        alloptions = [str(ctx.data.options[0])+ " --- ERROR --- Write the Orderee first!"]
    else:
        players = await getplayerdata()
        print(ordereeid)
        LocationPull = players[str(ordereeid)]['Location']
        if players[str(ordereeid)]["Team"] == "No Team":
            TeamPull = "Null"
        else:
            TeamPull = players[str(ordereeid)]["Team"]

        #attacktargets
        attacktargets = [v["Username"] for v in players.values() if v['Location'] == LocationPull and v['Team'] != TeamPull]

        #localtargets
        localtargets = [v["Username"] for v in players.values() if v['Location'] == LocationPull]

        #lightattack
        lightattackoptions =["lightattack"]
        print(lightattackoptions)

        #heavyattack
        heavyattackoptions =["heavyattack"]
        print(heavyattackoptions)

        #interrupt
        interruptoptions =["interrupt"]
        print(interruptoptions)

        #rest
        restoptions =["rest"]
        print(restoptions)

        #evade
        evadeoptions =["evade"]
        print(evadeoptions)

        #travel
        traveloptions =["travel"]
        print(traveloptions)

        #use
        useoptions =["use"]
        print(useoptions)

        #location
        locationoptions =[]
        locationdict = {"Crossroads": "exchange","Dungeon":"loot", "Farmland":"farm", "Keep":"aid", "Lich's Castle":"battlelich", "Shop":"trade", "Tavern":"drink"}
        for k,v in locationdict.items():
            if k==players[str(ordereeid)]['Location']:
                locationoptions=[v]
        print(locationoptions)

        alloptions =[]
        alloptions = locationoptions + evadeoptions + restoptions + traveloptions + useoptions + lightattackoptions + heavyattackoptions + interruptoptions
    print(alloptions)
    items = alloptions
    print(items)
    choices = [
        interactions.Choice(name=item, value=item) for item in items if value.lower() in item.lower()
    ]
    await ctx.populate(choices)

@bot.autocomplete("order", "target")
async def order_autocomplete(ctx: interactions.CommandContext, value: str = ""):
    players = await getplayerdata()
    orderee = ctx.data.options[0].value
    orders = ctx.data.options[1].value
    ordereeid=""
    print(orderee)
    locationdict = {"Crossroads": "exchange","Dungeon":"loot", "Farmland":"farm", "Keep":"aid", "Lich's Castle":"battlelich", "Shop":"trade", "Tavern":"drink"}
    print(locationdict.values())
    for k,v in players.items():
        if v['Username']==str(orderee):
            ordereeid=k
    if str(ordereeid) not in players:
        print("failed orderee")
        alloptions = [str(ctx.data.options[0].value)+ " --- ERROR --- Write the Orderee first!"]
    elif (str(orders) in locationdict.values()) and (str(orders) not in locationdict[players[str(ordereeid)]["Location"]]) :
            print("orders fall outside of location action")
            print(locationdict[players[str(ordereeid)]["Location"]])
            alloptions = [" --- ERROR --- orders location based and orderee is in the wrong location!"]
    else:
        players = await getplayerdata()
        print(ordereeid)
        LocationPull = players[str(ordereeid)]['Location']
        if players[str(ordereeid)]["Team"] == "No Team":
            TeamPull = "Null"
        else:
            TeamPull = players[str(ordereeid)]["Team"]
        if orders == "lightattack" or orders == "heavyattack" or orders == "interrupt":
            alloptions = [v["Username"] for v in players.values() if v['Location'] == LocationPull and v['Team'] != TeamPull]
        elif orders == "exchange":
            alloptions = [v["Username"] for v in players.values() if v['Location'] == LocationPull]
        elif orders == "aid":
            alloptions = [v["Username"] for v in players.values() if v['Location'] != "Dead"]
        elif orders == "travel":
            if players[str(ordereeid)]["Location"] != "Crossroads":
                alloptions = ["Crossroads"]
            else:
                alloptions = ["Dungeon", "Farmland", "Keep", "Lich's Castle", "Shop", "Tavern"]
        elif orders == "evade":
            alloptions = [" --- ERROR --- delete this option!"]
        elif orders == "rest":
            alloptions = [" --- ERROR --- delete this option!"]
        elif orders == "use":
            ReadyInventory_pull = players[str(ordereeid)]["ReadyInventory"]
            readyitems = list(filter(None, list(ReadyInventory_pull.split("\n        "))))
            alloptions =[]
            for item in readyitems:
                alloptions.append(item)
        elif orders == "trade":
            shop = await getshopdata()
            itemnames = [v for v in shop.keys()]
            print (itemnames)
            alloptions = itemnames
        else:
            alloptions = [" --- ERROR --- orders are invalid! Rewrite the whole command!"]
    items = alloptions
    print(items)
    choices = [
        interactions.Choice(name=item, value=item) for item in items if value.lower() in item.lower()
    ]
    await ctx.populate(choices)

@bot.autocomplete("order", "readyitem")
async def order_autocomplete(ctx: interactions.CommandContext, value: str = ""):
    players = await getplayerdata()
    orderee = ctx.data.options[0].value
    orders = ctx.data.options[1].value
    ordereeid=""
    print(orderee)
    locationdict = {"Crossroads": "exchange","Dungeon":"loot", "Farmland":"farm", "Keep":"aid", "Lich's Castle":"battlelich", "Shop":"trade", "Tavern":"drink"}
    print(locationdict.values())
    for k,v in players.items():
        if v['Username']==str(orderee):
            ordereeid=k
    if str(ordereeid) not in players:
        print("failed orderee")
        alloptions = [str(ctx.data.options[0].value)+ " --- ERROR --- Write the Orderee first!"]
    elif str(orders) != "exchange":
            print("orders fall outside of exchange")
            alloptions = [" --- ERROR --- You are not exchanging, do not provide this option."]
    else:
        ReadyInventory_pull = players[str(ordereeid)]["ReadyInventory"]
        readyitems = list(filter(None, list(ReadyInventory_pull.split("\n        "))))
        alloptions=[]
        for i in readyitems:
            alloptions.append(i)
    items = alloptions
    print(items)
    choices = [
        interactions.Choice(name=item, value=item) for item in items if value.lower() in item.lower()
    ]
    await ctx.populate(choices)


#light attack is below
async def dolightattack(authorid,targetid):
    lightattackurl = "https://media.tenor.com/nmEa-Paa3XgAAAAd/the-slap2-slap.gif"
    players = await getplayerdata()
    players[str(authorid)]["Nextaction"] = ""
    current_time = int(time.time())
    user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
    location = players[str(authorid)]["Location"]
    channelid = locations[str(location)]["Channel_ID"]
    evading = False
    TeamPull = players[str(authorid)]["Team"]
    prettytargetid = "<@"+str(targetid)+">"
    realtargetid = targetid
    if TeamPull == "No Team":
        TeamPull = "Null"
    if (players[str(targetid)]["Location"] == players[str(authorid)]["Location"]) and (players[str(targetid)]["Team"] != TeamPull):
        if "EvadeTimer" in players[str(targetid)] :
            if current_time < players[str(targetid)]["EvadeTimer"]:
                evading = True
                print("evading")
        if evading:
            await rage(authorid)
            players = await getplayerdata()
            damage = 0
            targethp = players[str(targetid)]["HP"] - damage
            critroll = 0
            players[str(targetid)]["HP"] = targethp
            players[str(authorid)]["Rage"] = players[str(authorid)]["Rage"] +1
            players[str(authorid)]["Mana"] = players[str(authorid)]["Mana"] -1
            players[str(authorid)]["Lastaction"] = "lightattack"
            hpmoji = await hpmojiconv(targethp)
            with open("players.json", "w") as f:
                json.dump(players, f, indent=4)
        else:
            await rage(authorid)
            players = await getplayerdata()
            EquippedInventory_pull = players[str(authorid)]["EquippedInventory"]
            damageroll = random.randint(0, 300)
            critroll = random.randint(1, 10) + EquippedInventory_pull.count("critterihardlyknowher")
            if critroll >= 10:
                critdmg = math.ceil(950/2)
            else:
                critdmg = 0
            damage = 800 + damageroll + (EquippedInventory_pull.count("drinkingmedal") * 420)+ critdmg
            if players[str(targetid)]["ResetDamageCap"] == 0:
                players[str(targetid)]["ResetDamageCap"] = current_time + basecd
            damage = min(players[str(targetid)]["DamageCap"],damage)
            players[str(targetid)]["DamageCap"] = max(0,players[str(targetid)]["DamageCap"]-damage)
            targethp = players[str(targetid)]["HP"] - damage
            players[str(targetid)]["HP"] = targethp
            players[str(authorid)]["Rage"] = players[str(authorid)]["Rage"] +1
            players[str(authorid)]["Mana"] = players[str(authorid)]["Mana"] -1
            if str("Wight - ") in str(players[str(targetid)]):
                print("Target is a wight")
                prettytargetid = "<@"+str(targetid[8:])+">'s Wight"
                realtargetid = targetid[8:]
                await send_message(f"{prettytargetid} died because of <@{authorid}>!", channel_id=[general])
                ligma = await getligmadata()
                ligma[players[str(targetid)]["Location"]] = ligma[players[str(targetid)]["Location"]] +1
                with open("ligma.json","w") as h:
                   json.dump(ligma, h, indent=4)
                players[str(targetid)]["Location"] = "Dead"
                bounty = players[str(targetid)]["BountyReward"]
                players[str(authorid)]["SC"] = players[str(authorid)]["SC"] + bounty
            else:
                players[str(authorid)]["Mana"] = players[str(authorid)]["Mana"]
            players[str(authorid)]["Lastaction"] = "lightattack"
            hpmoji = await hpmojiconv(targethp)
            with open("players.json", "w") as f:
                json.dump(players, f, indent=4)
            if critroll >= 10:
                crit = "**CRITICAL HIT!\n\n**"
            else:
                print("nocrit")
                crit = ""
        lightattackimage = interactions.EmbedImageStruct(
                            url=lightattackurl,
                            height = 512,
                            width = 512,
                            )
        critrollstr = str((critroll-EquippedInventory_pull.count("critterihardlyknowher")))+" + "+str(EquippedInventory_pull.count("critterihardlyknowher"))
        lightattackemb = interactions.api.models.message.Embed(
            title = f"{players[str(authorid)]['Username']} light attacks {players[str(targetid)]['Username']}!",
            color = 0x34b7eb,
            description = f"{crit}<@{authorid}> threw a quick jab at <@{targetid}>!",
            image = lightattackimage,
            fields = [interactions.EmbedField(name="Crit Roll",value=critrollstr,inline=True)],
        )
        attackerchannel=str(locations[players[str(authorid)]["Location"]]["Channel_ID"])
        channel = await interactions.get(bot, interactions.Channel, object_id=attackerchannel , force='http')
        await channel.send(embeds=lightattackemb)
        lightattackprivemb = interactions.api.models.message.Embed(
            title = f"{players[str(authorid)]['Username']} light attacked {players[str(targetid)]['Username']}!",
            color = 0x34b7eb,
            description = f"{crit}<@{authorid}> throws a quick jab at <@{targetid}>!",
            image = lightattackimage,
            fields = [interactions.EmbedField(name="Crit Roll",value=critrollstr,inline=True),interactions.EmbedField(name="Damage",value=damage, inline=True),interactions.EmbedField(name="Target HP",value=hpmoji,inline=False)],
        )
        try:
            user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
            await user.send(embeds=lightattackprivemb)
        except:
            print(f"{authorid} not valid user to DM for queue")
        try:
            user2 = await interactions.get(bot, interactions.Member, object_id=realtargetid, guild_id=guildid, force='http')
            await user2.send(embeds=lightattackprivemb)
        except:
            print(f"{realtargetid} not valid user to DM for queue")
        await deadcheck(targethp,targetid,authorid,players)
    else:
        try:
            user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
            await user.send(f"You did not lightattack <@{targetid}> they are no longer a valid target!")
        except:
            print(f"{authorid} not valid user to DM")

@bot.command(
    name="lightattack",
    description="1mana.1rage. attack a player in your area for 800 - 1100 damage.",
    scope = guildid,
    options=[
        interactions.Option(
            type=interactions.OptionType.STRING,
            name="playertarget",
            description="start typing who you want to attack",
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
        cost = 1
        Mana_pull = players[str(ctx.author.id)]["Mana"]
        if cost-Mana_pull > 0:
            enoughmanatime = (players[str(ctx.author.id)]["NextMana"])+(max((cost-Mana_pull-1),0))*basecd
            players[str(ctx.author.id)]["ReadyDate"] = enoughmanatime
            with open("players.json", "w") as f:
                json.dump(players, f, indent=4)
            await queuenexttarget("lightattack",ctx,targetid)
            await ctx.send(f"You don't have the mana for that!\n\nThe action has been queued for <t:{enoughmanatime}>.", ephemeral = True)
        else:
            manamoji = await manamojiconv(Mana_pull- cost)
            lightattackemb = interactions.api.models.message.Embed(
                title = f"You light attack {players[str(targetid)]['Username']}!",
                color = 0x34b7eb,
                fields = [interactions.EmbedField(name="Mana Remaining",value=manamoji,inline=True)],
            )
            await ctx.send(embeds=lightattackemb,ephemeral = True)
            await dolightattack(ctx.author.id,targetid)
    else:
        await ctx.send(f"You aren't in the competition!" , ephemeral = True)


@bot.autocomplete("lightattack", "playertarget")
async def light_autocomplete(ctx: interactions.CommandContext, value: str = ""):
    players = await getplayerdata()
    LocationPull = players[str(ctx.author.id)]["Location"]
    sameLocationUserIDs = {k: v for k, v in players.items() if v['Location'] == LocationPull}
    if players[str(ctx.author.id)]["Team"] == "No Team":
        TeamPull = "Null"
    else:
        TeamPull = players[str(ctx.author.id)]["Team"]
    sameLocationUsernames = [v["Username"] for v in players.values() if v['Location'] == LocationPull and v['Team'] != TeamPull]
    print (LocationPull)
    print (sameLocationUsernames)
    items = sameLocationUsernames
    choices = [
        interactions.Choice(name=item, value=item) for item in items if value.lower() in item.lower()
    ]
    await ctx.populate(choices)

#heavy attack is below
async def doheavyattack(authorid,targetid):
    heavyattackurl = "https://media.tenor.com/0dRjVrsqP8cAAAAC/smash-bros.gif"
    players = await getplayerdata()
    players[str(authorid)]["Nextaction"] = ""
    current_time = int(time.time())
    user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
    location = players[str(authorid)]["Location"]
    channelid = locations[str(location)]["Channel_ID"]
    evading = False
    TeamPull = players[str(authorid)]["Team"]
    prettytargetid = "<@"+str(targetid)+">"
    realtargetid = targetid
    if TeamPull == "No Team":
        TeamPull = "Null"
    if (players[str(targetid)]["Location"] == players[str(authorid)]["Location"]) and (players[str(targetid)]["Team"] != TeamPull):

        if "EvadeTimer" in players[str(targetid)] :
            if current_time < players[str(targetid)]["EvadeTimer"]:
                evading = True
                print("evading")
        if evading:
            await rage(authorid)
            players = await getplayerdata()
            damage = 0
            targethp = players[str(targetid)]["HP"] - damage
            players[str(targetid)]["HP"] = targethp
            players[str(authorid)]["Rage"] = players[str(authorid)]["Rage"] +6
            players[str(authorid)]["Mana"] = players[str(authorid)]["Mana"] -3 + min((EquippedInventory_pull.count("AWP")),1)
            players[str(authorid)]["Lastaction"] = "heavyattack"
            hpmoji = await hpmojiconv(targethp)
            with open("players.json", "w") as f:
                json.dump(players, f, indent=4)
        else:
            await rage(authorid)
            players = await getplayerdata()
            EquippedInventory_pull = players[str(authorid)]["EquippedInventory"]
            damageroll = random.randint(0, 300)
            critroll = random.randint(1, 10) + (EquippedInventory_pull.count("critterihardlyknowher") * 1)
            if critroll >= 10:
                critdmg = math.ceil(3650/2)
            else:
                critdmg = 0
            damage = 3500 + damageroll + critdmg
            if players[str(targetid)]["ResetDamageCap"] == 0:
                players[str(targetid)]["ResetDamageCap"] = current_time + basecd
            damage = min(players[str(targetid)]["DamageCap"],damage)
            players[str(targetid)]["DamageCap"] = max(0,players[str(targetid)]["DamageCap"]-damage)
            targethp = players[str(targetid)]["HP"] - damage
            players[str(targetid)]["HP"] = targethp
            players[str(authorid)]["Rage"] = players[str(authorid)]["Rage"] +6
            players[str(authorid)]["Mana"] = players[str(authorid)]["Mana"] -3 + min((EquippedInventory_pull.count("AWP")),1)
            if str("Wight - ") in str(players[str(targetid)]):
                print("Target is a wight")
                prettytargetid = "<@"+str(targetid[8:])+">'s Wight"
                realtargetid = targetid[8:]
                await send_message(f"{prettytargetid} died because of <@{authorid}>!", channel_id=[general])
                ligma = await getligmadata()
                ligma[players[str(targetid)]["Location"]] = ligma[players[str(targetid)]["Location"]] +1
                with open("ligma.json","w") as h:
                   json.dump(ligma, h, indent=4)
                players[str(targetid)]["Location"] = "Dead"
                bounty = players[str(targetid)]["BountyReward"]
                players[str(authorid)]["SC"] = players[str(authorid)]["SC"] + bounty
                prettytargetid = "<@"+str(targetid[8:])+">'s Wight"
                realtargetid = targetid[8:]
                await send_message(f"{prettytargetid} died because of <@{authorid}>!", channel_id=[general])
            else:
                players[str(authorid)]["Mana"] = players[str(authorid)]["Mana"]
            players[str(authorid)]["Lastaction"] = "heavyattack"
            hpmoji = await hpmojiconv(targethp)
            with open("players.json", "w") as f:
                json.dump(players, f, indent=4)
            if critroll >= 10:
                crit = "**CRITICAL HIT!\n\n**"
            else:
                print("nocrit")
                crit = ""
        heavyattackimage = interactions.EmbedImageStruct(
                            url=heavyattackurl,
                            height = 512,
                            width = 512,
                            )
        critrollstr = str((critroll-EquippedInventory_pull.count("critterihardlyknowher")))+" + "+str(EquippedInventory_pull.count("critterihardlyknowher"))
        heavyattackemb = interactions.api.models.message.Embed(
            title = f"{players[str(authorid)]['Username']} heavy attacks {players[str(targetid)]['Username']}!",
            color = 0xed8a34,
            description = f"{crit}<@{authorid}> takes a massive swing at <@{targetid}>!",
            image = heavyattackimage,
            fields = [interactions.EmbedField(name="Crit Roll",value=critrollstr,inline=True)],
        )
        attackerchannel=str(locations[players[str(authorid)]["Location"]]["Channel_ID"])
        channel = await interactions.get(bot, interactions.Channel, object_id=attackerchannel , force='http')
        await channel.send(embeds=heavyattackemb)
        heavyattackprivemb = interactions.api.models.message.Embed(
            title = f"{players[str(authorid)]['Username']} heavy attacked {players[str(targetid)]['Username']}!",
            color = 0xed8a34,
            description = f"{crit}<@{authorid}> takes a massive swing at <@{targetid}>!",
            image = heavyattackimage,
            fields = [interactions.EmbedField(name="Crit Roll",value=critrollstr,inline=True),interactions.EmbedField(name="Damage",value=damage, inline=True),interactions.EmbedField(name="Target HP",value=hpmoji,inline=False)],
        )
        await deadcheck(targethp,targetid,authorid,players)
        try:
            user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
            await user.send(embeds=heavyattackprivemb)
        except:
            print(f"{authorid} not valid user to DM")
        try:
            user2 = await interactions.get(bot, interactions.Member, object_id=realtargetid, guild_id=guildid, force='http')
            await user2.send(embeds=heavyattackprivemb)
        except:
            print(f"{targetid} not valid user to DM")
    else:
        try:
            user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
            await user.send(f"You did not heavyattack <@{targetid}> they are no longer a valid target!")
        except:
            print(f"{authorid} not valid user to DM")

@bot.command(
    name="heavyattack",
    description="3mana.6rage. attack a player in your area for 3500 - 3800 damage.",
    scope = guildid,
    options=[
        interactions.Option(
            type=interactions.OptionType.STRING,
            name="playertarget",
            description="start typing who you want to attack",
            required=True,
            autocomplete=True,
        )
    ]
)
async def heavyattack(ctx: interactions.CommandContext, playertarget: str):
    players = await getplayerdata()
    current_time = int(time.time())
    EquippedInventory_pull = players[str(ctx.author.id)]["EquippedInventory"]
    print(f"{playertarget} is the player target")
    for k, v in players.items():
        if v['Username'] == str(playertarget):
            targetid = k
    print(f"{targetid} is the player target id")
    channelid=ctx.channel_id
    if str(ctx.author.id) in players:
        cost = 3 - min((EquippedInventory_pull.count("AWP")),1)
        Mana_pull = players[str(ctx.author.id)]["Mana"]
        if cost-Mana_pull > 0:
            enoughmanatime = (players[str(ctx.author.id)]["NextMana"])+(max((cost-Mana_pull-1),0))*basecd
            players[str(ctx.author.id)]["ReadyDate"] = enoughmanatime
            with open("players.json", "w") as f:
                json.dump(players, f, indent=4)
            await queuenexttarget("heavyattack",ctx,targetid)
            await ctx.send(f"You don't have the mana for that! The action has been queued for <t:{enoughmanatime}>.", ephemeral = True)
        else:
            manamoji = await manamojiconv(Mana_pull- cost)
            heavyattackemb = interactions.api.models.message.Embed(
                title = f"You heavy attack {players[str(targetid)]['Username']}!",
                color = 0xed8a34,
                fields = [interactions.EmbedField(name="Mana Remaining",value=manamoji,inline=True)],
            )
            await ctx.send(embeds=heavyattackemb,ephemeral = True)
            await doheavyattack(ctx.author.id,targetid)
    else:
        await ctx.send(f"You aren't in the competition!", ephemeral=True)


@bot.autocomplete("heavyattack", "playertarget")
async def heavy_autocomplete(ctx: interactions.CommandContext, value: str = ""):
    players = await getplayerdata()
    LocationPull = players[str(ctx.author.id)]["Location"]
    sameLocationUserIDs = {k: v for k, v in players.items() if v['Location'] == LocationPull}
    if players[str(ctx.author.id)]["Team"] == "No Team":
        TeamPull = "Null"
    else:
        TeamPull = players[str(ctx.author.id)]["Team"]
    sameLocationUsernames = [v["Username"] for v in players.values() if v['Location'] == LocationPull and v['Team'] != TeamPull]
    print (LocationPull)
    print (sameLocationUsernames)
    items = sameLocationUsernames
    choices = [
        interactions.Choice(name=item, value=item) for item in items if value.lower() in item.lower()
    ]
    await ctx.populate(choices)

#interrupt is below
async def dointerrupt(authorid,targetid):
    await rage(authorid)
    interrupturl = "https://thumbs.gfycat.com/EnragedGleamingIberianmidwifetoad-max-1mb.gif"
    players = await getplayerdata()
    players[str(authorid)]["Nextaction"] = ""
    current_time = int(time.time())
    user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
    location = players[str(authorid)]["Location"]
    channelid = locations[str(location)]["Channel_ID"]
    players[str(authorid)]["Mana"] = players[str(authorid)]["Mana"] -1
    resting = False
    evading = False
    TeamPull = players[str(authorid)]["Team"]
    if TeamPull == "No Team":
        TeamPull = "Null"
    if (players[str(targetid)]["Location"] == players[str(authorid)]["Location"]) and (players[str(targetid)]["Team"] != TeamPull):
        if current_time < players[str(targetid)]["EvadeTimer"]:
            evading = True
            print("evading")
        if current_time < players[str(targetid)]["RestTimer"]:
            resting = True
            print("resting")
        if resting or evading:
            damage = 4200
            if players[str(targetid)]["ResetDamageCap"] == 0:
                players[str(targetid)]["ResetDamageCap"] = current_time + basecd
            damage = min(players[str(targetid)]["DamageCap"],damage)
            players[str(targetid)]["DamageCap"] = max(0,players[str(targetid)]["DamageCap"]-damage)
            targethp = players[str(targetid)]["HP"] - damage
            players[str(targetid)]["HP"] = targethp
            players[str(authorid)]["Lastaction"] = "interrupt"
            hpmoji = await hpmojiconv(targethp)
            players[str(targetid)]["RestTimer"] = current_time
            players[str(targetid)]["EvadeTimer"] = current_time
            with open("players.json", "w") as f:
                json.dump(players, f, indent=4)
        else:
            damage = 0
            targethp = players[str(targetid)]["HP"] - damage
            hpmoji = await hpmojiconv(targethp)
            players[str(authorid)]["Lastaction"] = "interrupt"
            with open("players.json", "w") as f:
                json.dump(players, f, indent=4)
        interruptimage = interactions.EmbedImageStruct(
                            url=interrupturl,
                            height = 512,
                            width = 512,
                            )
        oldnextaction = players[str(targetid)]["Nextaction"]
        newnextaction = ""
        players[str(targetid)]["Nextaction"] = ""
        desc = ""
        desc2 = ""
        removequeue = "No"
        if oldnextaction != newnextaction:
            desc = f"Removed the queued action: **{oldnextaction}**"
            removequeue = "Yes"
        if damage == 4200:
            desc2 = f"Target took 4200 damage and is no longer resting or evading."
        interruptemb = interactions.api.models.message.Embed(
            title = f"{players[str(authorid)]['Username']} tries to interrupt {players[str(targetid)]['Username']}!",
            color = 0x8541fa,
            description = f"<@{authorid}> makes distracting noises at <@{targetid}>!",
            image = interruptimage,
            fields = [interactions.EmbedField(name="Interrupted Queue:",value=removequeue,inline=True),interactions.EmbedField(name="Interrupted Damage:",value=damage,inline=True)],
            )
        attackerchannel=str(locations[players[str(authorid)]["Location"]]["Channel_ID"])
        channel = await interactions.get(bot, interactions.Channel, object_id=attackerchannel , force='http')
        await channel.send(embeds=interruptemb)
        interruptembpriv = interactions.api.models.message.Embed(
            title = f"{players[str(authorid)]['Username']} tries to interrupt {players[str(targetid)]['Username']}!",
            color = 0x8541fa,
            description = f"<@{authorid}> makes distracting noises at <@{targetid}>!\n\n{desc}",
            image = interruptimage,
            fields = [interactions.EmbedField(name="Interrupted Queue:",value=removequeue,inline=True)],
        )
        try:
            user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
            await user.send(embeds=interruptembpriv)
        except:
            print(f"{authorid} not valid user to DM")
        try:
            user2 = await interactions.get(bot, interactions.Member, object_id=targetid, guild_id=guildid, force='http')
            await user2.send(embeds=interruptembpriv)
        except:
            print(f"{targetid} not valid user to DM")
        await deadcheck(targethp,targetid,authorid,players)
        with open("players.json", "w") as f:
            json.dump(players, f, indent=4)
    else:
        try:
            user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
            await user.send(f"You did not interrupt <@{targetid}> they are no longer a valid target!")
        except:
            print(f"{targetid} not valid user to DM")

@bot.command(
    name="interrupt",
    description="1mana. 4200dmg to an opponent in your area if they are rest/evading. stop their queue/rest/evading.",
    scope = guildid,
    options=[
        interactions.Option(
            type=interactions.OptionType.STRING,
            name="playertarget",
            description="start typing who you want to interrupt",
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
        cost = 1
        Mana_pull = players[str(ctx.author.id)]["Mana"]
        if cost-Mana_pull > 0:
            enoughmanatime = (players[str(ctx.author.id)]["NextMana"])+(max((cost-Mana_pull-1),0))*basecd
            players[str(ctx.author.id)]["ReadyDate"] = enoughmanatime
            with open("players.json", "w") as f:
                json.dump(players, f, indent=4)
            await queuenexttarget("interrupt",ctx,targetid)
            await ctx.send(f"You don't have the mana for that! The action has been queued for <t:{enoughmanatime}>.", ephemeral = True)
        else:
            manamoji = await manamojiconv(Mana_pull- cost)
            interruptemb = interactions.api.models.message.Embed(
                title = f"You interrupt {players[str(targetid)]['Username']}!",
                color = 0x8541fa,
                fields = [interactions.EmbedField(name="Mana Remaining",value=manamoji,inline=True)],
            )
            await ctx.send(embeds=interruptemb,ephemeral = True)
            await dointerrupt(ctx.author.id,targetid)
    else:
        await ctx.send(f"You aren't in the competition!", ephemeral=True)

@bot.autocomplete("interrupt", "playertarget")
async def interrupt_autocomplete(ctx: interactions.CommandContext, value: str = ""):
    players = await getplayerdata()
    LocationPull = players[str(ctx.author.id)]["Location"]
    sameLocationUserIDs = {k: v for k, v in players.items() if v['Location'] == LocationPull}
    if players[str(ctx.author.id)]["Team"] == "No Team":
        TeamPull = "Null"
    else:
        TeamPull = players[str(ctx.author.id)]["Team"]
    sameLocationUsernames = [v["Username"] for v in players.values() if v['Location'] == LocationPull and v['Team'] != TeamPull]
    print (LocationPull)
    print (sameLocationUsernames)
    items = sameLocationUsernames
    choices = [
        interactions.Choice(name=item, value=item) for item in items if value.lower() in item.lower()
    ]
    await ctx.populate(choices)

#evade is below
async def doevade(authorid):
    await rage(authorid)
    evadeurl = "https://i.imgur.com/4CKqGIw.gif"
    players = await getplayerdata()
    players[str(authorid)]["Nextaction"] = ""
    current_time = int(time.time())
    user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
    location = players[str(authorid)]["Location"]
    channelid = locations[str(location)]["Channel_ID"]
    players[str(authorid)]["Mana"] = players[str(authorid)]["Mana"] -1
    players[str(authorid)]["Lastaction"] = "evade"
    players[str(authorid)]["Lastactiontime"] = current_time
    players[str(authorid)]["EvadeTimer"] = current_time + 86400
    with open("players.json", "w") as f:
        json.dump(players, f, indent=4)
    evadeimg = interactions.EmbedImageStruct(
                        url=evadeurl,
                        height = 512,
                        width = 512,
                        )
    evadeemb = interactions.api.models.message.Embed(
        title = f"{players[str(authorid)]['Username']} is now evading!",
        color = 0x41faaa,
        description = f"<@{authorid}> is dodging all hands until <t:{players[str(authorid)]['EvadeTimer']}>!",
        image = evadeimg,
        )
    try:
        user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
        await user.send(embeds=evadeemb)
    except:
        print(f"{authorid} not valid user to DM")

@bot.command(
    name="evade",
    description="1mana. you are evading for the next 24h receiving no dmg from light or heavy attacks",
    scope = guildid,
)
async def evade_command(ctx: interactions.CommandContext):
    players = await getplayerdata()
    channelid=ctx.channel_id
    if str(ctx.author.id) in players:
        cost = 1
        Mana_pull = players[str(ctx.author.id)]["Mana"]
        if cost-Mana_pull > 0:
            enoughmanatime = (players[str(ctx.author.id)]["NextMana"])+(max((cost-Mana_pull-1),0))*basecd
            players[str(ctx.author.id)]["ReadyDate"] = enoughmanatime
            with open("players.json", "w") as f:
                json.dump(players, f, indent=4)
            await queuenext(ctx)
            await ctx.send(f"You don't have the mana for that! The action has been queued for <t:{enoughmanatime}>.", ephemeral = True)
        else:
            manamoji = await manamojiconv(Mana_pull- cost)
            evadeemb = interactions.api.models.message.Embed(
                title = f"You begin evading!",
                color = 0x41faaa,
                fields = [interactions.EmbedField(name="Mana Remaining",value=manamoji,inline=True)],
            )
            await ctx.send(embeds=evadeemb,ephemeral = True)
            await doevade(ctx.author.id)
    else:
        await ctx.send(f"You aren't in the competition!" , ephemeral = True)

#rest is below
async def dorest(authorid):
    resturl = "https://media.tenor.com/WB1nsdk07-IAAAAC/yaziprint-0020cm.gif"
    players = await getplayerdata()
    current_time = int(time.time())
    players[str(authorid)]["Nextaction"] = ""
    user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
    location = players[str(authorid)]["Location"]
    channelid = locations[str(location)]["Channel_ID"]
    hp_pull = players[str(authorid)]["HP"]
    heal = math.ceil(int((10000 - hp_pull) / 2))
    if players[str(authorid)]["ResetHealCap"] == 0:
        players[str(authorid)]["ResetHealCap"] = current_time + basecd
    heal = min(players[str(authorid)]["ResetHealCap"],heal)
    players[str(authorid)]["ResetHealCap"] = max(0,players[str(authorid)]["ResetHealCap"]-heal)
    players[str(authorid)]["Mana"] = min(players[str(authorid)]["Mana"] + 1,3)
    mana_pull = players[str(authorid)]["Mana"]
    manamoji = await manamojiconv(mana_pull)
    players[str(authorid)]["Lastaction"] = "rest"
    players[str(authorid)]["Lastactiontime"] = current_time
    players[str(authorid)]["RestTimer"] = current_time + 86400
    players[str(authorid)]["HP"] = min(players[str(authorid)]["HP"] + heal, 10000)
    hpmoji = await hpmojiconv(players[str(authorid)]["HP"])
    with open("players.json", "w") as f:
        json.dump(players, f, indent=4)
    restimg = interactions.EmbedImageStruct(
                        url=resturl,
                        height = 512,
                        width = 512,
                        )
    restembpriv = interactions.api.models.message.Embed(
        title = f"{players[str(authorid)]['Username']} is now resting!",
        color = 0x05ad0b,
        description = f"<@{authorid}> is resting until <t:{players[str(authorid)]['RestTimer']}>, immediately gains 1 mana, and immediately heals half their missing health rounded up!\n\n*They may continue to take actions while resting, but they are susceptible to interrupt damage.*",
        image = restimg,
        fields = [interactions.EmbedField(name="Mana",value=manamoji,inline=True),interactions.EmbedField(name="HP",value=hpmoji,inline=True)],
        )
    try:
        user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
        await user.send(embeds=restembpriv)
    except:
        print(f"{authorid} not valid user to DM")
    restemb = interactions.api.models.message.Embed(
        title = f"{players[str(authorid)]['Username']} is now resting!",
        color = 0x05ad0b,
        description = f"<@{authorid}> is resting until <t:{players[str(authorid)]['RestTimer']}> and immediately gains 1 mana and heals half their missing health rounded up!\n\n*They may continue to take actions while resting, but they are susceptible to interrupt damage.*",
        image = restimg,
        )
    restchannel=str(locations[players[str(authorid)]["Location"]]["Channel_ID"])
    channel = await interactions.get(bot, interactions.Channel, object_id=restchannel , force='http')
    await channel.send(embeds=restemb)

@bot.command(
    name="rest",
    description="you rest for 24h, gain a mana, and heal half your missing health rounded up",
    scope = guildid,
)
async def rest_command(ctx: interactions.CommandContext):
    players = await getplayerdata()
    channelid=ctx.channel_id
    resting = False
    current_time = int(time.time())
    if current_time < players[str(ctx.author.id)]["RestTimer"]:
        resting = True
        print("resting")
    if str(ctx.author.id) in players:
        current_time = int(time.time())
        Lastaction_pull=players[str(ctx.author.id)]["Lastaction"]
        cost = -1
        Mana_pull = players[str(ctx.author.id)]["Mana"]
        if resting:
                manamoji = await manamojiconv(Mana_pull)
                resttimer = players[str(ctx.author.id)]["RestTimer"]
                restemb = interactions.api.models.message.Embed(
                    title = f"You cannot rest! You are still resting from your last rest!",
                    description = f"You must wait until <t:{resttimer}>, before you can rest!",
                    color = 0x05ad0b,
                    fields = [interactions.EmbedField(name="Mana Remaining",value=manamoji,inline=True)],
                )
                await ctx.send(embeds=restemb,ephemeral = True)
        else:
            manamoji = await manamojiconv(min(Mana_pull - cost,3))
            restemb = interactions.api.models.message.Embed(
                title = f"You rest!",
                color = 0x05ad0b,
                fields = [interactions.EmbedField(name="Mana Remaining",value=manamoji,inline=True)],
            )
            await ctx.send(embeds=restemb,ephemeral = True)
            await dorest(ctx.author.id)
    else:
        await ctx.send(f"You aren't in the competition!" , ephemeral = True)

#exchange is below
async def doexchange(authorid, targetid, readyitem):
    await rage(authorid)
    players = await getplayerdata()
    players[str(authorid)]["Nextaction"] = ""
    user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
    location = players[str(authorid)]["Location"]
    channelid = locations[str(location)]["Channel_ID"]
    current_time = int(time.time())
    EquippedInventory_pull = players[str(authorid)]["EquippedInventory"]
    print(f"{targetid} is the player target id")
    ReadyInventory_pull = str(players[str(authorid)]["ReadyInventory"])
    players[str(authorid)]["Mana"] = players[str(authorid)]["Mana"] -1
    players[str(authorid)]["Lastaction"] = "exchange"
    players[str(authorid)]["SC"] = players[str(authorid)]["SC"] + (EquippedInventory_pull.count("crookedabacus") * 1)
    players[str(targetid)]["ReadyInventory"] = players[str(targetid)]["ReadyInventory"]  + "\n        " + readyitem
    ReadyInventory_pull = str(players[str(authorid)]["ReadyInventory"])
    ReadyInventory_pull = ReadyInventory_pull.replace(str("\n        " +readyitem), "",1)
    players[str(authorid)]["ReadyInventory"] = ReadyInventory_pull
    with open("players.json","w") as f:
        json.dump(players,f, indent=4)
    exchangeurl = "https://media.tenor.com/838Jvd_ARZAAAAAd/exchange-luggage-delivery.gif"
    exchangeimg = interactions.EmbedImageStruct(
                        url=exchangeurl,
                        height = 512,
                        width = 512,
                        )
    exchangeemb = interactions.api.models.message.Embed(
        title = f"{players[str(authorid)]['Username']} gives {players[str(targetid)]['Username']} an item!",
        color = 0xbaaa1c,
        description = f"<@{authorid}> is in a corner shaking hands with <@{targetid}>!",
        image = exchangeimg,
    )
    exchangechannel=str(locations[players[str(authorid)]["Location"]]["Channel_ID"])
    channel = await interactions.get(bot, interactions.Channel, object_id=exchangechannel , force='http')
    await channel.send(embeds=exchangeemb)
    exchangeembpriv = interactions.api.models.message.Embed(
        title = f"{players[str(authorid)]['Username']} gives {players[str(targetid)]['Username']} an item!",
        color = 0xbaaa1c,
        description = f"<@{authorid}> is in a corner shaking hands with <@{targetid}>!",
        image = exchangeimg,
        fields = [interactions.EmbedField(name="Item Given",value=readyitem,inline=True)],
    )
    try:
        user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
        await user.send(embeds=exchangeembpriv)
    except:
        print(f"{authorid} not valid user to DM")
    try:
        user2 = await interactions.get(bot, interactions.Member, object_id=targetid, guild_id=guildid, force='http')
        await user2.send(embeds=exchangeembpriv)
    except:
        print(f"{targetid} not valid user to DM")

@bot.command(
    name="exchange",
    description="1mana. give a player in your area a ready item from your inventory.",
    scope = guildid,
    options=[
        interactions.Option(
            type=interactions.OptionType.STRING,
            name="playertarget",
            description="start typing who you want to give something to",
            required=True,
            autocomplete=True,
        ),
        interactions.Option(
            type=interactions.OptionType.STRING,
            name="readyitem",
            description="type the item you want to give",
            required=True,
            autocomplete=True,
        )
    ]
)
async def exchange(ctx: interactions.CommandContext, playertarget, readyitem: str):
    players = await getplayerdata()
    current_time = int(time.time())
    channelid=ctx.channel_id
    authorid=ctx.author.id
    print(f"{playertarget} is the player target")
    print(f"{readyitem} is the item target")
    cost = 1
    Mana_pull = players[str(ctx.author.id)]["Mana"]
    for k,v in players.items():
        if v['Username']==str(playertarget):
            targetid=k
    if str(authorid) in players:
        ReadyInventory_pull = str(players[str(ctx.author.id)]["ReadyInventory"])
        if locations["Crossroads"]["Role_ID"] not in ctx.author.roles:
            await ctx.send(f"You cannot exchange when you are not in the crossroads!", ephemeral=True)
        elif ReadyInventory_pull=="":
            await ctx.send(f"You don't have any items in your Ready Inventory!", ephemeral = True)
        elif cost-Mana_pull > 0:
            enoughmanatime = (players[str(ctx.author.id)]["NextMana"])+(max((cost-Mana_pull-1),0))*basecd
            players[str(ctx.author.id)]["ReadyDate"] = enoughmanatime
            with open("players.json", "w") as f:
                json.dump(players, f, indent=4)
            await queuenexttarget("exchange",ctx,targetid,readyitem)
            await ctx.send(f"You don't have the mana for that! The action has been queued for <t:{enoughmanatime}>.", ephemeral = True)
        else:
            manamoji = await manamojiconv(Mana_pull- cost)
            exchangeemb = interactions.api.models.message.Embed(
                title = f"You exchange with {players[str(targetid)]['Username']}!",
                color = 0xbaaa1c,
                fields = [interactions.EmbedField(name="Mana Remaining",value=manamoji,inline=True)],
            )
            await ctx.send(embeds=exchangeemb,ephemeral = True)
            await doexchange(ctx.author.id,targetid,readyitem)
    else:
        await ctx.send(f"You aren't in the competition!" , ephemeral = True)


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
        interactions.Choice(name=item, value=item) for item in items if value.lower() in item.lower()
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
        interactions.Choice(name=item, value=item) for item in items if value.lower() in item.lower()
    ]
    await ctx.populate(choices)

#farm is below
async def dofarm(authorid):
    await rage(authorid)
    players = await getplayerdata()
    players[str(authorid)]["Nextaction"] = ""
    current_time = int(time.time())
    EquippedInventory_pull=players[str(authorid)]["EquippedInventory"]
    user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
    location = players[str(authorid)]["Location"]
    channelid = locations[str(location)]["Channel_ID"]
    Lastaction_pull=players[str(authorid)]["Lastaction"]
    farmSC = int(random.randint(1, 4)) + (EquippedInventory_pull.count("tractor") * 1) + (Lastaction_pull.count("farm") * 1)
    SC_pull = players[str(authorid)]["SC"] + farmSC  # +randbuff
    players[str(authorid)]["SC"] = SC_pull #write to players
    cooldown = basecd * 1  # seconds in one day
    players[str(authorid)]["Mana"] = players[str(authorid)]["Mana"] -1
    players[str(authorid)]["Lastaction"] = "farm"
    with open("players.json", "w") as f:
        json.dump(players, f, indent=4)
    farmimg = interactions.EmbedImageStruct(
                        url="https://media.tenor.com/0CleP8SBHpgAAAAC/doja-cat-moo.gif",
                        height = 512,
                        width = 512,
                        )
    farmemb = interactions.api.models.message.Embed(
        title = f"{players[str(authorid)]['Username']} farms the land!",
        color = 0x2c3d00,
        description = f"<@{authorid}> works a sweat in those fields!",
        image = farmimg,
        fields = [interactions.EmbedField(name="Farmed SC",value=farmSC,inline=True)],
        )
    farmerchannel=str(locations[players[str(authorid)]["Location"]]["Channel_ID"])
    channel = await interactions.get(bot, interactions.Channel, object_id=farmerchannel , force='http')
    await channel.send(embeds=farmemb)

@bot.command(
    name="farm",
    description="1mana. roll 1d4 gain that many seed coins.",
    scope = guildid,
)
async def farm(ctx: interactions.CommandContext):
    players = await getplayerdata()
    current_time = int(time.time())
    channelid=ctx.channel_id
    authorid=ctx.author.id
    if str(authorid) in players:
        cost = 1
        Mana_pull = players[str(ctx.author.id)]["Mana"]
        if locations["Farmland"]["Role_ID"] not in ctx.author.roles:
            await ctx.send(f"You cannot farm when you are not in the farmland!", ephemeral=True)
        elif cost-Mana_pull > 0:
            enoughmanatime = (players[str(ctx.author.id)]["NextMana"])+(max((cost-Mana_pull-1),0))*basecd
            players[str(ctx.author.id)]["ReadyDate"] = enoughmanatime
            with open("players.json", "w") as f:
                json.dump(players, f, indent=4)
            await queuenext(ctx)
            await ctx.send(f"You don't have the mana for that! The action has been queued for <t:{enoughmanatime}>.", ephemeral = True)
        else:
            manamoji = await manamojiconv(Mana_pull- cost)
            farmemb = interactions.api.models.message.Embed(
                title = f"You farm!",
                color = 0x2c3d00,
                fields = [interactions.EmbedField(name="Mana Remaining",value=manamoji,inline=True)],
            )
            await ctx.send(embeds=farmemb,ephemeral = True)
            await dofarm(ctx.author.id)
    else:
        await ctx.send(f"You aren't in the competition!" , ephemeral = True)

#aid is below

async def doaid(authorid, targetid):
    await rage(authorid)
    players = await getplayerdata()
    players[str(authorid)]["Nextaction"] = ""
    user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
    location = players[str(authorid)]["Location"]
    channelid = locations[str(location)]["Channel_ID"]
    current_time = int(time.time())
    print(f"{targetid} is the player target")
    targethp=players[str(targetid)]["HP"]
    heal = min(math.ceil(int((10000 - targethp)/4)),10000)
    players[str(authorid)]["Mana"] = players[str(authorid)]["Mana"] -1
    players[str(authorid)]["Lastaction"] = "aid"
    players[str(targetid)]["HP"] = min(players[str(targetid)]["HP"] + heal, 10000)
    targethp=players[str(targetid)]["HP"]
    hpmoji = await hpmojiconv(targethp)
    with open("players.json","w") as f:
        json.dump(players,f, indent=4)
    aidimg = interactions.EmbedImageStruct(
                        url="https://media.tenor.com/5_-Wx7KMJIEAAAAC/ohyeah-hi.gif",
                        height = 512,
                        width = 512,
                        )
    aidemb = interactions.api.models.message.Embed(
        title = f"{players[str(authorid)]['Username']} aids {players[str(targetid)]['Username']}!",
        color = 0x2da66b,
        description = f"<@{authorid}> channels the Keep's strength into <@{targetid}> healing them!",
        image = aidimg,
        )
    aiderchannel=str(locations[players[str(authorid)]["Location"]]["Channel_ID"])
    aidedchannel=str(locations[players[str(targetid)]["Location"]]["Channel_ID"])
    channel = await interactions.get(bot, interactions.Channel, object_id=aiderchannel , force='http')
    await channel.send(embeds=aidemb)
    channel2 = await interactions.get(bot, interactions.Channel, object_id=aidedchannel , force='http')
    await channel2.send(embeds=aidemb)
    aidembpriv = interactions.api.models.message.Embed(
        title = f"{players[str(authorid)]['Username']} aids {players[str(targetid)]['Username']}!",
        color = 0x2da66b,
        description = f"<@{authorid}> channels the Keep's strength into <@{targetid}> healing them!",
        image = aidimg,
        fields = [interactions.EmbedField(name="Heal",value=heal,inline=True),interactions.EmbedField(name="New Target HP",value=hpmoji,inline=True)],
    )
    try:
        user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
        await user.send(embeds=aidembpriv)
    except:
        print(f"{authorid} not valid user to DM")
    try:
        user2 = await interactions.get(bot, interactions.Member, object_id=targetid, guild_id=guildid, force='http')
        await user2.send(embeds=aidembpriv)
    except:
        print(f"{targetid} not valid user to DM")

@bot.command(
    name="aid",
    description="1mana. heal chosen player 1/4 of their missing health.",
    scope = guildid,
    options=[
        interactions.Option(
            type=interactions.OptionType.STRING,
            name="playertarget",
            description="start typing who you want to aid",
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
    for k,v in players.items():
        if v['Username']==str(playertarget):
            targetid=k
    print(f"{targetid} is the player target id")
    if str(ctx.author.id) in players:
        cost = 1
        Mana_pull = players[str(ctx.author.id)]["Mana"]
        if locations["Keep"]["Role_ID"] not in ctx.author.roles:
            await ctx.send(f"You cannot aid when you are not in the keep!", ephemeral=True)
        elif cost-Mana_pull > 0:
            enoughmanatime = (players[str(ctx.author.id)]["NextMana"])+(max((cost-Mana_pull-1),0))*basecd
            players[str(ctx.author.id)]["ReadyDate"] = enoughmanatime
            with open("players.json", "w") as f:
                json.dump(players, f, indent=4)
            await queuenexttarget("aid",ctx,targetid)
            await ctx.send(f"You don't have the mana for that! The action has been queued for <t:{enoughmanatime}>.", ephemeral = True)
        else:
            manamoji = await manamojiconv(Mana_pull- cost)
            aidemb = interactions.api.models.message.Embed(
                title = f"You aid {players[str(targetid)]['Username']}!",
                color = 0x2da66b,
                fields = [interactions.EmbedField(name="Mana Remaining",value=manamoji,inline=True)],
            )
            await ctx.send(embeds=aidemb,ephemeral = True)
            await doaid(ctx.author.id,targetid)
    else:
        await ctx.send(f"You aren't in the competition!" , ephemeral = True)

@bot.autocomplete("aid", "playertarget")
async def aid_autocomplete(ctx: interactions.CommandContext, value: str = ""):
    players = await getplayerdata()
    Usernames = [v["Username"] for v in players.values() if v['Location'] != "Dead"]
    print (Usernames)
    items = Usernames
    choices = [
        interactions.Choice(name=item, value=item) for item in items if value.lower() in item.lower()
    ]
    await ctx.populate(choices)

#trade is below

async def dotrade(authorid, itemtarget):
    await rage(authorid)
    print("dotrade")
    print(f"{authorid}")
    print(f"{itemtarget}")
    players = await getplayerdata()
    players[str(authorid)]["Nextaction"] = ""
    shop = await getshopdata()
    current_time = int(time.time())
    user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
    location = players[str(authorid)]["Location"]
    channelid = locations[str(location)]["Channel_ID"]
    print(f"{itemtarget} is the player target")
    players[str(authorid)]["Mana"] = players[str(authorid)]["Mana"] -1
    players[str(authorid)]["Lastaction"] = "trade"
    #spend SC and gain abacus money
    EquippedInventory_pull = players[str(authorid)]["EquippedInventory"]
    cost = shop[str(itemtarget)]["Cost"]
    players[str(authorid)]["SC"] = players[str(authorid)]["SC"] - cost + (EquippedInventory_pull.count("crookedabacus") * 1)
    #add item to inventory
    players[str(authorid)]["ReadyInventory"] = players[str(authorid)]["ReadyInventory"] + "\n        "+itemtarget
    with open("players.json","w") as f:
        json.dump(players,f, indent=4)
    tradeimg = interactions.EmbedImageStruct(
                        url="https://media.tenor.com/mt-AI5e-0nsAAAAC/fry-shut-up-and-take-my-money.gif",
                        height = 512,
                        width = 512,
                        )
    tradeemb = interactions.api.models.message.Embed(
        title = f"{players[str(authorid)]['Username']} buys an item!",
        color = 0xfff700,
        image = tradeimg,
        description = f"<@{authorid}> haggles for a(n) {itemtarget}",
        fields = [interactions.EmbedField(name="Item Bought",value=itemtarget,inline=True)],
        )
    buyerchannel=str(locations[players[str(authorid)]["Location"]]["Channel_ID"])
    channel = await interactions.get(bot, interactions.Channel, object_id=buyerchannel , force='http')
    await channel.send(embeds=tradeemb)
    tradeembpriv = interactions.api.models.message.Embed(
        title = f"{players[str(authorid)]['Username']} buys an item!",
        color = 0xfff700,
        image = tradeimg,
        description = f"<@{authorid}> haggles for a {itemtarget}",
        fields = [interactions.EmbedField(name="Item Bought",value=itemtarget,inline=True),interactions.EmbedField(name="SC Remaining",value=players[str(authorid)]["SC"],inline=True)],
        )
    try:
        user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
        await user.send(embeds=tradeembpriv)
    except:
        print(f"{authorid} not valid user to DM")

@bot.command(
    name="trade",
    description="1mana. exchange seed coins for a shop item.",
    scope = guildid,
    options=[
        interactions.Option(
            type=interactions.OptionType.STRING,
            name="itemtarget",
            description="type what you want to buy",
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
        manacost = 1
        Mana_pull = players[str(ctx.author.id)]["Mana"]
        if locations["Shop"]["Role_ID"] not in ctx.author.roles:
            await ctx.send(f"You cannot trade when you are not in the Shop!", ephemeral=True)
        elif SC_pull < cost:
            await ctx.send(f"Your {SC_pull} seed coins are not able to purchase an item that costs {cost} seed coins! ", ephemeral = True)
        elif manacost-Mana_pull > 0:
            enoughmanatime = (players[str(ctx.author.id)]["NextMana"])+(max((manacost-Mana_pull-1),0))*basecd
            players[str(ctx.author.id)]["ReadyDate"] = enoughmanatime
            with open("players.json", "w") as f:
                json.dump(players, f, indent=4)
            await queuenexttarget("trade",ctx,itemtarget)
            await ctx.send(f"You don't have the mana for that! The action has been queued for <t:{enoughmanatime}>.", ephemeral = True)
        else:
            manamoji = await manamojiconv(Mana_pull - manacost)
            manaemb = interactions.api.models.message.Embed(
                title = f"You trade!",
                color = 0xfff700,
                fields = [interactions.EmbedField(name="Mana Remaining",value=manamoji,inline=True)],
            )
            await ctx.send(embeds=manaemb,ephemeral = True)
            await dotrade(ctx.author.id,itemtarget)
    else:
        await ctx.send(f"You aren't in the competition!" , ephemeral = True)

@bot.autocomplete("trade", "itemtarget")
async def trade_autocomplete(ctx: interactions.CommandContext, value: str = ""):
    print("trade")
    shop = await getshopdata()
    itemnames = [v for v in shop.keys()]
    print (itemnames)
    items = itemnames
    choices = [
        interactions.Choice(name=item, value=item) for item in items if value.lower() in item.lower()
    ]
    await ctx.populate(choices)

#drink is below

async def dodrink(authorid):
    await rage(authorid)
    players = await getplayerdata()
    players[str(authorid)]["Nextaction"] = ""
    scores = await gettaverndata()
    cooldown = basecd
    current_time = int(time.time())
    Lastaction_pull = players[str(authorid)]["Lastaction"]
    playerroll = int(int(random.randint(1,4)) + (Lastaction_pull.count("drink") * 1))
    scores[str(authorid)] = {}
    scores[str(authorid)]["Username"] = players[str(authorid)]["Username"]
    user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
    scores[str(authorid)]["Media"] = interactions.Member.get_avatar_url(user, guild_id=guildid)
    scores[str(authorid)]["Score"] = playerroll
    scores[str(authorid)]["Scoreexpiry"] = current_time+cooldown
    username = players[str(authorid)]["Username"]
    print(f"{username} is drinking")
    print(f"playerroll = {playerroll}")
    print(f"scores = \n{scores}\n")
    players[str(authorid)]["Mana"] = players[str(authorid)]["Mana"] -1
    players[str(authorid)]["Lastaction"] = "drink"
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
    highscoremedia = "https://i.imgur.com/Mt9swvj.png"
    for x in scores.values():
        if x["Score"] == highscore and x["Scoreexpiry"] > current_time:
            highscoremedia = x["Media"]
            highscorename = x["Username"]
    with open("tavern.json","w") as t:
        json.dump(scores,t, indent=4)
    print("Player Tavern Score Saved")
    #check if the max is greater than the player's roll
    if highscore > playerroll:
        print(f"playerscore is lower than highscore")
        highscoremedia = "https://i.imgur.com/Mt9swvj.png"
        for x in scores.values():
            if x["Score"] == highscore and x["Scoreexpiry"] > current_time:
                highscoremedia = x["Media"]
                highscorename = x["Username"]
        if lowscore == playerroll:
            damagedesc = "This roll is the lowest roll, they lose 1/4 of their current health!"
        else:
            damagedesc = "This roll is not the lowest roll, they heal for 1/4 of their current health!"
        drinktenorimage = interactions.EmbedImageStruct(
                            url=highscoremedia,
                            height = 375,
                            width = 500,
                            )
        drinktenor = interactions.api.models.message.Embed(
            title = f"Defeated by {highscorename}!",
            color = 0xff0000,
            description = f"<@{authorid}> spilled their drink, then farted, then pooped their pants. Very embarassing.\n\n{damagedesc} \n\nThey lost the drinking challenge against {highscorename}!",
            image = drinktenorimage,
            fields = [interactions.EmbedField(name="Player Roll",value=playerroll, inline=True),interactions.EmbedField(name="High Score",value=highscore,inline=True),interactions.EmbedField(name="Low Score",value=lowscore,inline=True)],
        )
        tavernchannel=str(locations["Tavern"]["Channel_ID"])
        channel = await interactions.get(bot, interactions.Channel, object_id=tavernchannel , force='http')
        await channel.send(embeds=drinktenor)
    else:
        highscoremedia = "https://i.imgur.com/Mt9swvj.png"
        for x in scores.values():
            if x["Score"] == highscore and x["Scoreexpiry"] > current_time:
                highscoremedia = x["Media"]
                highscorename = x["Username"]
        drinktenorimage = interactions.EmbedImageStruct(
                            url="https://i.imgur.com/Mt9swvj.png",
                            height = 375,
                            width = 500,
                            )
        print(f"playerscore is equal to or higher than the highscore")
        if lowscore == playerroll:
            damagedesc = "This roll is the lowest roll, they lose 1/4 of their current health!"
        else:
            damagedesc = "This roll is not the lowest roll, they heal for 1/4 of their current health!"
        usernameauthor = players[str(authorid)]["Username"]
        drinktenor = interactions.api.models.message.Embed(
            title = f"{usernameauthor} is the champion!",
            color = 0x09ff00,
            description = f"<@{authorid}> threw back shot after shot, tankard after tankard, until they were the last one standing!\n\nThey were awarded a medal for their drinking prowess! \n\n{damagedesc}!",
            image = drinktenorimage,
            fields = [interactions.EmbedField(name="Player Roll",value=playerroll, inline=True),interactions.EmbedField(name="High Score",value=highscore,inline=True),interactions.EmbedField(name="Low Score",value=lowscore,inline=True)],
        )
        tavernchannel=str(locations["Tavern"]["Channel_ID"])
        channel = await interactions.get(bot, interactions.Channel, object_id=tavernchannel , force='http')
        await channel.send(embeds=drinktenor)
        print(f"playerscore is the highscore")
        players[str(authorid)]["EquippedInventory"]=players[str(authorid)]["EquippedInventory"] + "\n        "+"drinkingmedal"
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
    if lowscore == playerroll: #check if the min is equal to the player's roll
        highscoremedia = "https://i.imgur.com/Mt9swvj.png"
        for x in scores.values():
            if x["Score"] == highscore and x["Scoreexpiry"] > current_time:
                highscoremedia = x["Media"]
                highscorename = x["Username"]
        drinktenorimage = interactions.EmbedImageStruct(
                            url=highscoremedia,
                            height = 375,
                            width = 500,
                            )
        print(f"lowscore is equal to playerscore")
        hp_pull = players[str(authorid)]["HP"]
        hp_pull= max(hp_pull - math.ceil(hp_pull/4),0)
        hpmoji = await hpmojiconv(hp_pull)
        drinkprivate = interactions.api.models.message.Embed(
            title = f"Damaged by lost Drinking Challenge!",
            color = 0xff0000,
            description = f"You had the lowest roll in the Tavern and lost 1/4 of your current hp!",
            image = drinktenorimage,
            fields = [interactions.EmbedField(name="Player Roll",value=playerroll, inline=True),interactions.EmbedField(name="High Score",value=highscore,inline=True),interactions.EmbedField(name="Low Score",value=lowscore,inline=True),interactions.EmbedField(name="New HP",value=hpmoji,inline=True)],
        )
        try:
            user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
            await user.send(embeds=drinkprivate)
        except:
            print(f"{authorid} not valid user to DM")
        players[str(authorid)]["HP"] = hp_pull
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
    else :
        highscoremedia = "https://i.imgur.com/Mt9swvj.png"
        for x in scores.values():
            if x["Score"] == highscore and x["Scoreexpiry"] > current_time:
                highscoremedia = x["Media"]
                highscorename = x["Username"]
        drinktenorimage = interactions.EmbedImageStruct(
                            url=highscoremedia,
                            height = 375,
                            width = 500,
                            )
        print(f"lowscore is not equal to playerscore")
        hp_pull = players[str(authorid)]["HP"]
        hp_pull=min(hp_pull+math.ceil((10000-hp_pull)/4),10000)
        hpmoji = await hpmojiconv(hp_pull)
        drinkprivate = interactions.api.models.message.Embed(
            title = f"Healed by Drinking Challenge!",
            color = 0x09ff00,
            description = f"You did not have the lowest roll in the Tavern and healed 1/4 of your missing hp!",
            image = drinktenorimage,
            fields = [interactions.EmbedField(name="Player Roll",value=playerroll, inline=True),interactions.EmbedField(name="High Score",value=highscore,inline=True),interactions.EmbedField(name="Low Score",value=lowscore,inline=True),interactions.EmbedField(name="New HP",value=hpmoji,inline=True)],
        )
        try:
            user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
            await user.send(embeds=drinkprivate)
        except:
            print(f"{authorid} not valid user to DM")
        players[str(authorid)]["HP"] = hp_pull
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
    with open("players.json","w") as f:
        json.dump(players,f, indent=4)

@bot.command(
    name="drink",
    description="1mana. score 1d4.high:gain drinkingmedal. heal 1/4 missing hp except low score loses 1/4hp.",
    scope = guildid,
)
async def drink(ctx: interactions.CommandContext):
    players = await getplayerdata()
    current_time = int(time.time())
    channelid=ctx.channel_id
    if str(ctx.author.id) in players:
        cost = 1
        Mana_pull = players[str(ctx.author.id)]["Mana"]
        if locations["Tavern"]["Role_ID"] not in ctx.author.roles:
            await ctx.send(f"You cannot drink when you are not in the tavern!", ephemeral=True)
        elif cost-Mana_pull > 0:
            enoughmanatime = (players[str(ctx.author.id)]["NextMana"])+(max((cost-Mana_pull-1),0))*basecd
            players[str(ctx.author.id)]["ReadyDate"] = enoughmanatime
            with open("players.json", "w") as f:
                json.dump(players, f, indent=4)
            await queuenext(ctx)
            await ctx.send(f"You don't have the mana for that! The action has been queued for <t:{enoughmanatime}>.", ephemeral = True)
        else:
            await ctx.send(f"You drink!\n\nSubmit another command!",ephemeral=True)
            if Mana_pull - cost > 0:
                manamoji = await manamojiconv(Mana_pull - cost)
                await ctx.send(f"You have {manamoji} mana remaining",ephemeral=True)
            else :
                await ctx.send(f"Your next action will be queued.",ephemeral=True)
            await dodrink(ctx.author.id)
    else:
        await ctx.send(f"You aren't in the competition!" , ephemeral = True)

#loot is below

async def doloot(authorid):
    await rage(authorid)
    players = await getplayerdata()
    players[str(authorid)]["Nextaction"] = ""
    scores = await getdungeondata()
    cooldown = basecd
    Lastaction_pull = players[str(authorid)]["Lastaction"]
    EquippedInventory_pull=players[str(authorid)]["EquippedInventory"]
    playerroll = int(int(random.randint(1,4)) + (Lastaction_pull.count("loot") * 1)) + (EquippedInventory_pull.count("adventuringgear") * 1)
    current_time = int(time.time())
    scores[str(authorid)] = {}
    scores[str(authorid)]["Username"] = players[str(authorid)]["Username"]
    user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
    scores[str(authorid)]["Media"] = interactions.Member.get_avatar_url(user, guild_id=guildid)
    scores[str(authorid)]["Score"] = playerroll
    scores[str(authorid)]["Scoreexpiry"] = current_time+cooldown
    username = players[str(authorid)]["Username"]
    print(f"{username} is looting")
    print(f"playerroll = {playerroll}")
    print(f"scores = \n{scores}\n")
    players[str(authorid)]["Mana"] = players[str(authorid)]["Mana"] -1
    players[str(authorid)]["Lastaction"] = "loot"
    with open("players.json","w") as f:
        json.dump(players,f, indent=4)
    if scores[str("NPC6")]["Scoreexpiry"] > current_time :
        highscore= max(x["Score"] for x in scores.values() if x["Scoreexpiry"] > current_time)
        lowscore= min(x["Score"] for x in scores.values() if x["Scoreexpiry"] > current_time)
        print("NPC6 score is not expired, and has not been rewritten")
        print(f"highscore is {highscore}")
        print(f"lowscore is {lowscore}")
    else:
        scores[str("NPC6")]["Score"] = int(random.randint(1,4)-1)
        scores[str("NPC6")]["Scoreexpiry"] = current_time +cooldown
        print("NPC6 score is expired, and has been rewritten")
        highscore= max(x["Score"] for x in scores.values() if x["Scoreexpiry"] > current_time)
        lowscore= min(x["Score"] for x in scores.values() if x["Scoreexpiry"] > current_time)
        print(f"highscore is {highscore}")
        print(f"lowscore is {lowscore}")
    if scores[str("NPC5")]["Scoreexpiry"] > current_time:
        highscore= max(x["Score"] for x in scores.values() if x["Scoreexpiry"] > current_time)
        lowscore= min(x["Score"] for x in scores.values() if x["Scoreexpiry"] > current_time)
        print("NPC5 score is not expired, and has not been rewritten")
        print(f"highscore is {highscore}")
        print(f"lowscore is {lowscore}")
    else:
        scores[str("NPC5")]["Score"] = int(random.randint(1,4)-1)
        scores[str("NPC5")]["Scoreexpiry"] = current_time +cooldown
        print("NPC5 score is expired, and has been rewritten")
        highscore= max(x["Score"] for x in scores.values() if x["Scoreexpiry"] > current_time)
        lowscore= min(x["Score"] for x in scores.values() if x["Scoreexpiry"] > current_time)
        print(f"highscore is {highscore}")
        print(f"lowscore is {lowscore}")
    highscoremedia = "https://media.tenor.com/c1VeLRFcWJAAAAAS/adventuretime-dungeon.gif"
    for x in scores.values():
        if x["Score"] == highscore and x["Scoreexpiry"] > current_time:
            highscoremedia = x["Media"]
            highscorename = x["Username"]
    with open("dungeon.json","w") as o:
        json.dump(scores,o, indent=4)
    print("Player dungeon Score Saved")
    #check if the max is greater than the player's roll
    if highscore > playerroll:
        print(f"playerscore is lower than highscore")
        highscoremedia = "https://media.tenor.com/c1VeLRFcWJAAAAAS/adventuretime-dungeon.gif"
        for x in scores.values():
            if x["Score"] == highscore and x["Scoreexpiry"] > current_time:
                highscoremedia = x["Media"]
                highscorename = x["Username"]
        if lowscore == playerroll:
            damagedesc = "This roll is the lowest roll, they lose 1/4 of their current health!"
        else:
            damagedesc = "This roll is not the lowest roll!"
        loottenorimage = interactions.EmbedImageStruct(
                            url=highscoremedia,
                            height = 512,
                            width = 512,
                            )
        loottenor = interactions.api.models.message.Embed(
            title = f"Defeated by {highscorename}!",
            color = 0x474545,
            description = f"<@{authorid}> tripped, rolled a nat one, then was hit by a trap! Very embarassing.\n\n{damagedesc} \n\nThey failed to loot because of {highscorename}!",
            image = loottenorimage,
            fields = [interactions.EmbedField(name="Player Roll",value=playerroll, inline=True),interactions.EmbedField(name="High Score",value=highscore,inline=True),interactions.EmbedField(name="Low Score",value=lowscore,inline=True)],
        )
        dungeonchannel=str(locations["Dungeon"]["Channel_ID"])
        channel = await interactions.get(bot, interactions.Channel, object_id=dungeonchannel, force='http')
        await channel.send(embeds=loottenor)
    else:
        print(f"playerscore is equal to or higher than the highscore")
        highscoremedia = "https://media.tenor.com/c1VeLRFcWJAAAAAS/adventuretime-dungeon.gif"
        for x in scores.values():
            if x["Score"] == highscore and x["Scoreexpiry"] > current_time:
                highscoremedia = x["Media"]
                highscorename = x["Username"]
        if lowscore == playerroll:
            damagedesc = "This roll is the lowest roll, they lose 1/4 of their current health!"
        else:
            damagedesc = "This roll is not the lowest roll!"
        highscoremedia = "https://media.tenor.com/c1VeLRFcWJAAAAAd/adventuretime-dungeon.gif"
        usernameauthor = players[str(authorid)]["Username"]
        loottenorimage = interactions.EmbedImageStruct(
                            url=highscoremedia,
                            height = 512,
                            width = 512,
                            )
        loottenor = interactions.api.models.message.Embed(
            title = f"{usernameauthor} is successful!",
            color = 0x474545,
            description = f"<@{authorid}> slayed beast after beast, until they were the last one standing!\n\nThey looted a random item!",
            image = loottenorimage,
            fields = [interactions.EmbedField(name="Player Roll",value=playerroll, inline=True),interactions.EmbedField(name="High Score",value=highscore,inline=True),interactions.EmbedField(name="Low Score",value=lowscore,inline=True)],
        )
        dungeonchannel=str(locations["Dungeon"]["Channel_ID"])
        channel = await interactions.get(bot, interactions.Channel, object_id=dungeonchannel, force='http')
        await channel.send(embeds=loottenor)
        #shop item random
        shop = await getshopdata()
        randomitem = random.choice(list(shop))
        hp_pull = players[str(authorid)]["HP"]
        hpmoji = await hpmojiconv(hp_pull)
        loottenorimage = interactions.EmbedImageStruct(
                            url="https://media.tenor.com/c1VeLRFcWJAAAAAS/adventuretime-dungeon.gif",
                            height = 512,
                            width = 512,
                            )
        lootprivate = interactions.api.models.message.Embed(
            title = f"You looted!",
            color = 0x474545,
            description = f"You had the high roll in the Dungeon and gained {randomitem}!",
            image = loottenorimage,
            fields = [interactions.EmbedField(name="Player Roll",value=playerroll, inline=True),interactions.EmbedField(name="High Score",value=highscore,inline=True),interactions.EmbedField(name="Low Score",value=lowscore,inline=True),interactions.EmbedField(name="New HP",value=hpmoji,inline=True)],
        )
        try:
            user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
            await user.send(embeds=lootprivate)
        except:
            print(f"{authorid} not valid user to DM")
        players[str(authorid)]["ReadyInventory"]=players[str(authorid)]["ReadyInventory"] + "\n        "+randomitem
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
    if lowscore == playerroll: #check if the min is equal to the player's roll
        print(f"lowscore is equal to playerscore")
        highscoremedia = "https://media.tenor.com/c1VeLRFcWJAAAAAS/adventuretime-dungeon.gif"
        for x in scores.values():
            if x["Score"] == highscore and x["Scoreexpiry"] > current_time:
                highscoremedia = x["Media"]
                highscorename = x["Username"]
        loottenorimage = interactions.EmbedImageStruct(
                            url=highscoremedia,
                            height = 512,
                            width = 512,
                            )
        hp_pull = players[str(authorid)]["HP"]
        hp_pull= max(hp_pull - math.ceil(hp_pull/4),0)
        hpmoji = await hpmojiconv(hp_pull)
        lootprivate = interactions.api.models.message.Embed(
            title = f"Damaged by failed looting!",
            color = 0x474545,
            description = f"You had the lowest roll in the Dungeon and lost 1/4 of your current hp!",
            image = loottenorimage,
            fields = [interactions.EmbedField(name="Player Roll",value=playerroll, inline=True),interactions.EmbedField(name="High Score",value=highscore,inline=True),interactions.EmbedField(name="Low Score",value=lowscore,inline=True),interactions.EmbedField(name="New HP",value=hpmoji,inline=True)],
        )
        try:
            user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
            await user.send(embeds=lootprivate)
        except:
            print(f"{authorid} not valid user to DM")
        players[str(authorid)]["HP"] = hp_pull
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
    else :
        print(f"lowscore is not equal to playerscore")
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
    with open("players.json","w") as f:
        json.dump(players,f, indent=4)

@bot.command(
    name="loot",
    description="1mana.score 1d4. on high score gain an item at random. low score: lose 1/4 of your current health.",
    scope = guildid,
)
async def loot(ctx: interactions.CommandContext):
    players = await getplayerdata()
    current_time = int(time.time())
    channelid=ctx.channel_id
    if str(ctx.author.id) in players:
        cost = 1
        Mana_pull = players[str(ctx.author.id)]["Mana"]
        if locations["Dungeon"]["Role_ID"] not in ctx.author.roles:
            await ctx.send(f"You cannot /loot when you are not in the Dungeon!", ephemeral=True)
        elif cost-Mana_pull > 0:
            enoughmanatime = (players[str(ctx.author.id)]["NextMana"])+(max((cost-Mana_pull-1),0))*basecd
            players[str(ctx.author.id)]["ReadyDate"] = enoughmanatime
            with open("players.json", "w") as f:
                json.dump(players, f, indent=4)
            await queuenext(ctx)
            await ctx.send(f"You don't have the mana for that! The action has been queued for <t:{enoughmanatime}>.", ephemeral = True)
        else:
            manamoji = await manamojiconv(Mana_pull- cost)
            manaemb = interactions.api.models.message.Embed(
                title = f"You attempt to loot!",
                color = 0x474545,
                fields = [interactions.EmbedField(name="Mana Remaining",value=manamoji,inline=True)],
            )
            await ctx.send(embeds=manaemb,ephemeral = True)
            await doloot(ctx.author.id)
    else:
        await ctx.send(f"You aren't in the competition!" , ephemeral = True)

#dobattlelich is below

async def dobattlelich(authorid):
    await rage(authorid)
    players = await getplayerdata()
    players[str(authorid)]["Nextaction"] = ""
    scores = await getlichdata()
    cooldown = basecd
    Lastaction_pull = players[str(authorid)]["Lastaction"]
    EquippedInventory_pull=players[str(authorid)]["EquippedInventory"]
    playerroll = int(int(random.randint(1,4)) + (Lastaction_pull.count("battlelich") * 1))
    current_time = int(time.time())
    scores[str(authorid)] = {}
    scores[str(authorid)]["Username"] = players[str(authorid)]["Username"]
    user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
    scores[str(authorid)]["Media"] = interactions.Member.get_avatar_url(user, guild_id=guildid)
    scores[str(authorid)]["Score"] = playerroll
    scores[str(authorid)]["Scoreexpiry"] = current_time+cooldown
    username = players[str(authorid)]["Username"]
    print(f"{username} is battling the lich")
    print(f"playerroll = {playerroll}")
    print(f"scores = \n{scores}\n")
    players[str(authorid)]["Mana"] = players[str(authorid)]["Mana"] -1
    players[str(authorid)]["Lastaction"] = "battlelich"
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
    highscoremedia = "https://i.imgur.com/WoG1ubB.png"
    for x in scores.values():
        if x["Score"] == highscore and x["Scoreexpiry"] > current_time:
            highscoremedia = x["Media"]
            highscorename = x["Username"]
    with open("lichcastle.json","w") as l:
        json.dump(scores,l, indent=4)
    print("Player dungeon Score Saved")
    #check if the max is greater than the player's roll
    if highscore > playerroll:
        print(f"playerscore is lower than highscore")
        highscoremedia = "https://i.imgur.com/WoG1ubB.png"
        for x in scores.values():
            if x["Score"] == highscore and x["Scoreexpiry"] > current_time:
                highscoremedia = x["Media"]
                highscorename = x["Username"]
        if lowscore == playerroll:
            damagedesc = "This roll is the lowest roll, they lose 1/4 of their current health!"
        else:
            damagedesc = "This roll is not the lowest roll!"
        lichimg = interactions.EmbedImageStruct(
                            url=highscoremedia,
                            height = 500,
                            width = 500,
                            )
        lichemb = interactions.api.models.message.Embed(
            title = f"Defeated by {highscorename}!",
            color = 0x000000,
            description = f"<@{authorid}> was tossed around, smacked around, and bashed around! Very embarassing.\n\n{damagedesc} \n\nThey failed to gain the lich item because of {highscorename}!",
            image = lichimg,
            fields = [interactions.EmbedField(name="Player Roll",value=playerroll, inline=True),interactions.EmbedField(name="High Score",value=highscore,inline=True),interactions.EmbedField(name="Low Score",value=lowscore,inline=True)],
        )
        lichchannel=str(locations["Lich's Castle"]["Channel_ID"])
        channel = await interactions.get(bot, interactions.Channel, object_id=lichchannel, force='http')
        await channel.send(embeds=lichemb)
    else:
        print(f"playerscore is equal to or higher than the highscore")
        highscoremedia = "https://i.imgur.com/WoG1ubB.png"
        for x in scores.values():
            if x["Score"] == highscore and x["Scoreexpiry"] > current_time:
                highscoremedia = x["Media"]
                highscorename = x["Username"]
        if lowscore == playerroll:
            damagedesc = "This roll is the lowest roll, they lose 1/4 of their current health!"
        else:
            damagedesc = "This roll is not the lowest roll!"
        usernameauthor = players[str(authorid)]["Username"]
        lichimg = interactions.EmbedImageStruct(
                            url="https://www.reactiongifs.us/wp-content/uploads/2013/09/kill_it_shaun_of_the_dead.gif",
                            height = 500,
                            width = 500,
                            )
        lichemb = interactions.api.models.message.Embed(
            title = f"{usernameauthor} is successful!",
            color = 0x000000,
            description = f"<@{authorid}> slayed the lich and zombie hordes, until they were the last one standing!\n\nThey gained the lich item!",
            image = lichimg,
            fields = [interactions.EmbedField(name="Player Roll",value=playerroll, inline=True),interactions.EmbedField(name="High Score",value=highscore,inline=True),interactions.EmbedField(name="Low Score",value=lowscore,inline=True)],
        )
        lichchannel=str(locations["Lich's Castle"]["Channel_ID"])
        channel = await interactions.get(bot, interactions.Channel, object_id=lichchannel, force='http')
        await channel.send(embeds=lichemb)
        players[str(authorid)]["ReadyInventory"]=players[str(authorid)]["ReadyInventory"] + "\n        lichitem"
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
    if lowscore == playerroll: #check if the min is equal to the player's roll
        print(f"lowscore is equal to playerscore")
        highscoremedia = "https://i.imgur.com/WoG1ubB.png"
        for x in scores.values():
            if x["Score"] == highscore and x["Scoreexpiry"] > current_time:
                highscoremedia = x["Media"]
                highscorename = x["Username"]
        lichimg = interactions.EmbedImageStruct(
                            url=highscoremedia,
                            height = 500,
                            width = 500,
                            )
        hp_pull = players[str(authorid)]["HP"]
        hp_pull= max(hp_pull - math.ceil(hp_pull/4),0)
        hpmoji = await hpmojiconv(hp_pull)
        lichprivate = interactions.api.models.message.Embed(
            title = f"Damaged by failed Lich Battle!",
            color = 0x000000,
            description = f"You had the lowest roll in the Lich's Castle and lost 1/4 of your current hp!",
            image = lichimg,
            fields = [interactions.EmbedField(name="Player Roll",value=playerroll, inline=True),interactions.EmbedField(name="High Score",value=highscore,inline=True),interactions.EmbedField(name="Low Score",value=lowscore,inline=True),interactions.EmbedField(name="New HP",value=hpmoji,inline=True)],
        )
        try:
            user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
            await user.send(embeds=lichprivate)
        except:
            print(f"{authorid} not valid user to DM")
        players[str(authorid)]["HP"] = hp_pull
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
    else :
        print(f"lowscore is not equal to playerscore")
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
    with open("players.json","w") as f:
        json.dump(players,f, indent=4)


async def douse(authorid, readyitem):
    players = await getplayerdata()
    players[str(authorid)]["Nextaction"] = ""
    shop = await getshopdata()
    user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
    manacost = shop[str(readyitem)]["ManaCost"]
    print(f"{authorid} will use {readyitem} for {manacost}!")
    location = players[str(authorid)]["Location"]
    channelid = locations[str(location)]["Channel_ID"]
    current_time = int(time.time())
    ReadyInventory_pull = str(players[str(authorid)]["ReadyInventory"])
    print("Step1")
    players[str(authorid)]["Mana"] = players[str(authorid)]["Mana"] - shop[str(readyitem)]["ManaCost"]
    print("Step2")
    with open("players.json","w") as f:
        json.dump(players,f, indent=4)
    print("Step3")
    loop = asyncio.get_running_loop()
    await loop.create_task(functiondict[readyitem](**{'authorid': authorid}))


@bot.command(
    name="battlelich",
    description="1mana. score 1d4. high score: gain Lich's Item. low score: lose 1/4 current health.",
    scope = guildid,
)
async def battlelich(ctx: interactions.CommandContext):
    players = await getplayerdata()
    current_time = int(time.time())
    channelid=ctx.channel_id
    if str(ctx.author.id) in players:
        cost = 1
        Mana_pull = players[str(ctx.author.id)]["Mana"]
        if locations["Lich's Castle"]["Role_ID"] not in ctx.author.roles:
            await ctx.send(f"You cannot battlelich when you are not in the Lich's Castle!", ephemeral=True)
        elif cost-Mana_pull > 0:
            enoughmanatime = (players[str(ctx.author.id)]["NextMana"])+(max((cost-Mana_pull-1),0))*basecd
            players[str(ctx.author.id)]["ReadyDate"] = enoughmanatime
            with open("players.json", "w") as f:
                json.dump(players, f, indent=4)
            await queuenext(ctx)
            await ctx.send(f"You don't have the mana for that! The action has been queued for <t:{enoughmanatime}>.", ephemeral = True)
        else:
            manamoji = await manamojiconv(Mana_pull- cost)
            lichemb = interactions.api.models.message.Embed(
                title = f"You battle the lich!",
                color = 0x000000,
                fields = [interactions.EmbedField(name="Mana Remaining",value=manamoji,inline=True)],
            )
            await ctx.send(embeds=lichemb,ephemeral = True)
            await dobattlelich(ctx.author.id)
    else:
        await ctx.send(f"You aren't in the competition!" , ephemeral = True)

@bot.command(
    name="use",
    description="x mana. use or equip an item in your inventory",
    scope = guildid,
    options=[
        interactions.Option(
            type=interactions.OptionType.STRING,
            name="readyitem",
            description="type the item you want to use",
            required=True,
            autocomplete=True,
        )
    ]
)
async def use(ctx: interactions.CommandContext, readyitem: str):
    players = await getplayerdata()
    shop = await getshopdata()
    current_time = int(time.time())
    channelid=ctx.channel_id
    authorid=ctx.author.id
    print(f"{readyitem} is the item target")
    if str(authorid) in players:
        cost = shop[readyitem]["ManaCost"]
        Mana_pull = players[str(ctx.author.id)]["Mana"]
        ReadyInventory_pull = str(players[str(ctx.author.id)]["ReadyInventory"])
        if ReadyInventory_pull=="":
            await ctx.send(f"You don't have any items to use in your Inventory!", ephemeral = True)
        elif cost-Mana_pull > 0:
            enoughmanatime = (players[str(ctx.author.id)]["NextMana"])+(max((cost-Mana_pull-1),0))*basecd
            players[str(ctx.author.id)]["ReadyDate"] = enoughmanatime
            with open("players.json", "w") as f:
                json.dump(players, f, indent=4)
            await queuenexttarget("use",ctx,readyitem)
            await ctx.send(f"You don't have the mana for that! The action has been queued for <t:{enoughmanatime}>.", ephemeral = True)
        else:
            manamoji = await manamojiconv(Mana_pull- cost)
            manaemb = interactions.api.models.message.Embed(
                title = f"You use the {readyitem}!",
                color = 0x633914,
                fields = [interactions.EmbedField(name="Mana Remaining",value=manamoji,inline=True)],
            )
            await ctx.send(embeds=manaemb,ephemeral = True)
            await douse(ctx.author.id,readyitem)
    else:
        await ctx.send(f"You aren't in the competition!" , ephemeral = True)

@bot.autocomplete("use", "readyitem")
async def use_autocomplete(ctx: interactions.CommandContext, value: str = ""):
    players = await getplayerdata()
    ReadyInventory_pull = str(players[str(ctx.author.id)]["ReadyInventory"])
    print(ReadyInventory_pull)
    readyitems = list(filter(None, list(ReadyInventory_pull.split("\n        "))))
    print (readyitems)
    items = readyitems
    choices = [
        interactions.Choice(name=item, value=item) for item in items if value.lower() in item.lower()
    ]
    await ctx.populate(choices)

#lichitem is below

async def dolichitem(authorid):
    await rage(authorid)
    players = await getplayerdata()
    players[str(authorid)]["Nextaction"] = ""
    current_time = int(time.time())
    user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
    location = players[str(authorid)]["Location"]
    channelid = locations[str(location)]["Channel_ID"]
    players[str(authorid)]["Mana"] = players[str(authorid)]["Mana"] -1
    players[str(authorid)]["Lastaction"] = "lichitem"
    targethp=players[str(authorid)]["HP"]
    hpmoji = await hpmojiconv(targethp)
    user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
    userreadyinventory=str(players[str(authorid)]["ReadyInventory"])
    #replace first instance of item in user's readyinventory
    players[str(authorid)]["ReadyInventory"]=userreadyinventory.replace('\n        lichitem','',1)
    #add the item to the user's Equippedinventory
    players[str(authorid)]["EquippedInventory"]=players[str(authorid)]["EquippedInventory"]+"\n        lichitem"
    with open("players.json","w") as f:
        json.dump(players,f, indent=4)
    itemurl="https://media.tenor.com/tBozA1n6mysAAAAC/lich-skeleton.gif"
    itemimg = interactions.EmbedImageStruct(
                        url=itemurl,
                        height = 512,
                        width = 512,
                        )
    itememb = interactions.api.models.message.Embed(
        title = f"{players[str(authorid)]['Username']} equips a Lich Item!",
        color = 0x633914,
        description = f"<@{authorid}> equips a lich item. It's v icky and v gross. This will protect them from their next death.",
        image = itemimg,
    )
    userchannel=str(locations[players[str(authorid)]["Location"]]["Channel_ID"])
    channel = await interactions.get(bot, interactions.Channel, object_id=userchannel , force='http')
    await channel.send(embeds=itememb)


#drinkingmedal is below

async def dodrinkingmedal(authorid):
    await rage(authorid)
    players = await getplayerdata()
    players[str(authorid)]["Nextaction"] = ""
    user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
    location = players[str(authorid)]["Location"]
    channelid = locations[str(location)]["Channel_ID"]
    players = await getplayerdata()
    current_time = int(time.time())
    players[str(authorid)]["Lastaction"] = "drinkingmedal"
    userreadyinventory=str(players[str(authorid)]["ReadyInventory"])
    #replace first instance of item in user's readyinventory
    players[str(authorid)]["ReadyInventory"]=userreadyinventory.replace('\n        drinkingmedal','',1)
    #add the item to the user's Equippedinventory
    players[str(authorid)]["EquippedInventory"]=players[str(authorid)]["EquippedInventory"] + "\n        "+"drinkingmedal"
    with open("players.json","w") as f:
        json.dump(players,f, indent=4)
    itemurl="https://img.gifglobe.com/grabs/peepshow/S08E02/gif/h5CvJrGpnvQ8.gif"
    itemimg = interactions.EmbedImageStruct(
                        url=itemurl,
                        height = 512,
                        width = 512,
                        )
    itememb = interactions.api.models.message.Embed(
        title = f"{players[str(authorid)]['Username']} equips a Drinking Medal!",
        color = 0x633914,
        description = f"<@{authorid}> smiles strangely as they put the medal around their neck. Their light attacks do 420 additional damage.",
        image = itemimg,
    )
    userchannel=str(locations[players[str(authorid)]["Location"]]["Channel_ID"])
    channel = await interactions.get(bot, interactions.Channel, object_id=userchannel , force='http')
    await channel.send(embeds=itememb)


#goodiebag is below

async def dogoodiebag(authorid):
    await rage(authorid)
    players = await getplayerdata()
    players[str(authorid)]["Nextaction"] = ""
    user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
    location = players[str(authorid)]["Location"]
    channelid = locations[str(location)]["Channel_ID"]
    current_time = int(time.time())
    players[str(authorid)]["Lastaction"] = "goodiebag"
    userreadyinventory=str(players[str(authorid)]["ReadyInventory"])
    #get a randomitem
    shop = await getshopdata()
    randomitem = random.choice(list(shop))
    itemurl="https://media2.giphy.com/media/3o6EhZ8YQpXqIndxNm/200.gif"
    itemimg = interactions.EmbedImageStruct(
                        url=itemurl,
                        height = 512,
                        width = 512,
                        )
    itememb = interactions.api.models.message.Embed(
        title = f"{players[str(authorid)]['Username']} opens a Goodie Bag!",
        color = 0x633914,
        description = f"<@{authorid}> cracks open a cold Goodie Bag for a **{randomitem}**!",
        image = itemimg,
    )
    try:
        user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
        await user.send(embeds=itememb)
    except:
        print(f"{authorid} not valid user to DM")
    players[str(authorid)]["ReadyInventory"]=players[str(authorid)]["ReadyInventory"] + "\n        "+str(randomitem)
    userreadyinventory=str(players[str(authorid)]["ReadyInventory"])
    #replace first instance of item in user's readyinventory
    players[str(authorid)]["ReadyInventory"]=userreadyinventory.replace('\n        goodiebag','',1)
    with open("players.json","w") as f:
        json.dump(players,f, indent=4)
    itemurl="https://media2.giphy.com/media/3o6EhZ8YQpXqIndxNm/200.gif"
    itemimg = interactions.EmbedImageStruct(
                        url=itemurl,
                        height = 512,
                        width = 512,
                        )
    itememb = interactions.api.models.message.Embed(
        title = f"{players[str(authorid)]['Username']} opens a Goodie Bag!",
        color = 0x633914,
        description = f"<@{authorid}> cracks open a cold Goodie Bag for a random item!",
        image = itemimg,
    )
    userchannel=str(locations[players[str(authorid)]["Location"]]["Channel_ID"])
    channel = await interactions.get(bot, interactions.Channel, object_id=userchannel , force='http')
    await channel.send(embeds=itememb)

#tractor is below

async def dotractor(authorid):
    await rage(authorid)
    players = await getplayerdata()
    players[str(authorid)]["Nextaction"] = ""
    current_time = int(time.time())
    user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
    location = players[str(authorid)]["Location"]
    channelid = locations[str(location)]["Channel_ID"]
    players[str(authorid)]["Lastaction"] = "tractor"
    userreadyinventory=str(players[str(authorid)]["ReadyInventory"])
    #replace first instance of item in user's readyinventory
    players[str(authorid)]["ReadyInventory"]=userreadyinventory.replace('\n        tractor','',1)
    #add the item to the user's Equippedinventory
    players[str(authorid)]["EquippedInventory"]=players[str(authorid)]["EquippedInventory"] + "\n        "+"tractor"
    with open("players.json","w") as f:
        json.dump(players,f, indent=4)
    itemurl="https://media.tenor.com/sH_KNNF07EoAAAAC/honest-word-its-honest-work.gif"
    itemimg = interactions.EmbedImageStruct(
                        url=itemurl,
                        height = 512,
                        width = 512,
                        )
    itememb = interactions.api.models.message.Embed(
        title = f"{players[str(authorid)]['Username']} equips a Tractor!",
        color = 0x633914,
        description = f"<@{authorid}> puts a tractor underneath themselves so that they gain an additional SC whenever they /farm!",
        image = itemimg,
    )
    userchannel=str(locations[players[str(authorid)]["Location"]]["Channel_ID"])
    channel = await interactions.get(bot, interactions.Channel, object_id=userchannel , force='http')
    await channel.send(embeds=itememb)

#critterihardlyknowher is below

async def docritterihardlyknowher(authorid):
    await rage(authorid)
    players = await getplayerdata()
    players[str(authorid)]["Nextaction"] = ""
    current_time = int(time.time())
    user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
    location = players[str(authorid)]["Location"]
    channelid = locations[str(location)]["Channel_ID"]
    players[str(authorid)]["Lastaction"] = "critterihardlyknowher"
    userreadyinventory=str(players[str(authorid)]["ReadyInventory"])
    #replace first instance of item in user's readyinventory
    players[str(authorid)]["ReadyInventory"]=userreadyinventory.replace('\n        critterihardlyknowher','',1)
    #add the item to the user's Equippedinventory
    players[str(authorid)]["EquippedInventory"]=players[str(authorid)]["EquippedInventory"] + "\n        "+"critterihardlyknowher"
    with open("players.json","w") as f:
        json.dump(players,f, indent=4)
    itemurl="https://media0.giphy.com/media/3ohhwDjtC2yP75kota/giphy.gif"
    itemimg = interactions.EmbedImageStruct(
                        url=itemurl,
                        height = 512,
                        width = 512,
                        )
    itememb = interactions.api.models.message.Embed(
        title = f"{players[str(authorid)]['Username']} equips a Critter I hardly Know her!",
        color = 0x633914,
        description = f"<@{authorid}> equips Critter I hardly Know Her and is v ugly. Their critical rolls are increased by 1 for the rest of the game.\n*(Crit is a 1d10 roll, a 10 or higher is a crit that increases the base damage by 50%)*",
        image = itemimg,
    )
    userchannel=str(locations[players[str(authorid)]["Location"]]["Channel_ID"])
    channel = await interactions.get(bot, interactions.Channel, object_id=userchannel , force='http')
    await channel.send(embeds=itememb)

#beer-bandolier is below

async def dobeerbando(authorid):
    await rage(authorid)
    players = await getplayerdata()
    players[str(authorid)]["Nextaction"] = ""
    current_time = int(time.time())
    players[str(authorid)]["Lastaction"] = "beerbando"
    user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
    location = players[str(authorid)]["Location"]
    channelid = locations[str(location)]["Channel_ID"]
    #increase user's rage by 3
    players[str(authorid)]["Rage"]=players[str(authorid)]["Rage"]+3
    userreadyinventory=str(players[str(authorid)]["ReadyInventory"])
    #replace first instance of item in user's readyinventory
    players[str(authorid)]["ReadyInventory"]=userreadyinventory.replace('\n        beerbando','',1)
    #add the item to the user's Equippedinventory
    with open("players.json","w") as f:
        json.dump(players,f, indent=4)
    itemurl="https://media.tenor.com/eSp3S65iz6IAAAAM/beer-german.gif"
    itemimg = interactions.EmbedImageStruct(
                        url=itemurl,
                        height = 512,
                        width = 512,
                        )
    itememb = interactions.api.models.message.Embed(
        title = f"{players[str(authorid)]['Username']} cracks open a BeerBando!",
        color = 0x633914,
        description = f"<@{authorid}> pulls a beer out of their bandolier and chugs it to increase their Rage:fire: by 3!",
        image = itemimg,
    )
    userchannel=str(locations[players[str(authorid)]["Location"]]["Channel_ID"])
    channel = await interactions.get(bot, interactions.Channel, object_id=userchannel , force='http')
    await channel.send(embeds=itememb)

#localligmaoutbreak is below

async def dolocalligmaoutbreak(authorid):
    await rage(authorid)
    players = await getplayerdata()
    players[str(authorid)]["Nextaction"] = ""
    ligma = await getligmadata()
    current_time = int(time.time())
    players[str(authorid)]["Lastaction"] = "localligmaoutbreak"
    user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
    location = players[str(authorid)]["Location"]
    channelid = locations[str(location)]["Channel_ID"]
    samelocationUserIDs = {k: v for k, v in players.items() if v['Location'] == location}
    ligmadamage_pull = ligma[location]*250
    #damage everyone in the area
    for key in players.keys():
      if key in samelocationUserIDs:
        players[key]['HP'] = players[key]['HP'] - ligmadamage_pull
    # check for dead?
    print(f"\ndead?:{int(time.time())}")
    for k,v in players.items():
        if v['HP'] <= 0 and v['Location'] != "Dead":
            EquippedInventory_pull = v["EquippedInventory"]
            targetlichprot = EquippedInventory_pull.count("lichitem")
            print(f"\nthe target died!")
            user = await interactions.get(bot, interactions.Member, object_id=k, guild_id=guildid, force='http')
            if targetlichprot > 0:
                v["HP"] = 4200
                #replace first instance of item in user's readyinventory
                players[str(k)]["EquippedInventory"]=EquippedInventory_pull.replace('\n        lichitem',' ',1)
                await send_message(f"<@{k}> would have died because of <@{authorid}> ||LIGMA BALLS||, but they were protected by their equipped lich item! \n\nThat lichitem has since broken.", channel_id=[general])
            else:
                await send_message(f"<@{k}> died because of <@{authorid}> ||LIGMA BALLS||!", channel_id=[general])
                #give dead role
                await user.add_role(role=locations ["Dead"]["Role_ID"], guild_id=guildid)
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
                players[str(k)]["Location"] = "Dead"
                players[str(k)]["Team"] = "Dead"
                players[str(k)]["Nextaction"] = ""
            with open("players.json","w") as f:
                json.dump(players,f, indent=4)
    userreadyinventory=str(players[str(authorid)]["ReadyInventory"])
    #replace first instance of item in user's readyinventory
    players[str(authorid)]["ReadyInventory"]=userreadyinventory.replace('\n        localligmaoutbreak','',1)
    with open("players.json","w") as f:
        json.dump(players,f, indent=4)
    itemurl="https://media.tenor.com/K9s5fCvjG4AAAAAM/average-ligma-member-ligma.gif"
    itemimg = interactions.EmbedImageStruct(
                        url=itemurl,
                        height = 512,
                        width = 512,
                        )
    itememb = interactions.api.models.message.Embed(
        title = f"{players[str(authorid)]['Username']} activates a Local Ligma Outbreak!",
        color = 0x633914,
        description = f"<@{authorid}> activates a local ligma outbreak! \n\n\n||LIGMA BALLS|| dealt {ligmadamage_pull} to @everyone in {location}!",
        image = itemimg,
    )
    userchannel=str(locations[players[str(authorid)]["Location"]]["Channel_ID"])
    channel = await interactions.get(bot, interactions.Channel, object_id=userchannel , force='http')
    await channel.send(embeds=itememb)

#AWP is below

async def doAWP(authorid):
    await rage(authorid)
    players = await getplayerdata()
    players[str(authorid)]["Nextaction"] = ""
    current_time = int(time.time())
    user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
    location = players[str(authorid)]["Location"]
    channelid = locations[str(location)]["Channel_ID"]
    players[str(authorid)]["Lastaction"] = "aimtrain"
    userreadyinventory=str(players[str(authorid)]["ReadyInventory"])
    #replace first instance of item in user's readyinventory
    players[str(authorid)]["ReadyInventory"]=userreadyinventory.replace('\n        AWP','',1)
    #add the item to the user's Equippedinventory
    players[str(authorid)]["EquippedInventory"]=players[str(authorid)]["EquippedInventory"] + "\n        "+"AWP"
    with open("players.json","w") as f:
        json.dump(players,f, indent=4)
    itemurl="https://i.imgur.com/5DIpVK2.png"
    itemimg = interactions.EmbedImageStruct(
                        url=itemurl,
                        height = 512,
                        width = 512,
                        )
    itememb = interactions.api.models.message.Embed(
        title = f"{players[str(authorid)]['Username']} equips an AWP!",
        color = 0x633914,
        description = f"<@{authorid}> needs to pick up a weel gun! They've reduced the mana cost of their heavy attacks to two.",
        image = itemimg,
    )
    userchannel=str(locations[players[str(authorid)]["Location"]]["Channel_ID"])
    channel = await interactions.get(bot, interactions.Channel, object_id=userchannel , force='http')
    await channel.send(embeds=itememb)


#Crooked Abacus is below

async def docrookedabacus(authorid):
    await rage(authorid)
    players = await getplayerdata()
    players[str(authorid)]["Nextaction"] = ""
    current_time = int(time.time())
    user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
    location = players[str(authorid)]["Location"]
    channelid = locations[str(location)]["Channel_ID"]
    players[str(authorid)]["Lastaction"] = "crookedabacus"
    userreadyinventory=str(players[str(authorid)]["ReadyInventory"])
    #replace first instance of item in user's readyinventory
    players[str(authorid)]["ReadyInventory"]=userreadyinventory.replace('\n        crookedabacus','',1)
    #add the item to the user's Equippedinventory
    players[str(authorid)]["EquippedInventory"]=players[str(authorid)]["EquippedInventory"] + "\n        "+"crookedabacus"
    with open("players.json","w") as f:
        json.dump(players,f, indent=4)
    itemurl="https://i.imgur.com/D28u510.gif"
    itemimg = interactions.EmbedImageStruct(
                        url=itemurl,
                        height = 512,
                        width = 512,
                        )
    itememb = interactions.api.models.message.Embed(
        title = f"{players[str(authorid)]['Username']} equips a Crooked Abacus!",
        color = 0x633914,
        description = f"<@{authorid}>'s math seems off. They gain a SC whenever they /trade or /exchange!",
        image = itemimg,
    )
    userchannel=str(locations[players[str(authorid)]["Location"]]["Channel_ID"])
    channel = await interactions.get(bot, interactions.Channel, object_id=userchannel , force='http')
    await channel.send(embeds=itememb)

#adventuringgear is below

async def doadventuringgear(authorid):
    await rage(authorid)
    players = await getplayerdata()
    players[str(authorid)]["Nextaction"] = ""
    current_time = int(time.time())
    user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
    location = players[str(authorid)]["Location"]
    channelid = locations[str(location)]["Channel_ID"]
    players[str(authorid)]["Lastaction"] = "adventuringgear"
    userreadyinventory=str(players[str(authorid)]["ReadyInventory"])
    #replace first instance of item in user's readyinventory
    players[str(authorid)]["ReadyInventory"]=userreadyinventory.replace('\n        adventuringgear','',1)
    #add the item to the user's Equippedinventory
    players[str(authorid)]["EquippedInventory"]=players[str(authorid)]["EquippedInventory"] + "\n        "+"adventuringgear"
    with open("players.json","w") as f:
        json.dump(players,f, indent=4)
    itemurl="https://media.tenor.com/v8IHthjAtpkAAAAC/the-hobbit-bilbo.gif"
    itemimg = interactions.EmbedImageStruct(
                        url=itemurl,
                        height = 512,
                        width = 512,
                        )
    itememb = interactions.api.models.message.Embed(
        title = f"{players[str(authorid)]['Username']} equips Adventuring Gear!",
        color = 0x633914,
        description = f"<@{authorid}> equips adventuring gear to score one higher when they /loot!",
        image = itemimg,
    )
    userchannel=str(locations[players[str(authorid)]["Location"]]["Channel_ID"])
    channel = await interactions.get(bot, interactions.Channel, object_id=userchannel , force='http')
    await channel.send(embeds=itememb)

actionhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="Actions",
    custom_id="Actions",
)

@bot.component("Actions")
async def button_response(ctx):
    buttonemb = interactions.api.models.message.Embed(
        title = f"Actions",
        color = 0x000000,
        description = f"Actions are what you do! Most actions cost mana. You generate one mana every {int(basecd/60/60)} hours and can hold up to three mana at a time. Players can't take actions that would make their mana negative.\n\nWhen you attempt to perform an action but don't have enough mana, you instead queue the action. You perform that action when you have enough mana.\n\nFind out more:",
        )
    row = interactions.spread_to_rows(lightattackhelpbutton, heavyattackhelpbutton, interrupthelpbutton, evadehelpbutton, resthelpbutton, areactionhelpbutton, recruithelpbutton, useitemhelpbutton, gamblehelpbutton, statushelpbutton)
    await ctx.send(embeds = buttonemb, components=row, ephemeral=False)

wighthelpbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Wights",
    custom_id="wights",
)

@bot.component("wights")
async def button_response(ctx):
    buttonemb = interactions.api.models.message.Embed(
        title = f"Wights",
        color = 0x000000,
        description = f"Dead players can spawn a wight with 1hp, 3 mana, and 3 bounty reward in the Crossroads with `/wightspawn` by spending 3 mana! \n\nDead players can order their wight to travel to a new location for 1 of their Wight's mana with `/wighttravel`! \n\nDead players can order their wight to attack another person in their area for 69 damage by spending 1 of the wight's mana with `/wightattack`! \n\nLiving players who attack a Wight with a heavy or light attack gain the wight's bounty reward and increase the next ligma outbreak damage at the wight's location by 250! (This does not change the timing of ligma outbreaks)",
        )
    await ctx.send(embeds = buttonemb, ephemeral=False)

lightattackhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.DANGER,
    label="Light Attack",
    custom_id="Lightattack",
)

@bot.component("Lightattack")
async def button_response(ctx):
    buttonemb = interactions.api.models.message.Embed(
        title = f"Lightattack",
        color = 0x000000,
        description = f"Spend 1 mana to gain a Rage and attack an opponent in your area for 800 to 1100 damage.",
        fields = [interactions.EmbedField(name="Command",value="/lightattack",inline=True)],
        )
    await ctx.send(embeds = buttonemb, ephemeral=False)


statushelpbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Status",
    custom_id="Status",
)

@bot.component("Status")
async def button_response(ctx):
    buttonemb = interactions.api.models.message.Embed(
        title = f"Status",
        color = 0x000000,
        description = f"Use `/status` to find out more information about your current status.\n\n*Checking your status does not cost mana!*",
        fields = [interactions.EmbedField(name="Command",value="/status",inline=True)],
        )
    await ctx.send(embeds = buttonemb, ephemeral=False)

heavyattackhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.DANGER,
    label="Heavy Attack",
    custom_id="Heavyattack",
)

@bot.component("Heavyattack")
async def button_response(ctx):
    buttonemb = interactions.api.models.message.Embed(
        title = f"Heavy Attack",
        color = 0x000000,
        description = f"Spend 3 mana to gain 6 Rage and attack an opponent in your area for 3500 to 3800 damage.",
        fields =  [interactions.EmbedField(name="Command",value="/heavyattack",inline=True)],
        )
    await ctx.send(embeds = buttonemb, ephemeral=False)

interrupthelpbutton = interactions.Button(
    style=interactions.ButtonStyle.DANGER,
    label="Interrupt",
    custom_id="Interrupt",
)

@bot.component("Interrupt")
async def button_response(ctx):
    buttonemb = interactions.api.models.message.Embed(
        title = f"Interrupt",
        color = 0x000000,
        description = f"Spend 1 mana to attack an opponent in your area for 4200 damage if they are resting or evading. They stop resting/evading. The target loses all queued actions, regardless of whether they were resting/evading or not.",
        fields = [interactions.EmbedField(name="Command",value="/interrupt",inline=True)],
        )
    await ctx.send(embeds = buttonemb, ephemeral=False)


gamblehelpbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Gamble",
    custom_id="gamblehelp",
)

@bot.component("gamblehelp")
async def button_response(ctx):
    buttonemb = interactions.api.models.message.Embed(
        title = f"Gamble",
        color = 0x000000,
        description = f"Wager your health or SC on a 50/50 chance. If you lose the 50/50, you lose that much SC/HP. If you win the 50/50, you gain that much SC/HP!\n\n*This does not cost mana.*",
        fields = [interactions.EmbedField(name="Command",value="/gamble",inline=True)],
        )
    await ctx.send(embeds = buttonemb, ephemeral=False)

evadehelpbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Evade",
    custom_id="Evade",
)

@bot.component("Evade")
async def button_response(ctx):
    buttonemb = interactions.api.models.message.Embed(
        title = f"Evade",
        color = 0x000000,
        description = f"Spend 1 mana to receive no damage from light or heavy attacks while you are evading. You are evading for the next 24 hours.\n\n*You can still take actions while evading, but you are susceptible to interrupt damage.*",
        fields = [interactions.EmbedField(name="Command",value="/evade",inline=True)],
        )
    await ctx.send(embeds = buttonemb, ephemeral=False)


resthelpbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Rest",
    custom_id="Rest",
)

@bot.component("Rest")
async def button_response(ctx):
    buttonemb = interactions.api.models.message.Embed(
        title = f"Rest",
        color = 0x000000,
        description = f"Gain a mana and heal half your missing health rounded up. You are resting for the next 24 hours and cannot rest while you are resting.\n\n*You can still take actions while resting, but you are susceptible to interrupt damage.*",
        fields = [interactions.EmbedField(name="Command",value="/rest",inline=True)],
        )
    await ctx.send(embeds = buttonemb, ephemeral=False)

areactionhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Location Action",
    custom_id="AreaAction",
)

@bot.component("AreaAction")
async def button_response(ctx):
    row = interactions.spread_to_rows(crossroadshelpbutton, dungeonhelpbutton, farmlandhelpbutton, keephelpbutton, lichcastlehelpbutton, shophelpbutton, tavernhelpbutton)
    buttonemb = interactions.api.models.message.Embed(
        title = f"Locations",
        color = 0x000000,
        description = f"You can travel from any location to the Crossroads using /travel and you can travel from the Crossroads to any location using /travel \n\nLocations each have their own unique location action! Location actions cost 1 mana, but have a variety of effects. \n\nUse the buttons below to learn more about the various location actions:",
        fields = [interactions.EmbedField(name="Command",value="/travel",inline=True)],
        )
    await ctx.send(embeds = buttonemb, components = row, ephemeral=False)

useitemhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Use an Item",
    custom_id="useitem",
)

@bot.component("useitem")
async def button_response(ctx):
    buttonemb = interactions.api.models.message.Embed(
        title = f"Items",
        color = 0x000000,
        description = f"Items are either in your: \n\n**Ready Inventory**\nItems you can use with `/use` to equip or consume.\n\n**Equipped Inventory**\nItems you have equipped in the past that are giving you a passive effect.\n\nFind out more about each item below",
        fields = [interactions.EmbedField(name="Command",value="/use",inline=True)],
        )
    row = interactions.spread_to_rows(adventuringgearhelpbutton, AWPhelpbutton, crookedabacushelpbutton, goodiebaghelpbutton, tractorhelpbutton, drinkingmedalhelpbutton, lichitemhelpbutton, beerbandohelpbutton, critterihardlyknowherhelpbutton, localligmaoutbreakhelpbutton)
    await ctx.send(embeds = buttonemb, components = row, ephemeral=False)

recruithelpbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Recruit",
    custom_id="Recruit",
)

@bot.component("Recruit")
async def button_response(ctx):
    buttonemb = interactions.api.models.message.Embed(
        title = f"Recruit",
        color = 0x000000,
        description = f"Choose a player. \n\nIf you choose yourself and you belong to a team, you may leave your current team by spending a mana. \n\nIf you choose yourself and you don't belong to a team, you may create and join your own team. \n\nIf you choose another player and they have no team, they may join your team.\n\nIf you choose another player and they have a team, they may join your team by spending a mana.\n\n*Players with the same team as you are not opponents and therefore cannot be targeted by attacks or interrupts.*",
        fields = [interactions.EmbedField(name="Command",value="/recruit",inline=True)],
        )
    await ctx.send(embeds = buttonemb, ephemeral=False)

locationhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="Locations",
    custom_id="Locations",
)

@bot.component("Locations")
async def button_response(ctx):
    buttonemb = interactions.api.models.message.Embed(
        title = f"Locations",
        color = 0x000000,
        description = f"You can travel from any location to the Crossroads using /travel and you can travel from the Crossroads to any location using /travel \n\nLocations each have their own unique location action! Location actions cost 1 mana, but have a variety of effects. \n\nUse the buttons below to learn more about the various location actions:",
        fields = [interactions.EmbedField(name="Command",value="/travel",inline=True)],
        )
    row = interactions.spread_to_rows(crossroadshelpbutton, dungeonhelpbutton, farmlandhelpbutton, keephelpbutton, lichcastlehelpbutton, shophelpbutton, tavernhelpbutton)
    await ctx.send(embeds = buttonemb, components = row, ephemeral=False)

crossroadshelpbutton = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="Crossroads",
    custom_id="Crossroads",
)

@bot.component("Crossroads")
async def button_response(ctx):
    buttonemb = interactions.api.models.message.Embed(
        title = f"Crossroads",
        color = 0x000000,
        description = f"Spend 1 mana to give a player in your area a ready item from your inventory.",
        fields = [interactions.EmbedField(name="Command",value="/exchange",inline=True)],
        )
    await ctx.send(embeds = buttonemb, ephemeral=False)

dungeonhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="Dungeon",
    custom_id="Dungeon",
)

@bot.component("Dungeon")
async def button_response(ctx):
    buttonemb = interactions.api.models.message.Embed(
        title = f"Dungeon",
        color = 0x000000,
        description = f"Spend 1 mana to roll 1d4. If you roll the highest roll, gain a random item. If you roll the lowest roll, lose 1/4 of your current health. Scores expire after {int(basecd/60/60)} hours.",
        fields = [interactions.EmbedField(name="Command",value="/loot",inline=True)],
        )
    await ctx.send(embeds = buttonemb, ephemeral=False)

farmlandhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="Farmland",
    custom_id="Farmland",
)

@bot.component("Farmland")
async def button_response(ctx):
    buttonemb = interactions.api.models.message.Embed(
        title = f"Farmland",
        color = 0x000000,
        description = f"Spend 1 mana to roll 1d4. Gain the result of that roll in SCs.",
        fields = [interactions.EmbedField(name="Command",value="/farm",inline=True)],
        )
    await ctx.send(embeds = buttonemb, ephemeral=False)


keephelpbutton = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="Keep",
    custom_id="Keep",
)

@bot.component("Keep")
async def button_response(ctx):
    buttonemb = interactions.api.models.message.Embed(
        title = f"Keep",
        color = 0x000000,
        description = f"Spend 1 mana to heal the chosen player for 1/4 of their missing health.",
        fields = [interactions.EmbedField(name="Command",value="/aid",inline=True)],
        )
    await ctx.send(embeds = buttonemb, ephemeral=False)


lichcastlehelpbutton = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="Lich's Castle",
    custom_id="lichcastle",
)

@bot.component("lichcastle")
async def button_response(ctx):
    buttonemb = interactions.api.models.message.Embed(
        title = f"Lich's Castle",
        color = 0x000000,
        description = f"Spend 1 mana to roll 1d4. If you get the high roll, gain the lich's item. If you roll the low roll, lose 1/4 of your current health. Scores expire after {int(basecd/60/60)} hours.",
        fields = [interactions.EmbedField(name="Command",value="/battlelich",inline=True)],
        )
    await ctx.send(embeds = buttonemb, ephemeral=False)

shophelpbutton = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="Shop",
    custom_id="Shop",
)

@bot.component("Shop")
async def button_response(ctx):
    buttonemb = interactions.api.models.message.Embed(
        title = f"Shop",
        color = 0x000000,
        description = f"Spend 1 mana to exchange seed coins for a shop item.",
        fields = [interactions.EmbedField(name="Command",value="/trade",inline=True)],
        )
    await ctx.send(embeds = buttonemb, ephemeral=False)

tavernhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="Tavern",
    custom_id="Tavern",
)

@bot.component("Tavern")
async def button_response(ctx):
    buttonemb = interactions.api.models.message.Embed(
        title = f"Tavern",
        color = 0x000000,
        description = f"Spend 1 mana to roll 1d4. If you get the high roll, gain a drinking medal in your equipped inventory. If you roll the low roll, lose 1/4 of your current health. If you don't roll the low roll, heal for 1/4 of your missing health. Scores expire after {int(basecd/60/60)} hours.",
        fields = [interactions.EmbedField(name="Command",value="/drink",inline=True)],
        )
    await ctx.send(embeds = buttonemb, ephemeral=False)

itemhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="Items",
    custom_id="Items",
)

@bot.component("Items")
async def button_response(ctx):
    buttonemb = interactions.api.models.message.Embed(
        title = f"Items",
        color = 0x000000,
        description = f"Items fall into two broad categories: \n\n**Ready Items**\nItems you can use for effects that can be instantaneous or passive in nature.\nWhen you use a Ready Item for a passive effect, it moves to your Equipped Items.\n\n**Equipped items**\nItems you have used in the past that are giving you a passive effect.\n\nFind out more about each item below",
        fields = [interactions.EmbedField(name="Command",value="/use",inline=True)],
        )
    row = interactions.spread_to_rows(adventuringgearhelpbutton, AWPhelpbutton, crookedabacushelpbutton, goodiebaghelpbutton, tractorhelpbutton, drinkingmedalhelpbutton, lichitemhelpbutton, beerbandohelpbutton, critterihardlyknowherhelpbutton, localligmaoutbreakhelpbutton)
    await ctx.send(embeds = buttonemb, components = row, ephemeral=False)

adventuringgearhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Adventuring Gear",
    custom_id="adventuringgear",
)

@bot.component("adventuringgear")
async def button_response(ctx):
    buttonemb = interactions.api.models.message.Embed(
        title = f"Adventuring Gear",
        color = 0x000000,
        description = f"Spend 2 mana to equip this item. Increase your /loot rolls by 1 for each equipped Adventuring Gear.",
        fields = [interactions.EmbedField(name="Command",value="/use",inline=True),interactions.EmbedField(name=":coin:SC Cost",value="5",inline=True),interactions.EmbedField(name=":blue_square:Mana Cost",value="2",inline=True)],
        )
    await ctx.send(embeds = buttonemb, ephemeral=False)


localligmaoutbreakhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Local Ligma Outbreak",
    custom_id="localligmaoutbreak",
)

@bot.component("localligmaoutbreak")
async def button_response(ctx):
    buttonemb = interactions.api.models.message.Embed(
        title = f"Local Ligma Outbreak",
        color = 0x000000,
        description = f"Spend 2 mana to consume this item and deal the current ligma damage at this location to everyone in your area (including yourself).",
        fields = [interactions.EmbedField(name="Command",value="/use",inline=True),interactions.EmbedField(name=":coin:SC Cost",value="5",inline=True),interactions.EmbedField(name=":blue_square:Mana Cost",value="2",inline=True)],
        )
    await ctx.send(embeds = buttonemb, ephemeral=False)

AWPhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="AWP",
    custom_id="AWP",
)

@bot.component("AWP")
async def button_response(ctx):
    buttonemb = interactions.api.models.message.Embed(
        title = f"AWP",
        color = 0x000000,
        description = f"Spend 3 mana to equip this item. While you have an AWP equipped reduce the heavy attack mana cost to two. Doesn't stack.",
        fields = [interactions.EmbedField(name="Command",value="/use",inline=True),interactions.EmbedField(name=":coin:SC Cost",value="8",inline=True),interactions.EmbedField(name=":blue_square:Mana Cost",value="3",inline=True)],
        )
    await ctx.send(embeds = buttonemb, ephemeral=False)

crookedabacushelpbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Crooked Abacus",
    custom_id="crookedabacus",
)

@bot.component("crookedabacus")
async def button_response(ctx):
    buttonemb = interactions.api.models.message.Embed(
        title = f"Crooked Abacus",
        color = 0x000000,
        description = f"Spend 2 mana to equip this item. When you /trade or /exchange gain a SC for each Crooked Abacus you have equipped.",
        fields = [interactions.EmbedField(name="Command",value="/use",inline=True),interactions.EmbedField(name=":coin:SC Cost",value="5",inline=True),interactions.EmbedField(name=":blue_square:Mana Cost",value="2",inline=True)],
        )
    await ctx.send(embeds = buttonemb, ephemeral=False)

goodiebaghelpbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Goodie Bag",
    custom_id="goodiebag",
)

@bot.component("goodiebag")
async def button_response(ctx):
    buttonemb = interactions.api.models.message.Embed(
        title = f"Goodie Bag",
        color = 0x000000,
        description = f"Spend 1 mana to consume this item and add a random item to your ready inventory.",
        fields = [interactions.EmbedField(name="Command",value="/use",inline=True),interactions.EmbedField(name=":coin:SC Cost",value="6",inline=True),interactions.EmbedField(name=":blue_square:Mana Cost",value="1",inline=True)],
        )
    await ctx.send(embeds = buttonemb, ephemeral=False)

tractorhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Tractor",
    custom_id="tractor",
)

@bot.component("tractor")
async def button_response(ctx):
    buttonemb = interactions.api.models.message.Embed(
        title = f"Tractor",
        color = 0x000000,
        description = f"Spend 2 mana to equip this item. When you farm gain a SC for each Tractor you have equipped.",
        fields = [interactions.EmbedField(name="Command",value="/use",inline=True),interactions.EmbedField(name=":coin:SC Cost",value="5",inline=True),interactions.EmbedField(name=":blue_square:Mana Cost",value="2",inline=True)],
        )
    await ctx.send(embeds = buttonemb, ephemeral=False)

drinkingmedalhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Drinking Medal",
    custom_id="drinkingmedal",
)

@bot.component("drinkingmedal")
async def button_response(ctx):
    buttonemb = interactions.api.models.message.Embed(
        title = f"Drinking Medal",
        color = 0x000000,
        description = f"Spend 2 mana to equip this item. When you light attack increase the attack damage by 420 for each Drinking Medal you have equipped.",
        fields = [interactions.EmbedField(name="Command",value="/use",inline=True),interactions.EmbedField(name=":coin:SC Cost",value="6",inline=True),interactions.EmbedField(name=":blue_square:Mana Cost",value="2",inline=True)],
        )
    await ctx.send(embeds = buttonemb, ephemeral=False)

lichitemhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Lich's Item ",
    custom_id="lichitem",
)

@bot.component("lichitem")
async def button_response(ctx):
    buttonemb = interactions.api.models.message.Embed(
        title = f"Lich's Item",
        color = 0x000000,
        description = f"Spend 2 mana to equip this item. The next time you would die, prevent that death and lose an equipped Lich Item instead. This prevention sets your HP to 4200.",
        fields = [interactions.EmbedField(name="Command",value="/use",inline=True),interactions.EmbedField(name=":coin:SC Cost",value="15",inline=True),interactions.EmbedField(name=":blue_square:Mana Cost",value="2",inline=True)],
        )
    await ctx.send(embeds = buttonemb, ephemeral=False)

beerbandohelpbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Beer Bandolier",
    custom_id="beerbando",
)

@bot.component("beerbando")
async def button_response(ctx):
    buttonemb = interactions.api.models.message.Embed(
        title = f"Beer Bandolier",
        color = 0x000000,
        description = f"Spend 1 mana to consume this item and gain three rage.",
        fields = [interactions.EmbedField(name="Command",value="/use",inline=True),interactions.EmbedField(name=":coin:SC Cost",value="3",inline=True),interactions.EmbedField(name=":blue_square:Mana Cost",value="1",inline=True)],
        )
    await ctx.send(embeds = buttonemb, ephemeral=False)

critterihardlyknowherhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Critter? I hardly know her",
    custom_id="critterihardlyknowher",
)

@bot.component("critterihardlyknowher")
async def button_response(ctx):
    buttonemb = interactions.api.models.message.Embed(
        title = f"Critter? I hardly know her",
        color = 0x000000,
        description = f"Spend 2 mana to equip this item. When you roll for crit add one to your roll for each Critter? I hardly Know her you have equipped.\n*(Crit rolls are made on a 1d10, rolls >=10 deal 50% extra base damage)*",
        fields = [interactions.EmbedField(name="Command",value="/use",inline=True),interactions.EmbedField(name=":coin:SC Cost",value="6",inline=True),interactions.EmbedField(name=":blue_square:Mana Cost",value="2",inline=True)],
        )
    await ctx.send(embeds = buttonemb, ephemeral=False)


Bountyhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Bounties",
    custom_id="Bounties",
)

@bot.component("Bounties")
async def button_response(ctx):
    players = await getplayerdata()
    most_wanted = players[(max(players, key=lambda d: players[d]["BountyReward"]))]["Username"]
    most_wantedamt = players[(max(players, key=lambda d: players[d]["BountyReward"]))]["BountyReward"]
    if most_wantedamt == 3:
        most_wanted ="No players have an increased bounty"
    bountyemb = interactions.api.models.message.Embed(
        title = f"Bounties",
        color = 0x5764EF,
        description = f"When you kill a player with an attack or interrupt, you gain Seed Coins equal to their Bounty Reward!\n\n You may increase a player's Bounty Reward by spending a coin with the `/bounty` command.",
        fields = [interactions.EmbedField(name="Highest Bounty Player:",value=most_wanted,inline=False),interactions.EmbedField(name="Highest Bounty Amount:",value=most_wantedamt,inline=False)],
    )
    await ctx.send(embeds = bountyemb, ephemeral=False)

Ligmahelpbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Ligma",
    custom_id="Ligma",
)

@bot.component("Ligma")
async def button_response(ctx):
    ligma = await getligmadata()
    nextligmatime= ligma["ligmadate"]
    randomloc = ligma["nextlocation"]
    crossroadsdamage = 0
    if ligma["Crossroads"] > 0:
        crossroadsdamage = (ligma["Crossroads"]*250)
    dungeondamage = 0
    if ligma["Dungeon"] > 0:
        dungeondamage = (ligma["Dungeon"]*250)
    farmlanddamage = 0
    if ligma["Farmland"] > 0:
        farmlanddamage = (ligma["Farmland"]*250)
    keepdamage = 0
    if ligma["Keep"] > 0:
        keepdamage = (ligma["Keep"]*250)
    lichdamage = 0
    if ligma["Lich's Castle"] > 0:
        lichdamage = (ligma["Lich's Castle"]*250)
    taverndamage = 0
    if ligma["Tavern"] > 0:
        taverndamage = (ligma["Tavern"]*250)
    shopdamage = 0
    if ligma["Shop"] >0:
        shopdamage = (ligma["Shop"]*250)

    ligmaurl="https://media.tenor.com/K9s5fCvjG4AAAAAM/average-ligma-member-ligma.gif"
    ligmaimg = interactions.EmbedImageStruct(
                        url=ligmaurl,
                        height = 512,
                        width = 512,
                        )
    ligmaemb = interactions.api.models.message.Embed(
        title = f"Ligma",
        color = 0x5764EF,
        description = f"When the game begins a 7-day timer starts and a random location is chosen. When the timer ends, a ligma outbreak occurs at the location. The ligma damage at the random location increases by 250. Then each location does damage to each player inside equal to its own ligma damage. \n\nFinally, a new location is chosen at random and the timer is restarted with 10% less time.",
        image = ligmaimg,
        fields = [interactions.EmbedField(name="Next Ligma Time:",value=f"<t:{nextligmatime}>",inline=False),interactions.EmbedField(name="Next Ligma Outbreak Location:",value=randomloc,inline=False),interactions.EmbedField(name="Crossroads:",value=crossroadsdamage,inline=False),interactions.EmbedField(name="Dungeon:",value=dungeondamage,inline=False),interactions.EmbedField(name="Farmland:",value=farmlanddamage,inline=False),interactions.EmbedField(name="Keep:",value=keepdamage,inline=False),interactions.EmbedField(name="Lich's Castle:",value=lichdamage,inline=False),interactions.EmbedField(name="Shop:",value=shopdamage,inline=False),interactions.EmbedField(name="Tavern:",value=taverndamage,inline=False)],
    )
    await ctx.send(embeds = ligmaemb, ephemeral=False)

Ragehelpbutton = interactions.Button(
    style=interactions.ButtonStyle.DANGER,
    label="Rage",
    custom_id="Rage",
)

@bot.component("Rage")
async def button_response(ctx):
    players = await getplayerdata()
    rage = players[str(ctx.user.id)]["Rage"]
    rageheal = rage*420
    buttonemb = interactions.api.models.message.Embed(
        title = f"Rage",
        color = 0x000000,
        description = f"When you take an action that costs mana, you heal equal to your Rage times 420hp. Then you lose one Rage.",
        fields = [interactions.EmbedField(name=":fire:Rage",value=rage,inline=True),interactions.EmbedField(name="Next Rage Heal",value=rageheal,inline=True)],
        )
    await ctx.send(embeds = buttonemb, ephemeral=True)

Capshelpbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Caps",
    custom_id="Caps",
)

@bot.component("Caps")
async def button_response(ctx):
    players = await getplayerdata()
    HealCap = players[str(ctx.user.id)]["HealCap"]
    DamageCap = players[str(ctx.user.id)]["DamageCap"]
    ResetHealCap = players[str(ctx.user.id)]["ResetHealCap"]
    ResetDamageCap = players[str(ctx.user.id)]["ResetDamageCap"]
    if ResetDamageCap == 0:
        ResetDamageCap = f"{int(basecd/60/60)} hours after your next damage received."
    else:
        ResetDamageCap = f"<t:{ResetDamageCap}>"
    if ResetHealCap == 0:
        ResetHealCap = f"{int(basecd/60/60)} hours after your next healing received."
    else:
        ResetHealCap = f"<t:{ResetHealCap}>"
    buttonemb = interactions.api.models.message.Embed(
        title = f"Caps",
        color = 0x000000,
        description = f"You can only receive up to 4200 healing from your rest and rage in a given {int(basecd/60/60)} hours.\n\n You can only receive 6900 damage from other players' attacks and interrupts in a given {int(basecd/60/60)} hours.",
        fields = [interactions.EmbedField(name="Current Heal Cap",value=HealCap,inline=False),interactions.EmbedField(name="Next Heal Cap Reset",value=ResetHealCap,inline=False),interactions.EmbedField(name="Current Damage Cap",value=HealCap,inline=False),interactions.EmbedField(name="Next Damage Cap Reset",value=ResetDamageCap,inline=False)],
        )
    await ctx.send(embeds = buttonemb, ephemeral=True)

@bot.command(
    name="help",
    description="get info on a topic",
)
async def help(ctx: interactions.CommandContext,):
    players = await getplayerdata()
    current_time = int(time.time())
    channelid=ctx.channel_id
    row = interactions.spread_to_rows(actionhelpbutton, locationhelpbutton, itemhelpbutton, Ligmahelpbutton, Ragehelpbutton, Bountyhelpbutton, wighthelpbutton, Capshelpbutton)
    buttonemb = interactions.api.models.message.Embed(
        title = f"README_Link",
        color = 0x000000,
        description = f"Pick a topic below that you would like help with!",
        url = "https://github.com/plerpsandplerps/AnnouncerBot/blob/main/README.md",)
    await ctx.send(embeds = buttonemb, components = row, ephemeral=False)

gamblehpbutton = interactions.Button(
    style=interactions.ButtonStyle.DANGER,
    label="Gamble HP",
    custom_id="gamblehp",
)

@bot.component("gamblehp")
async def button_response(ctx):
    row = interactions.ActionRow(
    components=[button5hp, button25hp, button50hp, button75hp, button100hp]
)
    gambleimg = interactions.EmbedImageStruct(
                        url="https://i.imgur.com/cvbHkgt.png",
                        height = 64,
                        width = 64,
                        )
    gamblehp = interactions.api.models.message.Embed(
        title = "Gamble HP",
        color = 0xfff700,
        description = f"How much of your HP would you like to wager?",
        image = gambleimg,
        )
    await ctx.send(embeds = gamblehp, components = row, ephemeral=True)

button5hp = interactions.Button(
    style=interactions.ButtonStyle.DANGER,
    label="5 HP",
    custom_id="button5hp",
)

@bot.component("button5hp")
async def button_response(ctx):
    flip =  int(random.randint(1, 2))
    players = await getplayerdata()
    hpnumber = 5
    if flip == 1:
        hpchange = 0-hpnumber
        title = "Lost"
        color2 = 0xff0000
        tag = "lost"
        tag2 = "ribs"
    else:
        hpchange = hpnumber
        title = "Won"
        color2 = 0x1aff00
        tag = "won"
        tag2 = "loins"
    players[str(ctx.author.id)]["HP"] = players[str(ctx.author.id)]["HP"] + hpchange
    with open("players.json","w") as f:
        json.dump(players,f, indent=4)
    targethp = players[str(ctx.author.id)]["HP"]
    targetid = ctx.author.id
    authorid = ctx.author.id
    await deadcheck(targethp,targetid,authorid,players)
    hpmoji = await hpmojiconv(targethp)
    gambleimg = interactions.EmbedImageStruct(
                url="https://i.imgur.com/cvbHkgt.png",
                height = 64,
                width = 64,
                )
    gamblehp = interactions.api.models.message.Embed(
        title = f"{title}",
        color = color2,
        description = f"<@{ctx.author.id}> rolled {tag2}! <@{ctx.author.id}> {tag} {hpnumber} health with /gamble! ",
        image = gambleimg,
        fields = [interactions.EmbedField(name="HP",value=hpmoji,inline=False),interactions.EmbedField(name="HP Change",value=hpchange,inline=True)],
        )
    gamblerchannel = str(locations[players[str(ctx.author.id)]["Location"]]["Channel_ID"])
    channel = await interactions.get(bot, interactions.Channel, object_id=gamblerchannel , force='http')
    await ctx.send(embeds = gamblehp)


button25hp = interactions.Button(
    style=interactions.ButtonStyle.DANGER,
    label="25 HP",
    custom_id="button25hp",
)

@bot.component("button25hp")
async def button_response(ctx):
    flip =  int(random.randint(1, 2))
    players = await getplayerdata()
    hpnumber = 25
    if flip == 1:
        hpchange = 0-hpnumber
        title = "Lost"
        color2 = 0xff0000
        tag = "lost"
        tag2 = "ribs"
    else:
        hpchange = hpnumber
        title = "Won"
        color2 = 0x1aff00
        tag = "won"
        tag2 = "loins"
    players[str(ctx.author.id)]["HP"] = players[str(ctx.author.id)]["HP"] + hpchange
    with open("players.json","w") as f:
        json.dump(players,f, indent=4)
    targethp = players[str(ctx.author.id)]["HP"]
    targetid = ctx.author.id
    authorid = ctx.author.id
    await deadcheck(targethp,targetid,authorid,players)
    hpmoji = await hpmojiconv(targethp)
    gambleimg = interactions.EmbedImageStruct(
                url="https://i.imgur.com/cvbHkgt.png",
                height = 64,
                width = 64,
                )
    gamblehp = interactions.api.models.message.Embed(
        title = f"{title}",
        color = color2,
        description = f"<@{ctx.author.id}> rolled {tag2}! <@{ctx.author.id}> {tag} {hpnumber} health with /gamble! ",
        image = gambleimg,
        fields = [interactions.EmbedField(name="HP",value=hpmoji,inline=False),interactions.EmbedField(name="HP Change",value=hpchange,inline=True)],
        )
    gamblerchannel = str(locations[players[str(ctx.author.id)]["Location"]]["Channel_ID"])
    channel = await interactions.get(bot, interactions.Channel, object_id=gamblerchannel , force='http')
    await ctx.send(embeds = gamblehp)

button50hp = interactions.Button(
    style=interactions.ButtonStyle.DANGER,
    label="50 HP",
    custom_id="button50hp",
)

@bot.component("button50hp")
async def button_response(ctx):
    flip =  int(random.randint(1, 2))
    players = await getplayerdata()
    hpnumber = 50
    if flip == 1:
        hpchange = 0-hpnumber
        title = "Lost"
        color2 = 0xff0000
        tag = "lost"
        tag2 = "ribs"
    else:
        hpchange = hpnumber
        title = "Won"
        color2 = 0x1aff00
        tag = "won"
        tag2 = "loins"
    players[str(ctx.author.id)]["HP"] = players[str(ctx.author.id)]["HP"] + hpchange
    with open("players.json","w") as f:
        json.dump(players,f, indent=4)
    targethp = players[str(ctx.author.id)]["HP"]
    targetid = ctx.author.id
    authorid = ctx.author.id
    await deadcheck(targethp,targetid,authorid,players)
    hpmoji = await hpmojiconv(targethp)
    gambleimg = interactions.EmbedImageStruct(
                url="https://i.imgur.com/cvbHkgt.png",
                height = 64,
                width = 64,
                )
    gamblehp = interactions.api.models.message.Embed(
        title = f"{title}",
        color = color2,
        description = f"<@{ctx.author.id}> rolled {tag2}! <@{ctx.author.id}> {tag} {hpnumber} health with /gamble! ",
        image = gambleimg,
        fields = [interactions.EmbedField(name="HP",value=hpmoji,inline=False),interactions.EmbedField(name="HP Change",value=hpchange,inline=True)],
        )
    gamblerchannel = str(locations[players[str(ctx.author.id)]["Location"]]["Channel_ID"])
    channel = await interactions.get(bot, interactions.Channel, object_id=gamblerchannel , force='http')
    await ctx.send(embeds = gamblehp)

button75hp = interactions.Button(
    style=interactions.ButtonStyle.DANGER,
    label="75 HP",
    custom_id="button75hp",
)

@bot.component("button75hp")
async def button_response(ctx):
    flip =  int(random.randint(1, 2))
    players = await getplayerdata()
    hpnumber = 75
    if flip == 1:
        hpchange = 0-hpnumber
        title = "Lost"
        color2 = 0xff0000
        tag = "lost"
        tag2 = "ribs"
    else:
        hpchange = hpnumber
        title = "Won"
        color2 = 0x1aff00
        tag = "won"
        tag2 = "loins"
    players[str(ctx.author.id)]["HP"] = players[str(ctx.author.id)]["HP"] + hpchange
    with open("players.json","w") as f:
        json.dump(players,f, indent=4)
    targethp = players[str(ctx.author.id)]["HP"]
    targetid = ctx.author.id
    authorid = ctx.author.id
    await deadcheck(targethp,targetid,authorid,players)
    hpmoji = await hpmojiconv(targethp)
    gambleimg = interactions.EmbedImageStruct(
                url="https://i.imgur.com/cvbHkgt.png",
                height = 64,
                width = 64,
                )
    gamblehp = interactions.api.models.message.Embed(
        title = f"{title}",
        color = color2,
        description = f"<@{ctx.author.id}> rolled {tag2}! <@{ctx.author.id}> {tag} {hpnumber} health with /gamble! ",
        image = gambleimg,
        fields = [interactions.EmbedField(name="HP",value=hpmoji,inline=False),interactions.EmbedField(name="HP Change",value=hpchange,inline=True)],
        )
    gamblerchannel = str(locations[players[str(ctx.author.id)]["Location"]]["Channel_ID"])
    channel = await interactions.get(bot, interactions.Channel, object_id=gamblerchannel , force='http')
    await ctx.send(embeds = gamblehp)

button100hp = interactions.Button(
    style=interactions.ButtonStyle.DANGER,
    label="100 HP",
    custom_id="button100hp",
)

@bot.component("button100hp")
async def button_response(ctx):
    flip =  int(random.randint(1, 2))
    players = await getplayerdata()
    hpnumber = 100
    if flip == 1:
        hpchange = 0-hpnumber
        title = "Lost"
        color2 = 0xff0000
        tag = "lost"
        tag2 = "ribs"
    else:
        hpchange = hpnumber
        title = "Won"
        color2 = 0x1aff00
        tag = "won"
        tag2 = "loins"
    players[str(ctx.author.id)]["HP"] = players[str(ctx.author.id)]["HP"] + hpchange
    with open("players.json","w") as f:
        json.dump(players,f, indent=4)
    targethp = players[str(ctx.author.id)]["HP"]
    targetid = ctx.author.id
    authorid = ctx.author.id
    await deadcheck(targethp,targetid,authorid,players)
    hpmoji = await hpmojiconv(targethp)
    gambleimg = interactions.EmbedImageStruct(
                url="https://i.imgur.com/cvbHkgt.png",
                height = 64,
                width = 64,
                )
    gamblehp = interactions.api.models.message.Embed(
        title = f"{title}",
        color = color2,
        description = f"<@{ctx.author.id}> rolled {tag2}! <@{ctx.author.id}> {tag} {hpnumber} health with /gamble! ",
        image = gambleimg,
        fields = [interactions.EmbedField(name="HP",value=hpmoji,inline=False),interactions.EmbedField(name="HP Change",value=hpchange,inline=True)],
        )
    gamblerchannel = str(locations[players[str(ctx.author.id)]["Location"]]["Channel_ID"])
    channel = await interactions.get(bot, interactions.Channel, object_id=gamblerchannel , force='http')
    await ctx.send(embeds = gamblehp)

gamblescbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Gamble SC",
    custom_id="gamblesc",
)

@bot.component("gamblesc")
async def button_response(ctx):
    row = interactions.ActionRow(
    components=[button1sc, button2sc, button3sc, button4sc, button5sc]
)
    gambleimg = interactions.EmbedImageStruct(
                        url="https://i.imgur.com/cvbHkgt.png",
                        height = 64,
                        width = 64,
                        )
    gamblesc = interactions.api.models.message.Embed(
        title = "Gamble SC",
        color = 0xfff700,
        description = f"How much of your SC would you like to wager?",
        image = gambleimg,
        )
    await ctx.send(embeds = gamblesc, components = row, ephemeral=True)

button1sc = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="1 SC",
    custom_id="button1sc",
)

@bot.component("button1sc")
async def button_response(ctx):
    flip =  int(random.randint(1, 2))
    players = await getplayerdata()
    scnumber = 1
    if players[str(ctx.author.id)]["SC"] < scnumber:
        gambleimg = interactions.EmbedImageStruct(
                    url="https://i.imgur.com/cvbHkgt.png",
                    height = 64,
                    width = 64,
                    )
        gamblehp = interactions.api.models.message.Embed(
            title = f"You don't have {scnumber} to Gamble!",
            color = 0xff0000,
            description = f"<@{ctx.author.id}> doesn't have the SC to gamble!",
            image = gambleimg,
            )
        gamblerchannel = str(locations[players[str(ctx.author.id)]["Location"]]["Channel_ID"])
        channel = await interactions.get(bot, interactions.Channel, object_id=gamblerchannel , force='http')
        await ctx.send(embeds = gamblehp)
    else:
        if flip == 1:
            scchange = 0-scnumber
            title = "Lost"
            color2 = 0xff0000
            tag = "lost"
            tag2 = "ribs"
        else:
            scchange = scnumber
            title = "Won"
            color2 = 0x1aff00
            tag = "won"
            tag2 = "loins"
        players[str(ctx.author.id)]["SC"] = players[str(ctx.author.id)]["SC"] + scchange
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
        targetSC = players[str(ctx.author.id)]["SC"]
        gambleimg = interactions.EmbedImageStruct(
                    url="https://i.imgur.com/cvbHkgt.png",
                    height = 64,
                    width = 64,
                    )
        gamblehp = interactions.api.models.message.Embed(
            title = f"{title}",
            color = color2,
            description = f"<@{ctx.author.id}> rolled {tag2}! <@{ctx.author.id}> {tag} {scnumber} SC with /gamble! ",
            image = gambleimg,
            fields = [interactions.EmbedField(name="SC:coin:",value=targetSC,inline=False),interactions.EmbedField(name="SC Change",value=scchange,inline=True)],
            )
        gamblerchannel = str(locations[players[str(ctx.author.id)]["Location"]]["Channel_ID"])
        channel = await interactions.get(bot, interactions.Channel, object_id=gamblerchannel , force='http')
        await ctx.send(embeds = gamblehp)

button2sc = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="2 SC",
    custom_id="button2sc",
)

@bot.component("button2sc")
async def button_response(ctx):
    flip =  int(random.randint(1, 2))
    players = await getplayerdata()
    scnumber = 2
    if players[str(ctx.author.id)]["SC"] < scnumber:
        gambleimg = interactions.EmbedImageStruct(
                    url="https://i.imgur.com/cvbHkgt.png",
                    height = 64,
                    width = 64,
                    )
        gamblehp = interactions.api.models.message.Embed(
            title = f"You don't have {scnumber} to Gamble!",
            color = 0xff0000,
            description = f"<@{ctx.author.id}> doesn't have the SC to gamble!",
            image = gambleimg,
            )
        gamblerchannel = str(locations[players[str(ctx.author.id)]["Location"]]["Channel_ID"])
        channel = await interactions.get(bot, interactions.Channel, object_id=gamblerchannel , force='http')
        await ctx.send(embeds = gamblehp)
    else:
        if flip == 1:
            scchange = 0-scnumber
            title = "Lost"
            color2 = 0xff0000
            tag = "lost"
            tag2 = "ribs"
        else:
            scchange = scnumber
            title = "Won"
            color2 = 0x1aff00
            tag = "won"
            tag2 = "loins"
        players[str(ctx.author.id)]["SC"] = players[str(ctx.author.id)]["SC"] + scchange
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
        targetSC = players[str(ctx.author.id)]["SC"]
        gambleimg = interactions.EmbedImageStruct(
                    url="https://i.imgur.com/cvbHkgt.png",
                    height = 64,
                    width = 64,
                    )
        gamblehp = interactions.api.models.message.Embed(
            title = f"{title}",
            color = color2,
            description = f"<@{ctx.author.id}> rolled {tag2}! <@{ctx.author.id}> {tag} {scnumber} SC with /gamble! ",
            image = gambleimg,
            fields = [interactions.EmbedField(name="SC:coin:",value=targetSC,inline=False),interactions.EmbedField(name="SC Change",value=scchange,inline=True)],
            )
        gamblerchannel = str(locations[players[str(ctx.author.id)]["Location"]]["Channel_ID"])
        channel = await interactions.get(bot, interactions.Channel, object_id=gamblerchannel , force='http')
        await ctx.send(embeds = gamblehp)

button3sc = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="3 SC",
    custom_id="button3sc",
)

@bot.component("button3sc")
async def button_response(ctx):
    flip =  int(random.randint(1, 2))
    players = await getplayerdata()
    scnumber = 3
    if players[str(ctx.author.id)]["SC"] < scnumber:
        gambleimg = interactions.EmbedImageStruct(
                    url="https://i.imgur.com/cvbHkgt.png",
                    height = 64,
                    width = 64,
                    )
        gamblehp = interactions.api.models.message.Embed(
            title = f"You don't have {scnumber} to Gamble!",
            color = 0xff0000,
            description = f"<@{ctx.author.id}> doesn't have the SC to gamble!",
            image = gambleimg,
            )
        gamblerchannel = str(locations[players[str(ctx.author.id)]["Location"]]["Channel_ID"])
        channel = await interactions.get(bot, interactions.Channel, object_id=gamblerchannel , force='http')
        await ctx.send(embeds = gamblehp)
    else:
        if flip == 1:
            scchange = 0-scnumber
            title = "Lost"
            color2 = 0xff0000
            tag = "lost"
            tag2 = "ribs"
        else:
            scchange = scnumber
            title = "Won"
            color2 = 0x1aff00
            tag = "won"
            tag2 = "loins"
        players[str(ctx.author.id)]["SC"] = players[str(ctx.author.id)]["SC"] + scchange
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
        targetSC = players[str(ctx.author.id)]["SC"]
        gambleimg = interactions.EmbedImageStruct(
                    url="https://i.imgur.com/cvbHkgt.png",
                    height = 64,
                    width = 64,
                    )
        gamblehp = interactions.api.models.message.Embed(
            title = f"{title}",
            color = color2,
            description = f"<@{ctx.author.id}> rolled {tag2}! <@{ctx.author.id}> {tag} {scnumber} SC with /gamble! ",
            image = gambleimg,
            fields = [interactions.EmbedField(name="SC:coin:",value=targetSC,inline=False),interactions.EmbedField(name="SC Change",value=scchange,inline=True)],
            )
        gamblerchannel = str(locations[players[str(ctx.author.id)]["Location"]]["Channel_ID"])
        channel = await interactions.get(bot, interactions.Channel, object_id=gamblerchannel , force='http')
        await ctx.send(embeds = gamblehp)

button4sc = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="4 SC",
    custom_id="button4sc",
)

@bot.component("button4sc")
async def button_response(ctx):
    flip =  int(random.randint(1, 2))
    players = await getplayerdata()
    scnumber = 4
    if players[str(ctx.author.id)]["SC"] < scnumber:
        gambleimg = interactions.EmbedImageStruct(
                    url="https://i.imgur.com/cvbHkgt.png",
                    height = 64,
                    width = 64,
                    )
        gamblehp = interactions.api.models.message.Embed(
            title = f"You don't have {scnumber} to Gamble!",
            color = 0xff0000,
            description = f"<@{ctx.author.id}> doesn't have the SC to gamble!",
            image = gambleimg,
            )
        gamblerchannel = str(locations[players[str(ctx.author.id)]["Location"]]["Channel_ID"])
        channel = await interactions.get(bot, interactions.Channel, object_id=gamblerchannel , force='http')
        await ctx.send(embeds = gamblehp)
    else:
        if flip == 1:
            scchange = 0-scnumber
            title = "Lost"
            color2 = 0xff0000
            tag = "lost"
            tag2 = "ribs"
        else:
            scchange = scnumber
            title = "Won"
            color2 = 0x1aff00
            tag = "won"
            tag2 = "loins"
        players[str(ctx.author.id)]["SC"] = players[str(ctx.author.id)]["SC"] + scchange
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
        targetSC = players[str(ctx.author.id)]["SC"]
        gambleimg = interactions.EmbedImageStruct(
                    url="https://i.imgur.com/cvbHkgt.png",
                    height = 64,
                    width = 64,
                    )
        gamblehp = interactions.api.models.message.Embed(
            title = f"{title}",
            color = color2,
            description = f"<@{ctx.author.id}> rolled {tag2}! <@{ctx.author.id}> {tag} {scnumber} SC with /gamble! ",
            image = gambleimg,
            fields = [interactions.EmbedField(name="SC:coin:",value=targetSC,inline=False),interactions.EmbedField(name="SC Change",value=scchange,inline=True)],
            )
        gamblerchannel = str(locations[players[str(ctx.author.id)]["Location"]]["Channel_ID"])
        channel = await interactions.get(bot, interactions.Channel, object_id=gamblerchannel , force='http')
        await ctx.send(embeds = gamblehp)

button5sc = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="5 SC",
    custom_id="button5sc",
)

@bot.component("button5sc")
async def button_response(ctx):
    flip =  int(random.randint(1, 2))
    players = await getplayerdata()
    scnumber = 5
    if players[str(ctx.author.id)]["SC"] < scnumber:
        gambleimg = interactions.EmbedImageStruct(
                    url="https://i.imgur.com/cvbHkgt.png",
                    height = 64,
                    width = 64,
                    )
        gamblehp = interactions.api.models.message.Embed(
            title = f"You don't have {scnumber} to Gamble!",
            color = 0xff0000,
            description = f"<@{ctx.author.id}> doesn't have the SC to gamble!",
            image = gambleimg,
            )
        gamblerchannel = str(locations[players[str(ctx.author.id)]["Location"]]["Channel_ID"])
        channel = await interactions.get(bot, interactions.Channel, object_id=gamblerchannel , force='http')
        await ctx.send(embeds = gamblehp)
    else:
        if flip == 1:
            scchange = 0-scnumber
            title = "Lost"
            color2 = 0xff0000
            tag = "lost"
            tag2 = "ribs"
        else:
            scchange = scnumber
            title = "Won"
            color2 = 0x1aff00
            tag = "won"
            tag2 = "loins"
        players[str(ctx.author.id)]["SC"] = players[str(ctx.author.id)]["SC"] + scchange
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
        targetSC = players[str(ctx.author.id)]["SC"]
        gambleimg = interactions.EmbedImageStruct(
                    url="https://i.imgur.com/cvbHkgt.png",
                    height = 64,
                    width = 64,
                    )
        gamblehp = interactions.api.models.message.Embed(
            title = f"{title}",
            color = color2,
            description = f"<@{ctx.author.id}> rolled {tag2}! <@{ctx.author.id}> {tag} {scnumber} SC with /gamble! ",
            image = gambleimg,
            fields = [interactions.EmbedField(name="SC:coin:",value=targetSC,inline=False),interactions.EmbedField(name="SC Change",value=scchange,inline=True)],
            )
        gamblerchannel = str(locations[players[str(ctx.author.id)]["Location"]]["Channel_ID"])
        channel = await interactions.get(bot, interactions.Channel, object_id=gamblerchannel , force='http')
        await ctx.send(embeds = gamblehp)

@bot.command(
    name="gamble",
    description="gamble to gain or lose health or SC.",
    scope = guildid,
)
async def gamble(ctx: interactions.CommandContext,):
    players = await getplayerdata()
    current_time = int(time.time())
    authorid=ctx.author.id
    channelid=ctx.channel_id
    row = interactions.ActionRow(
    components=[gamblehpbutton, gamblescbutton]
)
    gambleimg = interactions.EmbedImageStruct(
                        url="https://i.imgur.com/cvbHkgt.png",
                        height = 64,
                        width = 64,
                        )
    gambleemb = interactions.api.models.message.Embed(
        title = f"What would you like to gamble?",
        color = 0xfff700,
        description = f"Choose health or SC",
        image = gambleimg,
        )
    await ctx.send(embeds = gambleemb, components = row, ephemeral = True)

@bot.command(
    name="quit",
    description="quit the game",
)
async def quit(ctx: interactions.CommandContext,):
    players = await getplayerdata()
    current_time = int(time.time())
    channelid=ctx.channel_id
    row = interactions.ActionRow(
    components=[yesquitbutton, noquitbutton ]
)
    await ctx.send(f"Are you sure you want to quit the game?", components = row, ephemeral = True)

yesquitbutton = interactions.Button(
    style=interactions.ButtonStyle.DANGER,
    label="Yes",
    custom_id="yesquitbutton",
)

@bot.component("yesquitbutton")
async def button_response(ctx):
    players = await getplayerdata()
    players[str(ctx.author.id)]["HP"] = 0
    targethp = 0
    targetid = str(ctx.author.id)
    authorid = str(ctx.author.id)
    await deadcheck(targethp,targetid,authorid,players)
    reminders = await getreminderdata()
    reminders[str(ctx.user.id)] = {}
    with open("reminders.json","w") as m:
        json.dump(reminders,m, indent=4)


noquitbutton = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="No, I don't want to quit",
    custom_id="noquitbutton",
)

@bot.component("noquitbutton")
async def button_response(ctx):
    await ctx.send(f"You chose not to die! Continue playing with a command!", ephemeral = True)


@bot.command(
    name="reminders",
    description="enable or disable reminders for the game",
)
async def reminders(ctx: interactions.CommandContext,):
    players = await getplayerdata()
    current_time = int(time.time())
    channelid=ctx.channel_id
    row = interactions.ActionRow(
    components=[yesremindme, noremindme ]
)
    await ctx.send(f"Do you want to enable reminders for the game?", components = row, ephemeral = False)

yesremindme = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="Yes, I want reminders",
    custom_id="yesremindme",
)

@bot.component("yesremindme")
async def button_response(ctx):
    reminders = await getreminderdata()
    user = await interactions.get(bot, interactions.Member, object_id=(ctx.user.id), guild_id=guildid, force='http')
    reminders.pop(str(ctx.user.id), None)
    with open("reminders.json","w") as m:
        json.dump(reminders,m, indent=4)
    await ctx.send(f"<@{ctx.user.id}> has enabled reminders!", ephemeral = False)

noremindme = interactions.Button(
    style=interactions.ButtonStyle.DANGER,
    label="No, I don't want reminders",
    custom_id="noremindme",
)

@bot.component("noremindme")
async def button_response(ctx):
    reminders = await getreminderdata()
    reminders[str(ctx.user.id)] = {}
    with open("reminders.json","w") as m:
        json.dump(reminders,m, indent=4)
    await ctx.send(f"You chose to not receive reminders!", ephemeral = True)

@bot.command(
    name="status",
    description="check your status.",
    scope = guildid,
)
async def status (ctx: interactions.CommandContext):
    players = await getplayerdata()
    shop = await getshopdata()
    hp_pull = players[str(ctx.author.id)]["HP"]
    location_pull = players[str(ctx.author.id)]["Location"]
    SC_pull = players[str(ctx.author.id)]["SC"]
    Rage_pull = players[str(ctx.author.id)]["Rage"]
    ReadyInventory_pull = players[str(ctx.author.id)]["ReadyInventory"]
    EquippedInventory_pull = players[str(ctx.author.id)]["EquippedInventory"]
    if EquippedInventory_pull == " ":
        EquippedInventory_pull = "Nothing in Equipped Inventory"
    else :
        EquippedInventory_pull = players[str(ctx.author.id)]["EquippedInventory"]
    Lastaction_pull = players[str(ctx.author.id)]["Lastaction"]
    Nextaction_pull = players[str(ctx.author.id)]["Nextaction"]
    words = players[ctx.author.id]['Nextaction'].split()
    mana_pull = players[str(ctx.author.id)]["Mana"]
    manamoji = await manamojiconv(mana_pull)
    mana_date = players[str(ctx.author.id)]["NextMana"]
    print(words)
    displayaction = "displayerror"
    if len(words) == 0:
        displayaction = "No queued action"
    elif len(words) == 1:
        displayaction = f"{words[0]}"
    elif words[1] in players:
        actiontargetid = words[1]
        displayaction = f"{words[0]} <@{actiontargetid}>"
        if len(words) == 3:
            displayaction = displayaction + " " + words[2]
    elif words[1] in locations:
        displayaction = f"{words}"
    elif words[1] in shop:
        displayaction = f"{words}"
    if ReadyInventory_pull =="":
        ReadyInventory_pull = "Nothing in Ready Inventory"
    else:
        ReadyInventory_pull = ReadyInventory_pull
    print(displayaction)
    mana_date = "<t:"+str(mana_date)+">"
    Team_pull = players[str(ctx.author.id)]["Team"]
    TeamOffer_pull = players[str(ctx.author.id)]["NewTeam"]
    hpmoji = await hpmojiconv(hp_pull)
    status = interactions.api.models.message.Embed(
        title = "Status",
        color = 0xf00c5f,
        fields = [interactions.EmbedField(name="HP",value=hpmoji),interactions.EmbedField(name="Mana",value=manamoji,inline=True),interactions.EmbedField(name="Next Mana",value=mana_date,inline=True),interactions.EmbedField(name="Location",value=location_pull,inline = False),interactions.EmbedField(name=":fire:Rage",value=Rage_pull,inline=True),interactions.EmbedField(name=":coin:SC",value=SC_pull,inline=True),interactions.EmbedField(name="Current Team",value=Team_pull,inline = False),interactions.EmbedField(name="Joinable Team",value=TeamOffer_pull,inline = True),interactions.EmbedField(name=":school_satchel:Ready Inventory",value=ReadyInventory_pull),interactions.EmbedField(name=":shield:Equipped Inventory",value=EquippedInventory_pull,inline=True),interactions.EmbedField(name=":alarm_clock:Next Action:",value=displayaction),interactions.EmbedField(name=":coin:Reward for Killing you:",value=players[str(ctx.author.id)]["BountyReward"])],
    )
    row = interactions.spread_to_rows(moreinfobutton, queuecancel, orderoptout)
    await ctx.send(embeds=status,ephemeral=True, components = row)

#travelto
async def dotravel(authorid,destination):
    await rage(authorid)
    travelurl = "https://media.tenor.com/Wm6TRmkD-_IAAAAC/juggernaut-xmen.gif"
    players = await getplayerdata()
    players[str(authorid)]["Nextaction"] = ""
    current_time = int(time.time())
    user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
    travelimg = interactions.EmbedImageStruct(
                        url=travelurl,
                        height = 512,
                        width = 512,
                        )
    if players[str(authorid)]["Location"] == "Crossroads" or destination == "Crossroads":
        oldtravelerchannel=str(locations[players[str(authorid)]["Location"]]["Channel_ID"])
        oldlocation = players[str(authorid)]["Location"]
        newlocation = destination
        players[str(authorid)]["Mana"] = players[str(authorid)]["Mana"] -1
        players[str(authorid)]["Lastaction"] = "travelto"
        players[str(authorid)]["Location"] = destination
        await user.remove_role(role=locations["Dungeon"]["Role_ID"], guild_id=guildid)
        await user.remove_role(role=locations["Farmland"]["Role_ID"], guild_id=guildid)
        await user.remove_role(role=locations["Keep"]["Role_ID"], guild_id=guildid)
        await user.remove_role(role=locations["Lich's Castle"]["Role_ID"], guild_id=guildid)
        await user.remove_role(role=locations["Shop"]["Role_ID"], guild_id=guildid)
        await user.remove_role(role=locations["Tavern"]["Role_ID"], guild_id=guildid)
        await user.remove_role(role=locations["Crossroads"]["Role_ID"], guild_id=guildid)
        await user.add_role(role=locations[str(destination)]["Role_ID"], guild_id=guildid)
        with open("players.json", "w") as f:
            json.dump(players, f, indent=4)
        newtravelerchannel=str(locations[players[str(authorid)]["Location"]]["Channel_ID"])
        travelemb = interactions.api.models.message.Embed(
            title = f"{players[str(authorid)]['Username']} arrives at the {newlocation}!",
            color = 0xad7205,
            description = f"<@{authorid}> saunters over from the {oldlocation}!",
            image = travelimg,
            fields = [interactions.EmbedField(name="Old Location",value=oldlocation,inline=True),interactions.EmbedField(name="New Location",value=newlocation,inline=True)],
        )
        newchannel = await interactions.get(bot, interactions.Channel, object_id=newtravelerchannel , force='http')
        oldchannel = await interactions.get(bot, interactions.Channel, object_id=oldtravelerchannel , force='http')
        await newchannel.send(embeds=travelemb)
        travelurl = "https://media.tenor.com/IvLly3CfFLIAAAAC/juggernaut-xmen.gif"
        travelimg = interactions.EmbedImageStruct(
                            url=travelurl,
                            height = 512,
                            width = 512,
                            )
        travelemb = interactions.api.models.message.Embed(
            title = f"{players[str(authorid)]['Username']} leaves the {oldlocation}!",
            color = 0xad7205,
            description = f"<@{authorid}> saunters over to the {newlocation}!",
            image = travelimg,
            fields = [interactions.EmbedField(name="Old Location",value=oldlocation,inline=True),interactions.EmbedField(name="New Location",value=newlocation,inline=True)],
        )
        await oldchannel.send(embeds=travelemb)
    else:
        user = await interactions.get(bot, interactions.Member, object_id=authorid, force='http')
        await send_message(f"You must travel to the Crossroads before you can travel there!", user_id=[user])


@bot.command(
    name="travel",
    description="1mana. travel to any location from the crossroads or from any location to the crossroads.",
    scope = guildid,
)
async def travel(ctx: interactions.CommandContext):
    players = await getplayerdata()
    current_time = int(time.time())
    channelid=ctx.channel_id
    if str(ctx.author.id) in players:
        cost = 1
        Mana_pull = players[str(ctx.author.id)]["Mana"]
        if players[str(ctx.author.id)]["Location"] != "Crossroads":
            row = interactions.spread_to_rows(traveltocrossroadsbutton)
            travelurl = "https://i.makeagif.com/media/8-16-2015/tMsEme.gif"
            travelimg = interactions.EmbedImageStruct(
                                url=travelurl,
                                height = 512,
                                width = 512,
                                )
            travelemb = interactions.api.models.message.Embed(
                title = f"You aren't in the Crossroads",
                color = 0xad7205,
                image = travelimg,
                description = f"You must travel to the crossroads before you travel to another location!",
                )
            await ctx.send(embeds=travelemb, components = row, ephemeral = True)
        else:
            row = interactions.spread_to_rows(traveltodungeonbutton, traveltofarmlandbutton, traveltokeepbutton, traveltolichcastlebutton, traveltoshopbutton, traveltotavernbutton)
            travelurl = "https://i.makeagif.com/media/8-16-2015/tMsEme.gif"
            travelimg = interactions.EmbedImageStruct(
                                url=travelurl,
                                height = 512,
                                width = 512,
                                )
            travelemb = interactions.api.models.message.Embed(
                title = f"You are in the Crossroads",
                color = 0xad7205,
                image = travelimg,
                description = f"Where would you like to travel?",
                )
            await ctx.send(embeds=travelemb, components = row, ephemeral = True)
    else:
        await ctx.send(f"You aren't in the competition!" , ephemeral = True)

traveltocrossroadsbutton = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="Travel to Crossroads!",
    custom_id="traveltocrossroadsbutton",
)

@bot.component("traveltocrossroadsbutton")
async def button_response(ctx):
    players = await getplayerdata()
    current_time = int(time.time())
    destination = "Crossroads"
    channelid=ctx.channel_id
    cost = 1
    Mana_pull = players[str(ctx.author.id)]["Mana"]
    if cost-Mana_pull > 0:
        enoughmanatime = (players[str(ctx.author.id)]["NextMana"])+(max((cost-Mana_pull-1),0))*basecd
        players[str(ctx.author.id)]["ReadyDate"] = enoughmanatime
        with open("players.json", "w") as f:
            json.dump(players, f, indent=4)
        await queuenexttarget("travel",ctx,destination)
        await ctx.send(f"You don't have the mana for that! The action has been queued for <t:{enoughmanatime}>.", ephemeral = True)
    else:
        manamoji = await manamojiconv(Mana_pull- cost)
        travelemb = interactions.api.models.message.Embed(
            title = f"You travel!",
            color = 0xad7205,
            fields = [interactions.EmbedField(name="Mana Remaining",value=manamoji,inline=True)],
        )
        await ctx.send(embeds=travelemb,ephemeral = True)
        await dotravel(ctx.author.id,destination)

traveltodungeonbutton = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="Travel to Dungeon!",
    custom_id="traveltodungeonbutton",
)

@bot.component("traveltodungeonbutton")
async def button_response(ctx):
    players = await getplayerdata()
    current_time = int(time.time())
    destination = "Dungeon"
    channelid=ctx.channel_id
    cost = 1
    Mana_pull = players[str(ctx.author.id)]["Mana"]
    if cost-Mana_pull > 0:
        enoughmanatime = (players[str(ctx.author.id)]["NextMana"])+(max((cost-Mana_pull-1),0))*basecd
        players[str(ctx.author.id)]["ReadyDate"] = (players[str(ctx.author.id)]["NextMana"])+(max((cost-Mana_pull-1),0))*basecd
        with open("players.json", "w") as f:
            json.dump(players, f, indent=4)
        await queuenexttarget("travel",ctx,destination)
        await ctx.send(f"You don't have the mana to travel! The travel has been queued for <t:{enoughmanatime}>.", ephemeral = True)
    else:
        manamoji = await manamojiconv(Mana_pull- cost)
        travelemb = interactions.api.models.message.Embed(
            title = f"You travel!",
            color = 0xad7205,
            fields = [interactions.EmbedField(name="Mana Remaining",value=manamoji,inline=True)],
        )
        await ctx.send(embeds=travelemb,ephemeral = True)
        await dotravel(ctx.author.id,destination)


traveltofarmlandbutton = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="Travel to Farmland!",
    custom_id="traveltofarmlandbutton",
)

@bot.component("traveltofarmlandbutton")
async def button_response(ctx):
    players = await getplayerdata()
    current_time = int(time.time())
    destination = "Farmland"
    channelid=ctx.channel_id
    cost = 1
    Mana_pull = players[str(ctx.author.id)]["Mana"]
    if cost-Mana_pull > 0:
        enoughmanatime = (players[str(ctx.author.id)]["NextMana"])+(max((cost-Mana_pull-1),0))*basecd
        players[str(ctx.author.id)]["ReadyDate"] = (players[str(ctx.author.id)]["NextMana"])+(max((cost-Mana_pull-1),0))*basecd
        with open("players.json", "w") as f:
            json.dump(players, f, indent=4)
        await queuenexttarget("travel",ctx,destination)
        await ctx.send(f"You don't have the mana to travel! The travel has been queued for <t:{enoughmanatime}>.", ephemeral = True)
    else:
        manamoji = await manamojiconv(Mana_pull- cost)
        travelemb = interactions.api.models.message.Embed(
            title = f"You travel!",
            color = 0xad7205,
            fields = [interactions.EmbedField(name="Mana Remaining",value=manamoji,inline=True)],
        )
        await ctx.send(embeds=travelemb,ephemeral = True)
        await dotravel(ctx.author.id,destination)

traveltokeepbutton = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="Travel to Keep!",
    custom_id="traveltokeepbutton",
)

@bot.component("traveltokeepbutton")
async def button_response(ctx):
    players = await getplayerdata()
    current_time = int(time.time())
    destination = "Keep"
    channelid=ctx.channel_id
    cost = 1
    Mana_pull = players[str(ctx.author.id)]["Mana"]
    if cost-Mana_pull > 0:
        enoughmanatime = (players[str(ctx.author.id)]["NextMana"])+(max((cost-Mana_pull-1),0))*basecd
        players[str(ctx.author.id)]["ReadyDate"] = (players[str(ctx.author.id)]["NextMana"])+(max((cost-Mana_pull-1),0))*basecd
        with open("players.json", "w") as f:
            json.dump(players, f, indent=4)
        await queuenexttarget("travel",ctx,destination)
        await ctx.send(f"You don't have the mana to travel! The travel has been queued for <t:{enoughmanatime}>.", ephemeral = True)
    else:
        manamoji = await manamojiconv(Mana_pull- cost)
        travelemb = interactions.api.models.message.Embed(
            title = f"You travel!",
            color = 0xad7205,
            fields = [interactions.EmbedField(name="Mana Remaining",value=manamoji,inline=True)],
        )
        await ctx.send(embeds=travelemb,ephemeral = True)
        await dotravel(ctx.author.id,destination)

traveltolichcastlebutton = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="Travel to Lich's Castle!",
    custom_id="traveltolichcastlebutton",
)

@bot.component("traveltolichcastlebutton")
async def button_response(ctx):
    players = await getplayerdata()
    current_time = int(time.time())
    destination = "Lich's Castle"
    channelid=ctx.channel_id
    cost = 1
    Mana_pull = players[str(ctx.author.id)]["Mana"]
    if cost-Mana_pull > 0:
        enoughmanatime = (players[str(ctx.author.id)]["NextMana"])+(max((cost-Mana_pull-1),0))*basecd
        players[str(ctx.author.id)]["ReadyDate"] = (players[str(ctx.author.id)]["NextMana"])+(max((cost-Mana_pull-1),0))*basecd
        with open("players.json", "w") as f:
            json.dump(players, f, indent=4)
        await queuenexttarget("travel",ctx,destination)
        await ctx.send(f"You don't have the mana to travel! The travel has been queued for <t:{enoughmanatime}>.", ephemeral = True)
    else:
        manamoji = await manamojiconv(Mana_pull- cost)
        travelemb = interactions.api.models.message.Embed(
            title = f"You travel!",
            color = 0xad7205,
            fields = [interactions.EmbedField(name="Mana Remaining",value=manamoji,inline=True)],
        )
        await ctx.send(embeds=travelemb,ephemeral = True)
        await dotravel(ctx.author.id,destination)

traveltoshopbutton = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="Travel to Shop!",
    custom_id="traveltoshopbutton",
)

@bot.component("traveltoshopbutton")
async def button_response(ctx):
    players = await getplayerdata()
    current_time = int(time.time())
    destination = "Shop"
    channelid=ctx.channel_id
    cost = 1
    Mana_pull = players[str(ctx.author.id)]["Mana"]
    if cost-Mana_pull > 0:
        enoughmanatime = (players[str(ctx.author.id)]["NextMana"])+(max((cost-Mana_pull-1),0))*basecd
        players[str(ctx.author.id)]["ReadyDate"] = (players[str(ctx.author.id)]["NextMana"])+(max((cost-Mana_pull-1),0))*basecd
        with open("players.json", "w") as f:
            json.dump(players, f, indent=4)
        await queuenexttarget("travel",ctx,destination)
        await ctx.send(f"You don't have the mana to travel! The travel has been queued for <t:{enoughmanatime}>.", ephemeral = True)
    else:
        manamoji = await manamojiconv(Mana_pull- cost)
        travelemb = interactions.api.models.message.Embed(
            title = f"You travel!",
            color = 0xad7205,
            fields = [interactions.EmbedField(name="Mana Remaining",value=manamoji,inline=True)],
        )
        await ctx.send(embeds=travelemb,ephemeral = True)
        await dotravel(ctx.author.id,destination)

traveltotavernbutton = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="Travel to Tavern!",
    custom_id="traveltotavernbutton",
)

@bot.component("traveltotavernbutton")
async def button_response(ctx):
    players = await getplayerdata()
    current_time = int(time.time())
    destination = "Tavern"
    channelid=ctx.channel_id
    cost = 1
    Mana_pull = players[str(ctx.author.id)]["Mana"]
    if cost-Mana_pull > 0:
        enoughmanatime = (players[str(ctx.author.id)]["NextMana"])+(max((cost-Mana_pull-1),0))*basecd
        players[str(ctx.author.id)]["ReadyDate"] = (players[str(ctx.author.id)]["NextMana"])+(max((cost-Mana_pull-1),0))*basecd
        with open("players.json", "w") as f:
            json.dump(players, f, indent=4)
        await queuenexttarget("travel",ctx,destination)
        await ctx.send(f"You don't have the mana to travel! The travel has been queued for <t:{enoughmanatime}>.", ephemeral = True)
    else:
        manamoji = await manamojiconv(Mana_pull- cost)
        travelemb = interactions.api.models.message.Embed(
            title = f"You travel!",
            color = 0xad7205,
            fields = [interactions.EmbedField(name="Mana Remaining",value=manamoji,inline=True)],
        )
        await ctx.send(embeds=travelemb,ephemeral = True)
        await dotravel(ctx.author.id,destination)

#recruit

async def dorecruit(authorid, targetid):
    print("recruit")
    await rage(authorid)
    players = await getplayerdata()
    players[str(authorid)]["Nextaction"] = ""
    current_time = int(time.time())
    print(f"{targetid} is the player target")
    recruitimg = interactions.EmbedImageStruct(
                        url="https://thumbs.gfycat.com/ArtisticGrippingAbyssiniancat-max-1mb.gif",
                        height = 512,
                        width = 512,
                        )
    oldteam = ""
    newteam = ""
        #targetself
    if targetid == authorid:
        print("case1")
        if "Team" in players[str(authorid)] :
            print("case1.1")
            #targetself leave team
            if players[str(authorid)]["Team"] != "No Team":
                print("case1.1.1")
                oldteam = players[str(authorid)]["Team"]
                newteam = "No Team"
                recruitemb = interactions.api.models.message.Embed(
                    title = f"{players[str(authorid)]['Username']} considers leaving their team!",
                    color = 0x2da66c,
                    description = f"Do you want to leave {oldteam} in the dust?",
                    image = recruitimg,
                    fields = [interactions.EmbedField(name="Old Team",value=oldteam,inline=True),interactions.EmbedField(name="New Team",value=newteam,inline=True)],
                    )
                row = interactions.spread_to_rows(leaveteambutton, stayteambutton, futureteamrosterbutton, currentteamrosterbutton)
                try:
                    user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
                    await user.send(embeds=recruitemb, components = row)
                except:
                    print(f"{authorid} not valid user to DM")
            #create new team
            else :
                print("case1.1.2")
                oldteam = "No Team"
                newteam = str(players[str(authorid)]["Username"])+"'s team"
                recruitemb = interactions.api.models.message.Embed(
                    title = f"{players[str(authorid)]['Username']} considers creating a new team team!",
                    color = 0x2da66c,
                    description = f"Press join team below to spend a mana to create the team **{newteam}**",
                    image = recruitimg,
                    fields = [interactions.EmbedField(name="Old Team",value=oldteam,inline=True), interactions.EmbedField(name="New Team",value=newteam,inline=True)],
                    )
                row = interactions.spread_to_rows(jointeambutton, stayteambutton, futureteamrosterbutton, currentteamrosterbutton)
                try:
                    user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
                    await user.send(embeds=recruitemb, components=row)
                except:
                    print(f"{authorid} not valid user to DM")
                players[str(targetid)]["NewTeam"] = newteam
                with open("players.json", "w") as f:
                    json.dump(players, f, indent=4)
        #create new team
        else:
            print("case1.2")
            oldteam = "No Team"
            newteam = str(players[str(authorid)]["Username"])+"'s team"
            recruitemb = interactions.api.models.message.Embed(
                title = f"{players[str(authorid)]['Username']} considers creating a new team team!",
                color = 0x2da66c,
                description = f"Press join team below to spend a mana to create the team **{newteam}**",
                image = recruitimg,
                fields = [interactions.EmbedField(name="Old Team",value=oldteam,inline=True),interactions.EmbedField(name="New Team",value=newteam,inline=True)],
                )
            row = interactions.spread_to_rows(jointeambutton, stayteambutton, futureteamrosterbutton, currentteamrosterbutton)
            try:
                user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
                await user.send(embeds=recruitemb, components = row)
            except:
                print(f"{authorid} not valid user to DM")
    #target not self
    else:
        print("case2")
        #check if author has a team key
        if "Team" in players[str(authorid)]:
            print("case2.1")
            #check if author has team
            if players[str(authorid)]["Team"]!= "No Team" :
                print("case2.1.1")
                #offer to recruit target to author's existing team
                if "Team" in players[str(targetid)]:
                    print("case2.1.1.1")
                    newteam = players[str(authorid)]["Team"]
                    oldteam = players[str(targetid)]["Team"]
                else:
                    print("case2.1.1.2")
                    oldteam = "No Team"
                    newteam = players[str(authorid)]["Team"]
                recruitemb = interactions.api.models.message.Embed(
                    title = f"{players[str(authorid)]['Username']} wants to recruit you to {newteam}!",
                    color = 0x2da66c,
                    description = f"Do you want to spend a mana to accept their offer and join {newteam}?",
                    image = recruitimg,
                    fields = [interactions.EmbedField(name="Target Old Team",value=oldteam,inline=True),interactions.EmbedField(name="Target New Team",value=newteam,inline=True)],
                    )
                row = interactions.spread_to_rows(jointeambutton, stayteambutton, futureteamrosterbutton, currentteamrosterbutton)
                try:
                    user = await interactions.get(bot, interactions.Member, object_id=targetid, guild_id=guildid, force='http')
                    await user.send(embeds=recruitemb, components = row)
                except:
                    print(f"{targetid} not valid user to DM")
                recruitemb2 = interactions.api.models.message.Embed(
                    title = f"An offer has been sent to {players[str(targetid)]['Username']}!",
                    color = 0x2da66c,
                    description = f"You must wait for their reply.",
                    image = recruitimg,
                    fields = [interactions.EmbedField(name="Old Team",value=oldteam,inline=True),interactions.EmbedField(name="New Team",value=newteam,inline=True)],
                    )
                row = interactions.spread_to_rows(jointeambutton, stayteambutton, futureteamrosterbutton, currentteamrosterbutton)
                try:
                    user = await interactions.get(bot, interactions.Member, object_id=targetid, guild_id=guildid, force='http')
                    await user.send(embeds=recruitemb, components = row)
                except:
                    print(f"{targetid} not valid user to DM")
                try:
                    user2 = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
                    await user2.send(embeds=recruitemb2)
                except:
                    print(f"{authorid} not valid user to DM")
                players[str(targetid)]["NewTeam"] = newteam
                with open("players.json", "w") as f:
                    json.dump(players, f, indent=4)
            #if author doesn't have a team offer to create
            else:
                print("case2.1.2")
                oldteam = "No Team"
                newteam = str(players[str(authorid)]["Username"])+"'s team"
                players[str(authorid)]["NewTeam"] = newteam
                recruitemb = interactions.api.models.message.Embed(
                    title = f"{players[str(authorid)]['Username']} doesn't have a team!",
                    color = 0x2da66c,
                    description = f"Press join team below to spend a mana to create the team **{newteam}** before recruiting!",
                    image = recruitimg,
                    fields = [interactions.EmbedField(name="Old Team",value=oldteam,inline=True),interactions.EmbedField(name="New Team",value=newteam,inline=True)],
                    )
                row = interactions.spread_to_rows(jointeambutton, stayteambutton, futureteamrosterbutton, currentteamrosterbutton)
                try:
                    user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
                    await user.send(embeds=recruitemb, components = row)
                except:
                    print(f"{authorid} not valid user to DM")
                players[str(authorid)]["NewTeam"] = newteam
                with open("players.json", "w") as f:
                    json.dump(players, f, indent=4)
        #if author doesn't have a team key offer to create
        else:
            print("case2.2")
            oldteam = "No Team"
            newteam = str(players[str(authorid)]["Username"])+"'s team"
            recruitemb = interactions.api.models.message.Embed(
                title = f"{players[str(authorid)]['Username']} doesn't have a team!",
                color = 0x2da66c,
                description = f"Press join team below to spend a mana to create the team **{newteam}** before recruiting!",
                image = recruitimg,
                fields = [interactions.EmbedField(name="Old Team",value=oldteam,inline=True),interactions.EmbedField(name="New Team",value=newteam,inline=True)],
                )
            row = interactions.spread_to_rows(jointeambutton, stayteambutton, futureteamrosterbutton, currentteamrosterbutton)
            try:
                user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
                await user.send(embeds = recruitemb, components = row)
            except:
                print(f"{authorid} not valid user to DM")
            players[str(authorid)]["NewTeam"] = newteam
            with open("players.json", "w") as f:
                json.dump(players, f, indent=4)

@bot.command(
    name="recruit",
    description="self target to create a team or to leave a team. other targets join your team if they accept.",
    scope = guildid,
    options=[
        interactions.Option(
            type=interactions.OptionType.STRING,
            name="playertarget",
            description="start typing who you want to team up with",
            required=True,
            autocomplete=True,
        )
    ]
)
async def recruit(ctx: interactions.CommandContext, playertarget: str):
    players = await getplayerdata()
    current_time = int(time.time())
    channelid=ctx.channel_id
    for k,v in players.items():
        if v['Username']==str(playertarget):
            targetid=k
    print(f"{targetid} is the player target id")
    if str(ctx.author.id) in players:
        manamoji = await manamojiconv(players[str(ctx.author.id)]['Mana'])
        manaemb = interactions.api.models.message.Embed(
            title = f"You attempt to recruit {players[str(targetid)]['Username']}!",
            color = 0x2da66c,
            fields = [interactions.EmbedField(name="Mana Remaining",value=manamoji,inline=True)],
        )
        await ctx.send(embeds=manaemb,ephemeral = True)
        await dorecruit(ctx.author.id,targetid)
    else:
        await ctx.send(f"You aren't in the competition!" , ephemeral = True)

@bot.autocomplete("recruit", "playertarget")
async def recruit_autocomplete(ctx: interactions.CommandContext, value: str = ""):
    players = await getplayerdata()
    Usernames = [v["Username"] for v in players.values() if v['Location'] != "Dead"]
    print (Usernames)
    items = Usernames
    choices = [
        interactions.Choice(name=item, value=item) for item in items if value.lower() in item.lower()
    ]
    await ctx.populate(choices)

@bot.command(
    name="bounty",
    description="increase the bounty reward for killing a player with an attack or interrupt by one.",
    scope = guildid,
    options=[
        interactions.Option(
            type=interactions.OptionType.STRING,
            name="playertarget",
            description="start typing who you want to increase the bounty on",
            required=True,
            autocomplete=True,
        )
    ]
)
async def bounty(ctx: interactions.CommandContext, playertarget: str):
    players = await getplayerdata()
    current_time = int(time.time())
    channelid=ctx.channel_id
    bountychannel = 1046825086939840624
    channel = await interactions.get(bot, interactions.Channel, object_id=bountychannel , force='http')
    authorid = ctx.author.id
    for k,v in players.items():
        if v['Username']==str(playertarget):
            targetid=k
    print(f"{targetid} is the player target id")
    if str(ctx.author.id) in players:
        if players[str(authorid)]['SC'] >= 1:
            players[str(authorid)]['SC'] = players[str(authorid)]['SC'] -1
            insult1 = ['artless', 'bawdy', 'beslubbering', 'bootless', 'churlish', 'cockered', 'clouted', 'craven', 'currish', 'dankish', 'dissembling', 'droning', 'errant', 'fawning', 'fobbing', 'forward', 'frothy', 'gleeking', 'goatinsh,', 'goating', 'gorbellied', 'impertinent', 'infections', 'jarring', 'loggerheaded', ' lumpish', 'mammering', 'mangled']
            insult2 = ['base-court', 'bat-fowling', 'beef-witted', 'beetle-headed', 'boild-brained', 'clapper-clawed','clay-brained', 'common-kissing', 'crook-pated', 'dismal-dreaming', 'dizzy-eyed', 'doghearted', 'dread-bolted', 'earth-vexing', 'elf-skinned', 'fat-kidneyed', 'fen-sucked', 'flap-mouthed', 'fly-bitten', 'folly-fallen', 'fool-born', 'full-gorged', 'guts-griping', 'half-faced', 'hasty-witted', 'hedge-born', 'hell-hated']
            insult3 = ['apple-john', 'baggage', 'barnacle', 'bladder', 'boar-pig', 'bugbear', 'bum-bailey', 'canker-blossom', 'clack-dish', 'clotpole', 'coxcomb', 'codpiece', 'death-token', 'dewberry', 'flap-dragon', 'flax-wench', 'flirt-gill', 'foot-licker', 'fustilarian', 'giglet', 'gudgeon', 'haggard', 'harpy', 'hedge-pig', 'horn-beast', 'hugger-mugger', 'jointhead']
            my_insult = random.choice(insult1) + ' ' + random.choice(insult2) + ' ' + random.choice(insult3)
            players[str(targetid)]['BountyReward'] = players[str(targetid)]['BountyReward'] + 1
            bountyemb = interactions.api.models.message.Embed(
                title = f"{players[str(authorid)]['Username']} increased the bounty on {players[str(targetid)]['Username']}!",
                color = 0x2da66c,
                description = f"<@{targetid}>, you {my_insult}!",
                fields = [interactions.EmbedField(name="New Bounty",value=players[str(targetid)]['BountyReward'],inline=True),interactions.EmbedField(name="SC Remaining",value=players[str(authorid)]['SC'],inline=True)],
            )
            await ctx.send (embeds=bountyemb,ephemeral = True)
            bountyemb = interactions.api.models.message.Embed(
                title = f"{players[str(authorid)]['Username']} increased the bounty on {players[str(targetid)]['Username']}!",
                color = 0x2da66c,
                description = f"<@{targetid}>, you {my_insult}!",
                fields = [interactions.EmbedField(name="New Bounty",value=players[str(targetid)]['BountyReward'],inline=True)],
            )
            await channel.send(embeds=bountyemb)
            with open("players.json", "w") as f:
                json.dump(players, f, indent=4)
        else:
            bountyemb = interactions.api.models.message.Embed(
                title = f"{players[str(authorid)]['Username']} tried, but failed to increase the bounty on {players[str(targetid)]['Username']}!",
                color = 0x2da66c,
                description = "They are too poor to increase a bounty! ||HAHAHAHAHAAHAHAHA||",
                fields = [interactions.EmbedField(name="New Bounty",value=players[str(targetid)]['BountyReward'],inline=True),interactions.EmbedField(name="SC Remaining",value=players[str(authorid)]['SC'],inline=True)],
            )
            await ctx.send (embeds=bountyemb,ephemeral = True)
            bountyemb = interactions.api.models.message.Embed(
                title = f"{players[str(authorid)]['Username']} tried, but failed to increase the bounty on {players[str(targetid)]['Username']}!",
                color = 0x2da66c,
                description = "They are too poor to increase a bounty! ||HAHAHAHAHAAHAHAHA||",
                fields = [interactions.EmbedField(name="New Bounty",value=players[str(targetid)]['BountyReward'],inline=True)],
            )
            await channel.send(embeds=bountyemb)
    else:
        await ctx.send(f"You aren't in the competition!" , ephemeral = False)

@bot.autocomplete("bounty", "playertarget")
async def bounty_autocomplete(ctx: interactions.CommandContext, value: str = ""):
    players = await getplayerdata()
    Usernames = [v["Username"] for v in players.values() if v['Location'] != "Dead"]
    print (Usernames)
    items = Usernames
    choices = [
        interactions.Choice(name=item, value=item) for item in items if value.lower() in item.lower()
    ]
    await ctx.populate(choices)

jointeambutton = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="Join New Team!",
    custom_id="jointeambutton",
)

@bot.component("jointeambutton")
async def button_response(ctx):
    players = await getplayerdata()
    newteam = players[str(ctx.user.id)]["NewTeam"]
    recruitimg = interactions.EmbedImageStruct(
                        url="https://thumbs.gfycat.com/ArtisticGrippingAbyssiniancat-max-1mb.gif",
                        height = 512,
                        width = 512,
                        )
    if players[str(ctx.user.id)]["Team"] == "No Team":
        players[str(ctx.user.id)]["Mana"] = max(players[str(ctx.user.id)]["Mana"],0)
    else:
        players[str(ctx.user.id)]["Mana"] = max(players[str(ctx.user.id)]["Mana"]-1,0)
    manamoji = await manamojiconv(players[str(ctx.user.id)]['Mana'])
    recruitemb = interactions.api.models.message.Embed(
        title = f"{players[str(ctx.user.id)]['Username']} joined {newteam}!",
        color = 0x2da66c,
        description = f"{players[str(ctx.user.id)]['Username']} joined **{newteam}**!",
        image = recruitimg,
        fields = [interactions.EmbedField(name="New Team",value=newteam,inline=True)],
        )
    players[str(ctx.user.id)]["Team"] = newteam
    players[str(ctx.user.id)]["NewTeam"] = "No Team"
    players[str(ctx.user.id)]["Lastaction"] = "recruit"
    with open("players.json", "w") as f:
        json.dump(players, f, indent=4)
    locchannel=str(locations[players[str(ctx.user.id)]["Location"]]["Channel_ID"])
    channel = await interactions.get(bot, interactions.Channel, object_id=locchannel , force='http')
    await channel.send(embeds = recruitemb)
    await ctx.send(embeds = recruitemb)

leaveteambutton = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="Leave your team!",
    custom_id="leaveteambutton",
)

@bot.component("leaveteambutton")
async def button_response(ctx: interactions.CommandContext):
    players = await getplayerdata()
    recruitimg = interactions.EmbedImageStruct(
                        url="https://thumbs.gfycat.com/ArtisticGrippingAbyssiniancat-max-1mb.gif",
                        height = 512,
                        width = 512,
                        )
    newteam = players[str(ctx.user.id)]["NewTeam"]
    if players[str(ctx.user.id)]["Mana"] <1:
        manamoji = await manamojiconv(players[str(ctx.user.id)]['Mana'])
        recruitemb = interactions.api.models.message.Embed(
            title = f"{players[str(ctx.user.id)]['Username']} not enough mana to leave team!",
            color = 0x2da66c,
            description = f"You need a mana to leave your team!",
            image = recruitimg,
            fields = [interactions.EmbedField(name="New Team",value=newteam,inline=True),interactions.EmbedField(name="Mana",value=manamoji,inline=True)],
            )
        await ctx.send(embeds = recruitemb)
    else :
        players[str(ctx.user.id)]["Mana"] = max(players[str(ctx.user.id)]["Mana"] - 1,0)
        players[str(ctx.user.id)]["Team"] = "No Team"
        players[str(ctx.user.id)]["Lastaction"] = "recruit"
        with open("players.json", "w") as f:
            json.dump(players, f, indent=4)
        manamoji = await manamojiconv(players[str(ctx.user.id)]['Mana'])
        recruitemb = interactions.api.models.message.Embed(
            title = f"{players[str(ctx.user.id)]['Username']} left their team!",
            color = 0x2da66c,
            description = f"{players[str(ctx.user.id)]['Username']} spent a mana to leave their team!",
            image = recruitimg,
            fields = [interactions.EmbedField(name="New Team",value=newteam,inline=True)],
            )
        locchannel=str(locations[players[str(ctx.user.id)]["Location"]]["Channel_ID"])
        channel = await interactions.get(bot, interactions.Channel, object_id=locchannel , force='http')
        await channel.send(embeds = recruitemb)
        await ctx.send(embeds = recruitemb)

stayteambutton = interactions.Button(
    style=interactions.ButtonStyle.DANGER,
    label="Stay with current team!",
    custom_id="stayteambutton",
)

@bot.component("stayteambutton")
async def button_response(ctx: interactions.CommandContext):
    players = await getplayerdata()
    recruitimg = interactions.EmbedImageStruct(
                        url="https://thumbs.gfycat.com/ArtisticGrippingAbyssiniancat-max-1mb.gif",
                        height = 512,
                        width = 512,
                        )
    await ctx.send(f"You do not leave your team!", ephemeral=True)

moreinfobutton = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="More Info",
    custom_id="moreinfobutton",
)

@bot.component("moreinfobutton")
async def button_response(ctx: interactions.CommandContext):
    players = await getplayerdata()
    buttonemb = interactions.api.models.message.Embed(
        title = f"More Info",
        color = 0x2da66c,
        description = f"What would you like more info on?",
        )
    row = interactions.spread_to_rows(currentteamrosterbutton, allteamsbutton, allplayerbutton, deadplayersbutton, afkplayerbutton, activeplayerbutton)
    await ctx.send(embeds=buttonemb, components = row, ephemeral=True)

queuecancel = interactions.Button(
    style=interactions.ButtonStyle.DANGER,
    label="Clear Queue",
    custom_id="queuecancel",
)

@bot.component("queuecancel")
async def button_response(ctx: interactions.CommandContext):
    players = await getplayerdata()
    buttonemb = interactions.api.models.message.Embed(
        title = f"Queue Cancelled",
        color = 0x2da66c,
        description = f"Your queue has been cleared",
        )
    players[str(ctx.author.id)]["Nextaction"] = ""
    with open("players.json", "w") as f:
        json.dump(players, f, indent=4)
    await ctx.send(embeds=buttonemb, ephemeral=True)

orderoptout = interactions.Button(
    style=interactions.ButtonStyle.DANGER,
    label="Opt in/out of being Ordered",
    custom_id="orderoptout",
)
@bot.component("orderoptout")
async def button_response(ctx: interactions.CommandContext):
    players = await getplayerdata()
    if players[str(ctx.author.id)]["OptOutOrder"] == "Yes":
        players[str(ctx.author.id)]["OptOutOrder"] = "No"
        description = "opted in to"
    elif players[str(ctx.author.id)]["OptOutOrder"] == "No" or players[str(ctx.author.id)]["OptOutOrder"] == "":
        players[str(ctx.author.id)]["OptOutOrder"] = "Yes"
        players[str(ctx.author.id)]["Orders"] = ""
        description = "opted out of"
    buttonemb = interactions.api.models.message.Embed(
        title = f"You {description} being ordered",
        color = 0x2da66c,
        description = f"You have {description} being ordered!",
        )
    with open("players.json", "w") as f:
        json.dump(players, f, indent=4)
    await ctx.send(embeds=buttonemb, ephemeral=True)

currentteamrosterbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Current Team Roster",
    custom_id="currentteamrosterbutton",
)

@bot.component("currentteamrosterbutton")
async def button_response(ctx: interactions.CommandContext):
    players = await getplayerdata()
    teamhp = 0
    teamcount = 0
    teammana = 0
    teaminventory = " "
    if players[str(ctx.user.id)]["Team"] == "No Team":
        teampull = "You aren't on a team"
        teamcount = 1
    else:
        teampull = players[str(ctx.user.id)]["Team"]
    for v in players.values():
        if v['Team']== teampull and v['Location'] != 'Dead':
            teamhp = int(v["HP"]) + teamhp
            teamcount = teamcount+1
    #hpmoji
    numofgreensqs = math.floor(teamhp/(teamcount*1000))
    numofredsqs = math.floor(((teamcount*10000)-teamhp)/(teamcount*1000))
    yellowsq = math.ceil((teamhp-(numofgreensqs*(teamcount*1000)))/(teamcount*1000))
    teammojihp = str(numofgreensqs*":green_square:")+(yellowsq*":yellow_square:")+str(numofredsqs*":red_square:")+f"({teamhp:,}/{(teamcount*10000):,})"
    for v in players.values():
        if v['Team']== teampull and v['Location'] != 'Dead':
            teaminventory = "**"+v["Username"]+"**"+ v["ReadyInventory"]+"\n\n" + teaminventory
    sameTeamUsernames = [str(v["Mana"]*":blue_square:")+str((3-v["Mana"])*":purple_square:")+str(math.floor(v["HP"]/2500)*":green_square:")+str(math.ceil((10000-(max(v["HP"],0)))/2500)*":red_square:")+" - "+(str(v["Username"])+" - "+str(v["Location"])) for v in players.values() if v['Team'] == teampull and v['Location'] != 'Dead']
    if len(sameTeamUsernames) == 0:
        sameTeamUsernames = "No players are on your current team"
        teammojihp = await hpmojiconv(players[str(ctx.user.id)]["HP"])
        teaminventory = players[str(ctx.user.id)]["ReadyInventory"]
    elif len(str(sameTeamUsernames)) > 1000:
        sameTeamUsernames = '\n'.join(sameTeamUsernames)
        sameTeamUsernames = sameTeamUsernames[:900]+ "\n...too many players to display!"
    else:
        sameTeamUsernames = '\n'.join(sameTeamUsernames)
    buttonemb = interactions.api.models.message.Embed(
        title = f"{teampull}",
        color = 0x2da66c,
        #fields = [interactions.EmbedField(name="Team HP",value=teamhp,inline=True),interactions.EmbedField(name="Team Mana",value=teammana,inline=True)],
        fields = [interactions.EmbedField(name="Total Team Health",value=teammojihp,inline=False),interactions.EmbedField(name="Mana - Players - Locations",value=sameTeamUsernames,inline=False),interactions.EmbedField(name="Team Ready Inventory",value=teaminventory,inline=False),],
        )
    await ctx.send(embeds=buttonemb, ephemeral=True)

allplayerbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Living Player Locations",
    custom_id="allplayerbutton",
)

@bot.component("allplayerbutton")
async def button_response(ctx: interactions.CommandContext):
    players = await getplayerdata()
    #teamhp = #X
    #teamhp = await hpmojiconv(teamhp)
    #teammana = #X
    #teammana = await manamojiconv(teammana)
    crossUsernames = [(str(v["Username"])) for v in players.values() if v['Location'] == 'Crossroads']
    dungeonUsernames = [(str(v["Username"])) for v in players.values() if v['Location'] == 'Dungeon']
    keepUsernames = [(str(v["Username"])) for v in players.values() if v['Location'] == 'Keep']
    farmUsernames = [(str(v["Username"])) for v in players.values() if v['Location'] == 'Farmland']
    lichUsernames = [(str(v["Username"])) for v in players.values() if v['Location'] == "Lich's Castle"]
    shopUsernames = [(str(v["Username"])) for v in players.values() if v['Location'] == "Shop"]
    tavernUsernames = [(str(v["Username"])) for v in players.values() if v['Location'] == "Tavern"]

    crossUsernames = '\n'.join(crossUsernames)
    dungeonUsernames = '\n'.join(dungeonUsernames)
    keepUsernames = '\n'.join(keepUsernames)
    farmUsernames = '\n'.join(farmUsernames)
    lichUsernames = '\n'.join(lichUsernames)
    shopUsernames = '\n'.join(shopUsernames)
    tavernUsernames = '\n'.join(tavernUsernames)

    await Paginator(
        client=bot,
        ctx=ctx,
        timeout = 300,
        remove_after_timeout = True,
        hidden = True,
        pages=[
            Page("Crossroads",interactions.api.models.message.Embed(title="Living Players (Crossroads)", description=f"{crossUsernames}",ephemeral=True)),
            Page("Dungeon",interactions.api.models.message.Embed(title="Living Players (Dungeon)", description=f"{dungeonUsernames}",ephemeral=True)),
            Page("Farmland",interactions.api.models.message.Embed(title="Living Players (Farmland)", description=f"{farmUsernames}",ephemeral=True)),
            Page("Keep",interactions.api.models.message.Embed(title="Living Players (Keep)", description=f"{keepUsernames}",ephemeral=True)),
            Page("Lich's Castle",interactions.api.models.message.Embed(title="Living Players (Lich's Castle)", description=f"{lichUsernames}",ephemeral=True)),
            Page("Shop",interactions.api.models.message.Embed(title="Living Players (Shop)", description=f"{shopUsernames}",ephemeral=True)),
            Page("Tavern",interactions.api.models.message.Embed(title="Living Players (Tavern)", description=f"{tavernUsernames}",ephemeral=True)),
        ],
    ).run()

afkplayerbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="AFK Player Names",
    custom_id="afkplayerbutton",
)

@bot.component("afkplayerbutton")
async def button_response(ctx: interactions.CommandContext):
    players = await getplayerdata()
    #teamhp = #X
    #teamhp = await hpmojiconv(teamhp)
    #teammana = #X
    #teammana = await manamojiconv(teammana)
    afkUsernames = [(str(v["Username"])) for v in players.values() if v['Lastaction'] == 'start' and v['Location'] != 'Dead']
    afkUsernames = '\n'.join(afkUsernames)
    afkUsernamesDead = [(str(v["Username"])) for v in players.values() if v['Lastaction'] == 'start' and v['Location'] == 'Dead']
    afkUsernamesDead = '\n'.join(afkUsernamesDead)

    await Paginator(
        client=bot,
        ctx=ctx,
        timeout = 300,
        remove_after_timeout = True,
        pages=[
            Page("AFK Living",interactions.api.models.message.Embed(title="Living Players (AFK)", description=f"{afkUsernames}",ephemeral=True)),
            Page("AFK Dead",interactions.api.models.message.Embed(title="Dead Players (AFK)", description=f"{afkUsernamesDead}",ephemeral=True)),
        ],
    ).run()


activeplayerbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Active Player Names",
    custom_id="activeplayerbutton",
)

@bot.component("activeplayerbutton")
async def button_response(ctx: interactions.CommandContext):
    players = await getplayerdata()
    #teamhp = #X
    #teamhp = await hpmojiconv(teamhp)
    #teammana = #X
    #teammana = await manamojiconv(teammana)
    activeUsernames = [(str(v["Username"]))+" - "+(str(v["Location"])) for v in players.values() if v['Lastaction'] != 'start' and v['Location'] != 'Dead']
    activeUsernames = '\n'.join(activeUsernames)
    activeUsernamesDead = [(str(v["Username"])) for v in players.values() if v['Lastaction'] != 'start' and v['Location'] == 'Dead']
    activeUsernamesDead = '\n'.join(activeUsernamesDead)

    await Paginator(
        client=bot,
        ctx=ctx,
        timeout = 300,
        remove_after_timeout = True,
        pages=[
            Page("Active Living",interactions.api.models.message.Embed(title="Living Players who have taken an action (Active)", description=f"{activeUsernames}",ephemeral=True)),
            Page("Active Dead",interactions.api.models.message.Embed(title="Dead Players who have taken an action (Active)", description=f"{activeUsernamesDead}",ephemeral=True)),
        ],
    ).run()

allteamsbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="All Team Rosters",
    custom_id="allteamsbutton",
)

@bot.component("allteamsbutton")
async def button_response(ctx: interactions.CommandContext):
    players = await getplayerdata()
    #teamhp = #X
    #teamhp = await hpmojiconv(teamhp)
    #teammana = #X
    #teammana = await manamojiconv(teammana)
    TeamNames = []
    for v in players.values():
        if v['Team'] not in TeamNames and v['Team'] != 'No Team':
            TeamNames.append((str(v["Team"])))
        elif v['Team'] not in TeamNames:
            TeamNames.append((str(v["Team"])))
    pagesprep =[]
    for item in TeamNames:
        teamusers =[]
        for value in players.values():
            if item == value['Team'] and value['Location']!='Dead':
                teamusers.append((str(value["Username"]+" - "+value["Location"])))
        teamusersspace = '\n'.join(teamusers)
        pagesprep.append(Page(f"{item}",interactions.api.models.message.Embed(title=f"{item}", description=f"{teamusersspace}",ephemeral=True)))
    await Paginator(
        client=bot,
        ctx=ctx,
        timeout = 300,
        remove_after_timeout = True,
        pages=pagesprep,
    ).run()

futureteamrosterbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Proposed Team Roster",
    custom_id="futureteamrosterbutton",
)

@bot.component("futureteamrosterbutton")
async def button_response(ctx: interactions.CommandContext):
    players = await getplayerdata()
    #teamhp = #X
    #teamhp = await hpmojiconv(teamhp)
    #teammana = #X
    #teammana = await manamojiconv(teammana)
    if players[str(ctx.user.id)]["NewTeam"] == "No Team":
        teampull = "You have no possible team to join!"
    else:
        teampull = players[str(ctx.user.id)]["NewTeam"]
    sameTeamUsernames = [(str(v["Username"])+" - "+str(v["Location"])) for v in players.values() if v['Team'] == teampull and v['Location'] != 'Dead']
    if len(sameTeamUsernames) == 0:
        sameTeamUsernames = "No players are on that team"
    elif len(str(sameTeamUsernames)) > 1000:
        sameTeamUsernames = '\n'.join(sameTeamUsernames)
        sameTeamUsernames = sameTeamUsernames[:900]+ "\n...too many players to display!"
    else:
        sameTeamUsernames = '\n'.join(sameTeamUsernames)
    buttonemb = interactions.api.models.message.Embed(
        title = f"{teampull}",
        color = 0x2da66c,
        #fields = [interactions.EmbedField(name="Team HP",value=teamhp,inline=True),interactions.EmbedField(name="Team Mana",value=teammana,inline=True)],
        fields = [interactions.EmbedField(name="Players - Locations",value=sameTeamUsernames,inline=True)],
        )
    await ctx.send(embeds=buttonemb, ephemeral=True)

deadplayersbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Dead Players",
    custom_id="deadplayersbutton",
)

@bot.component("deadplayersbutton")
async def button_response(ctx: interactions.CommandContext):
    players = await getplayerdata()
    #teamhp = #X
    #teamhp = await hpmojiconv(teamhp)
    #teammana = #X
    #teammana = await manamojiconv(teammana)
    deadusernames = [v["Username"] for v in players.values() if v['Location'] == "Dead"]
    if len(deadusernames) == 0:
        deadusernames = "No players have died"
    elif len(str(deadusernames)) > 1000:
        deadusernames = '\n'.join(deadusernames)
        deadusernames = deadusernames[:900]+ "\n...too many players to display!"
    else:
        deadusernames = '\n'.join(deadusernames)
    buttonemb = interactions.api.models.message.Embed(
        color = 0x2da66c,
        #fields = [interactions.EmbedField(name="Team HP",value=teamhp,inline=True),interactions.EmbedField(name="Team Mana",value=teammana,inline=True)],
        fields = [interactions.EmbedField(name="Dead Players",value=deadusernames,inline=True)],
        )
    await ctx.send(embeds=buttonemb, ephemeral=True)

functiondict = {'lightattack' : dolightattack,
                'heavyattack' : doheavyattack,
                'interrupt' : dointerrupt,
                'evade' : doevade,
                'rest' : dorest,
                'farm' : dofarm,
                'travel' : dotravel,
                'aid': doaid,
                'exchange': doexchange,
                'trade': doexchange,
                'drink': dodrink,
                'battlelich': dobattlelich,
                'lichitem': dolichitem,
                'drinkingmedal': dodrinkingmedal,
                'tractor':dotractor,
                'beerbando':dobeerbando,
                'AWP':doAWP,
                'crookedabacus':docrookedabacus,
                'loot':doloot,
                'adventuringgear':doadventuringgear,
                'goodiebag':dogoodiebag,
                'critterihardlyknowher':docritterihardlyknowher,
                'localligmaoutbreak':dolocalligmaoutbreak,
                'trade':dotrade,
                'use' : douse}

bot.start ()

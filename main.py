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
    membersdictfind = r"(\d+):\s*id=\d+\s*,\s*username='(.*?)'\s*,.*?,\s*bot=(\w+),"
    membersdict = re.findall(membersdictfind, membersdict)
    membersdict = dict([(a, (b, c)) for a, b, c in membersdict])
    membersdict = {k: {'Username': v[0], 'Mana': 3, 'HP': 10000, 'Location': "Crossroads", 'SC': 10, 'Rage': 0, 'InitManaDate': current_time + basecd,'NextMana': current_time + basecd,'ReadyInventory': "\n        goodiebag",'EquippedInventory': ' ','ReadyDate': current_time,'Lastactiontime': current_time, 'Lastaction':"start",'Nextaction':"" } for k, v in membersdict.items() if v[1] != 'True'}
    players = await getplayerdata()
    bounty = await getbountydata()
    print(bounty)
    print(membersdict)
    for key in bounty.keys():
      if key in membersdict.keys():
        membersdict[key]['SC']+=bounty[key]['SC']
    newplayers = membersdict | players
    with open("players.json","w") as f:
        json.dump(newplayers,f, indent=4)
    for key in newplayers.keys():
        if key not in players.keys():
            user = await interactions.get(bot, interactions.Member, object_id=key, guild_id=guildid, force='http')
            await user.add_role(locations["Crossroads"]["Role_ID"], guildid)
            await user.add_role(locations["Playing"]["Role_ID"], guildid)
    loop = asyncio.get_running_loop()
    loop.create_task(pollfornext())
    loop.create_task(pollformanagain())
    loop.create_task(pollformana())
    loop.create_task(pollforqueue())
    print(f"Started at {current_time}")
    ligma = await getligmadata()
    channel = await interactions.get(bot, interactions.Channel, object_id=ligmachannel)
    if str("ligmadate") in ligma:
        print(f"ligma date already exists!")
        with open("ligma.json", "r") as h:
            ligmadate_pull = ligma["ligmadate"]
            ligmadamage_pull = ligma["ligmadamage"]
            ligmatimer_pull = ligma["ligmatimer"]
        print (f"ligma date pulled as {ligmadate_pull}, ligma timer pulled as {ligmatimer_pull}, and ligmadamage pulled as {ligmadamage_pull}")
        if ligmadate_pull < current_time :
            ligmatimer_pull=max(math.ceil(ligmatimer_pull*.9),basecd)
            nextligmatime=int(current_time+ligmatimer_pull)
            print(f"{ligmadamage_pull} ligma damage at {nextligmatime} and {ligmatimer_pull} days till next ligma")
            players = await getplayerdata ()
            print ("before")
            print (players)
            players = {key:{key2:value2-ligmadamage_pull if key2=="HP" else value2 for (key2,value2) in value.items()} for (key,value) in players.items()}
            print ("after")
            print (players)
            with open("players.json","w") as f:
                json.dump(players,f, indent=4)
            await channel.send(f"Oh no a Ligma outbreak! ||LIGMA BALLS|| damage increased by 100 then dealt **{ligmadamage_pull} damage** to everyone! \nThe ligma outbreak timer decreases by 10%! \nThe next ligma outbreak occurs at <t:{nextligmatime}> (in {ligmatimer_pull} seconds) to deal {min(ligmadamage_pull +100, 1500)} damage." )
            ligma["ligmadate"] = nextligmatime
            ligma["ligmadamage"] = ligmadamage_pull
            ligma["ligmatimer"] = ligmatimer_pull
            with open("ligma.json","w") as h:
               json.dump(ligma,h, indent=4)
        else:
            print("hi")
            currenttimeofday = (current_time % 86400) -14400 #seconds since midnight - timezone
            print(f"currenttimeofday={currenttimeofday}")
            announcementtime = int((1*60*60*10.5)) #10:30am
            print(f"announcementtime={announcementtime}")
            timeuntilannounce = announcementtime - currenttimeofday
            print(f"timeuntilannounce={timeuntilannounce}")
            if announcementtime < currenttimeofday:
                await asyncio.sleep(int(timeuntilannounce+86400))
            else:
                await asyncio.sleep(int(timeuntilannounce))
            await channel.send(f"The next ligma comes <t:{ligmadate_pull}> ({int(ligmadate_pull-current_time)} seconds) to deal {int(ligmadamage_pull+100)} damage.")
    else:
        smalltime=int(basecd) #set to 86400 (seconds in a day) when golive and blank ligma.json
        smalltimeunit="days" #set to days on golive
        firstcountdown=int(7*smalltime)
        nextligmatime=current_time+firstcountdown
        ligma = {}
        ligma["ligmadate"] = nextligmatime
        ligma["firstligmadate"] = nextligmatime
        ligma["ligmadamage"] = 650
        ligma["ligmatimer"] = firstcountdown
        ligmadamage_pull = ligma["ligmadamage"]
        ligmatimer_pull = firstcountdown
        with open("ligma.json","w") as h:
            json.dump(ligma,h, indent=4)
        ligma = await getligmadata()
        ligmadate_pull = ligma["ligmadate"]
        ligmadamage_pull = ligma["ligmadamage"]
        ligmatimer_pull = ligma["ligmatimer"]
        await channel.send(f"The first ligma damage occurs on <t:{nextligmatime}> (in {ligmatimer_pull} seconds) to deal {min(ligmadamage_pull +100, 1500)} damage." )
    await asyncio.sleep(int(ligmadate_pull-current_time))
    while ligmadamage_pull < 500000:
        ligmadamage_pull= min(ligma["ligmadamage"] +100, 1500)
        ligmatimer_pull=max(math.ceil(ligmatimer_pull*.9),basecd)
        nextligmatime=int(current_time+ligmatimer_pull)
        print(f"{ligmadamage_pull} ligma damage at {nextligmatime} and {ligmatimer_pull} seconds till next ligma")
        await channel.send(f"Ligma damage increased by 100 then dealt **{ligmadamage_pull} damage** to everyone! \nThe time between ligma damage decreases by 10%! \nThe next ligma damage occurs on <t:{nextligmatime}> (in {ligmatimer_pull} seconds) to deal {min(ligmadamage_pull +100, 1500)} damage." )
        players = await getplayerdata ()
        print ("before")
        print (players)
        players = {key:{key2:value2-ligmadamage_pull if key2=="HP" else value2 for (key2,value2) in value.items()} for (key,value) in players.items()}
        print ("after")
        print (players)
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
        ligma["ligmadate"] = nextligmatime
        ligma["ligmadamage"] = ligmadamage_pull
        ligma["ligmatimer"] = ligmatimer_pull
        with open("ligma.json","w") as h:
          json.dump(ligma,h, indent=4)
        await asyncio.sleep(nextligmatime-current_time)



@bot.event(name="on_message_create")
async def listen(message: interactions.Message):
    print(
        f"\nWe've received a message from {message.author.username} in {message.channel_id}. \nThe message is: \n\n{message.content}\n \nend content\n"
    )

async def deadcheck(targethp,targetid,authorid,players):
    print(f"\ndead?:{int(time.time())}")
    EquippedInventory_pull = players[targetid]["EquippedInventory"]
    targetlichprot = EquippedInventory_pull.count("lichitem")
    if targethp <= 0:
        print(f"\n the target died!")
        user = await interactions.get(bot, interactions.Member, object_id=targetid, guild_id=guildid, force='http')
        if targetlichprot > 0:
            players[targetid]["HP"] = 4200
            #replace first instance of item in user's readyinventory
            players[str(targetid)]["EquippedInventory"]=EquippedInventory_pull.replace('\n        lichitem','',1)
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
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
    else:
        print(f"\n the target didn't die!")

#rage heals 420 for each rage stack then decreases by 1
async def rage(authorid):
    rageplayers = await getplayerdata()
    rageplayers[str(authorid)]["HP"] = min(rageplayers[str(authorid)]["HP"] + ((rageplayers[str(authorid)]["Rage"])*420),10000)
    ragehealing = ((rageplayers[str(authorid)]["Rage"])*420)
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
                        loop.create_task(functiondict[words[0]](**{'authorid': k}))
                        print(f"{v['Username']} is doing {words[0]}")
                    elif words[0] == "use":
                        loop.create_task(functiondict[words[1]](**{'authorid': k}))
                        print(f"{v['Username']} is doing {words[0]} {words[1]}")
                    elif words[1] in players:
                        if len(words) == 3:
                            loop.create_task(functiondict[words[0]]( **{'authorid':k,'targetid':words[1],'readyitem':words[2]}))
                            print(f"{v['Username']} is doing {words[0]} {players[words[1]]['Username']} {words[2]}")
                        else:
                            print(f"{v['Username']} is doing {words[0]} {players[words[1]]['Username']}")
                            loop.create_task(functiondict[words[0]]( **{'authorid':k,'targetid':words[1]}))
                    elif words[1] in locations:
                        loop.create_task(functiondict[words[0]]( **{'authorid':k,'destination':words[1]}))
                        print(f"{v['Username']} is doing {words[0]} {words[1]}")
                    elif words[1] in shop:
                        loop.create_task(functiondict[words[0]]( **{'authorid':k,'itemtarget':words[1]}))
                        print(f"{v['Username']} is doing {words[0]} {words[1]}")
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
        await asyncio.sleep(30)

async def pollformanagain():
    #run forever
    while True:
        print(f"\npolling for managain:{int(time.time())}")
        players = await getplayerdata()
        for k,v in players.items():
                if v['NextMana'] < int(time.time()) and v['Location'] != "Dead":
                    #give mana
                    print(f"{v['Username']} is ready to gain a mana! {v['Mana']}/3")
                    v['NextMana'] = v['NextMana'] + basecd
                    v['Mana'] = min(v['Mana']+1,3)
                    with open("players.json","w") as f:
                        json.dump(players,f, indent=4)
        await asyncio.sleep(30)

async def pollformana():
    #run forever
    while True:
        current_time = int(time.time())
        currenttimeofday = (current_time % 86400) -14400 #seconds since midnight - timezone (eastern)
        print(f"currenttimeofday={currenttimeofday}")
        announcementtime = int((1*60*60*10.5)) #10:30am
        print(f"announcementtime={announcementtime}")
        timeuntilannounce = announcementtime - currenttimeofday
        print(f"timeuntilannounce={timeuntilannounce}")
        if announcementtime < currenttimeofday:
            await asyncio.sleep(int(timeuntilannounce+86400))
        else:
            await asyncio.sleep(int(timeuntilannounce))
        print(f"\npolling for mana:{int(time.time())}")
        players = await getplayerdata()
        readyplayers = [k for k, v in players.items() if v['Mana'] > 0 and v['Location'] != "Dead"]
        reminders = await getreminderdata()
        for key in readyplayers:
          if key in reminders:
            print(key)
            await send_message(f"You have mana to spend! \n\nSubmit a slash command here:\nhttps://discord.gg/Ct3uAgujg9", user_id=[key])
        #don't turn this on until the bot is not relaunching often
        await asyncio.sleep(int(1*60*60*24)) #timer


async def pollforqueue():
    #run forever
    while True:
        current_time = int(time.time())
        currenttimeofday = (current_time % 86400) -14400 #seconds since midnight - timezone
        print(f"currenttimeofday={currenttimeofday}")
        announcementtime = int((1*60*60*10.5)) #10:30am
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
        print(noqueueplayers)
        for key in noqueueplayers:
          if key in reminders:
            print(key)
            await send_message(f"You have no queued action! \n\nSubmit a slash command here:\nhttps://discord.gg/Ct3uAgujg9", user_id=[key])
        #don't turn this on until the bot is not relaunching often
        await asyncio.sleep(int(1*60*60*48)) #timer


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

#light attack is below
async def dolightattack(authorid,targetid):
    players = await getplayerdata()
    current_time = int(time.time())
    user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
    location = players[str(authorid)]["Location"]
    channelid = locations[str(location)]["Channel_ID"]
    if players[str(targetid)]["Lastaction"] == "evade" and (players[str(targetid)]["Lastactiontime"]+86400)<current_time:
        await rage(authorid)
        players = await getplayerdata()
        damage = 0
        targethp = players[str(targetid)]["HP"] - damage
        players[str(targetid)]["HP"] = targethp
        players[str(authorid)]["Rage"] = players[str(authorid)]["Rage"] +1
        players[str(authorid)]["Mana"] = players[str(authorid)]["Mana"] -1
        players[str(authorid)]["Lastaction"] = "lightattack"
        hpmoji = await hpmojiconv(targethp)
        with open("players.json", "w") as f:
            json.dump(players, f, indent=4)
        await send_message(f"<@{targetid}> evaded a light attack from <@{authorid}>! \nNew HP: {hpmoji} ", user_id=[authorid,targetid])
        await send_message(f"<@{authorid}> used a light attack on <@{targetid}>! ", channel_id=[channelid])
    else:
        await rage(authorid)
        players = await getplayerdata()
        EquippedInventory_pull = players[str(authorid)]["EquippedInventory"]
        damageroll = random.randint(0, 300)
        critroll = random.randint(0, 10) + (EquippedInventory_pull.count("critterihardlyknowher") * 1)
        critdmg = max(critroll-9,0)*950
        damage = 800 + damageroll + (EquippedInventory_pull.count("drinkingmedal") * 420)+ critdmg
        targethp = players[str(targetid)]["HP"] - damage
        players[str(targetid)]["HP"] = targethp
        await deadcheck(targethp,targetid,authorid,players)
        players[str(authorid)]["Rage"] = players[str(authorid)]["Rage"] +1
        players[str(authorid)]["Mana"] = players[str(authorid)]["Mana"] -1
        players[str(authorid)]["Lastaction"] = "lightattack"
        hpmoji = await hpmojiconv(targethp)
        with open("players.json", "w") as f:
            json.dump(players, f, indent=4)
        if critroll >= 10:
            send_message( f"<@{authorid}> scored a **CRITICAL HIT** on <@{targetid}>!", channel_id=[channelid])
        else:
            print("nocrit")
        await send_message(f"<@{targetid}> was hit by a light attack by <@{authorid}>! \nNew HP: {hpmoji} ", user_id=[authorid,targetid])
        await send_message( f"<@{authorid}> used a light attack on <@{targetid}>! ", channel_id=[channelid])

@bot.command(
    name="lightattack",
    description="1mana.1rage. attack a player in your area for 800 - 1100 damage.",
    scope = guildid,
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
        cost = 1
        Mana_pull = players[str(ctx.author.id)]["Mana"]
        if cost-Mana_pull > 0:
            enoughmanatime = (players[str(ctx.author.id)]["NextMana"])+(max((cost-Mana_pull-1),0))*basecd
            players[str(ctx.author.id)]["ReadyDate"] = enoughmanatime
            with open("players.json", "w") as f:
                json.dump(players, f, indent=4)
            await queuenexttarget("lightattack",ctx,targetid)
            await ctx.send(f"You don't have the mana for that! The action has been queued for <t:{enoughmanatime}>.", ephemeral = True)
        else:
            await ctx.send(f"You light attack!\n\nSubmit another action!",ephemeral=True)
            if Mana_pull - cost > 0:
                manamoji = await manamojiconv(Mana_pull- cost)
                await ctx.send(f"You have {manamoji} mana remaining",ephemeral=True)
            else :
                await ctx.send(f"Your next action will be queued.",ephemeral=True)
            await dolightattack(ctx.author.id,targetid)
    else:
        await ctx.send(f"You aren't in the competition!" , ephemeral = True)


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
        interactions.Choice(name=item, value=item) for item in items if value.lower() in item.lower()
    ]
    await ctx.populate(choices)

#heavy attack is below
async def doheavyattack(authorid,targetid):
    players = await getplayerdata()
    current_time = int(time.time())
    user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
    location = players[str(authorid)]["Location"]
    channelid = locations[str(location)]["Channel_ID"]
    if players[str(targetid)]["Lastaction"] == "evade" and (players[str(targetid)]["Lastactiontime"]+86400)<current_time:
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
        await send_message(f"<@{targetid}> evaded a heavy attack from <@{authorid}>! \nNew HP: {hpmoji} ", user_id=[authorid,targetid])
        await send_message(f"<@{authorid}> used a heavy attack on <@{targetid}>! ", channel_id=[channelid])
    else:
        await rage(authorid)
        players = await getplayerdata()
        EquippedInventory_pull = players[str(authorid)]["EquippedInventory"]
        damageroll = random.randint(0, 300)
        critroll = random.randint(0, 10) + (EquippedInventory_pull.count("critterihardlyknowher") * 1)
        critdmg = max(critroll-9,0)*3650
        damage = 3500 + damageroll + critdmg
        targethp = players[str(targetid)]["HP"] - damage
        players[str(targetid)]["HP"] = targethp
        await deadcheck(targethp,targetid,authorid,players)
        players[str(authorid)]["Rage"] = players[str(authorid)]["Rage"] +6
        players[str(authorid)]["Mana"] = players[str(authorid)]["Mana"] -3 + min((EquippedInventory_pull.count("AWP")),1)
        players[str(authorid)]["Lastaction"] = "heavyattack"
        hpmoji = await hpmojiconv(targethp)
        with open("players.json", "w") as f:
            json.dump(players, f, indent=4)
        if critroll >= 10:
            send_message( f"<@{authorid}> scored a **CRITICAL HIT** on <@{targetid}>!", channel_id=[channelid])
        else:
            print("nocrit")
        await send_message(f"<@{targetid}> was hit by a heavy attack by <@{authorid}>! \nNew HP: {hpmoji} ", user_id=[authorid,targetid])
        await send_message( f"<@{authorid}> used a heavy attack on <@{targetid}>! ", channel_id=[channelid])

@bot.command(
    name="heavyattack",
    description="3mana.6rage. attack a player in your area for 3500 - 3800 damage.",
    scope = guildid,
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
            await ctx.send(f"You heavy attack!\n\nSubmit another command!",ephemeral=True)
            if Mana_pull - cost > 0:
                manamoji = await manamojiconv(Mana_pull - cost)
                await ctx.send(f"You have {manamoji} mana remaining",ephemeral=True)
            else :
                await ctx.send(f"Your next action will be queued.",ephemeral=True)
            await doheavyattack(ctx.author.id, targetid)
    else:
        await ctx.send(f"You aren't in the competition!", ephemeral=True)


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
        interactions.Choice(name=item, value=item) for item in items if value.lower() in item.lower()
    ]
    await ctx.populate(choices)

#interrupt is below
async def dointerrupt(authorid,targetid):
    players = await getplayerdata()
    current_time = int(time.time())
    user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
    location = players[str(authorid)]["Location"]
    channelid = locations[str(location)]["Channel_ID"]
    if (players[str(targetid)]["Lastaction"] == "evade" or players[str(targetid)]["Lastaction"] == "rest") and (players[str(targetid)]["Lastactiontime"]+86400)<current_time:
        await rage(authorid)
        players = await getplayerdata()
        targethp = players[str(targetid)]["HP"] - 4200
        players[str(targetid)]["HP"] = targethp
        await deadcheck(targethp,targetid,authorid,players)
        players[str(authorid)]["Mana"] = players[str(authorid)]["Mana"] -1
        players[str(authorid)]["Lastaction"] = "interrupt"
        hpmoji = await hpmojiconv(targethp)
        with open("players.json", "w") as f:
            json.dump(players, f, indent=4)
        await send_message(f"<@{targetid}> was hit and damaged by an interrupt by <@{authorid}>! \nNew HP: {hpmoji} ", user_id=[authorid,targetid])
        await send_message(f"<@{authorid}> used an interrupt on <@{targetid}>! ",channel_id=channelid)
    else:
        await rage(authorid)
        players = await getplayerdata()
        players[str(authorid)]["Mana"] = players[str(authorid)]["Mana"] -1
        players[str(authorid)]["Lastaction"] = "interrupt"
        with open("players.json", "w") as f:
            json.dump(players, f, indent=4)
        await send_message(f"<@{targetid}> was not damaged by an interrupt from <@{authorid}>!", user_id=[authorid,targetid])
        await send_message(f"<@{authorid}> used an interrupt on <@{targetid}>! ",channel_id=[channelid])

@bot.command(
    name="interrupt",
    description="1mana. hit a player in your area for 4200 if they are resting or evading.",
    scope = guildid,
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
            await ctx.send(f"You interrupt!\n\nSubmit another command!",ephemeral=True)
            if Mana_pull - cost > 0:
                manamoji = await manamojiconv(Mana_pull - cost)
                await ctx.send(f"You have {manamoji} mana remaining",ephemeral=True)
            else :
                await ctx.send(f"Your next action will be queued.",ephemeral=True)
            await dointerrupt(ctx.author.id, targetid)
    else:
        await ctx.send(f"You aren't in the competition!", ephemeral=True)

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
        interactions.Choice(name=item, value=item) for item in items if value.lower() in item.lower()
    ]
    await ctx.populate(choices)

#evade is below
async def doevade(authorid):
    await rage(authorid)
    players = await getplayerdata()
    user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
    location = players[str(authorid)]["Location"]
    channelid = locations[str(location)]["Channel_ID"]
    players[str(authorid)]["Evade"] = True
    players[str(authorid)]["Mana"] = players[str(authorid)]["Mana"] -1
    players[str(authorid)]["Lastaction"] = "evade"
    players[str(authorid)]["Lastactiontime"] = current_time
    with open("players.json", "w") as f:
        json.dump(players, f, indent=4)
    await send_message(f"<@{authorid}> used evade! ",user_id=[authorid])

@bot.command(
    name="evade",
    description="1mana. receive no damage from light or heavy attacks",
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
            await ctx.send(f"You evade!\n\nSubmit another command!",ephemeral=True)
            if Mana_pull - cost > 0:
                manamoji = await manamojiconv(Mana_pull - cost)
                await ctx.send(f"You have {manamoji} mana remaining",ephemeral=True)
            else :
                await ctx.send(f"Your next action will be queued.",ephemeral=True)
            await doevade(ctx.author.id)
    else:
        await ctx.send(f"You aren't in the competition!" , ephemeral = True)

#rest is below
async def dorest(authorid):
    await rage(authorid)
    players = await getplayerdata()
    user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
    location = players[str(authorid)]["Location"]
    channelid = locations[str(location)]["Channel_ID"]
    hp_pull = players[str(authorid)]["HP"]
    heal = math.ceil(int((10000 - hp_pull) / 2))
    players[str(authorid)]["Mana"] = players[str(authorid)]["Mana"] -1
    players[str(authorid)]["Lastaction"] = "rest"
    players[str(authorid)]["Lastactiontime"] = current_time
    players[str(authorid)]["HP"] = min(players[str(authorid)]["HP"] + heal, 10000)
    hpmoji = await hpmojiconv(players[str(authorid)]["HP"])
    with open("players.json", "w") as f:
        json.dump(players, f, indent=4)
    await send_message(f"<@{authorid}> used rest!  \nNew Hp: {hpmoji}", user_id=[authorid])

@bot.command(
    name="rest",
    description="1mana. heal half your missing health rounded up unless you rested last action.",
    scope = guildid,
)
async def rest_command(ctx: interactions.CommandContext):
    players = await getplayerdata()
    channelid=ctx.channel_id
    if str(ctx.author.id) in players:
        current_time = int(time.time())
        Lastaction_pull=players[str(ctx.author.id)]["Lastaction"]
        cost = 1
        Mana_pull = players[str(ctx.author.id)]["Mana"]
        if Lastaction_pull == "rest":
                await ctx.send(f"You cannot rest! You rested as your last action!", ephemeral = True)
        elif cost-Mana_pull > 0:
            enoughmanatime = (players[str(ctx.author.id)]["NextMana"])+(max((cost-Mana_pull-1),0))*basecd
            players[str(ctx.author.id)]["ReadyDate"] = enoughmanatime
            with open("players.json", "w") as f:
                json.dump(players, f, indent=4)
            await queuenext(ctx)
            await ctx.send(f"You don't have the mana for that! The action has been queued for <t:{enoughmanatime}>.", ephemeral = True)
        else:
            await ctx.send(f"You rest!\n\nSubmit another command!",ephemeral=True)
            if Mana_pull - cost > 0:
                manamoji = await manamojiconv(Mana_pull - cost)
                await ctx.send(f"You have {manamoji} mana remaining",ephemeral=True)
            else :
                await ctx.send(f"Your next action will be queued.",ephemeral=True)
            await dorest(ctx.author.id)
    else:
        await ctx.send(f"You aren't in the competition!" , ephemeral = True)

#exchange is below
async def doexchange(authorid, targetid, readyitem):
    await rage(authorid)
    players = await getplayerdata()
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
    await send_message(f"<@{targetid}> was given {readyitem} from <@{authorid}>!", user_id=[authorid, targetid])
    await send_message(f"<@{authorid}> gave an item to <@{targetid}>! ", channel_id=[channelid], ephemeral=False)


@bot.command(
    name="exchange",
    description="1mana. give a player in your area a ready item from your inventory.",
    scope = guildid,
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
            await ctx.send(f"You cannot exchange when you are not in the crossroads!", ephemeral=True)  # golive
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
            await ctx.send(f"You exchange!\n\nSubmit another command!",ephemeral=True)
            if Mana_pull - cost > 0:
                manamoji = await manamojiconv(Mana_pull - cost)
                await ctx.send(f"You have {manamoji} mana remaining",ephemeral=True)
            else :
                await ctx.send(f"Your next action will be queued.",ephemeral=True)
            await doexchange(ctx.author.id, targetid,readyitem)
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
    #TODO implement channel specific messages... I don't have permission->channel linking in my test env
    await send_message(f"<@{authorid}> farmed {farmSC} from farming", user_id=[authorid]) #channel_id=[farmland])
    await send_message(f"<@{authorid}> farmed! ", channel_id=[channelid])

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
            await ctx.send(f"You cannot farm when you are not in the farmland!", ephemeral=True)  # golive
        elif cost-Mana_pull > 0:
            enoughmanatime = (players[str(ctx.author.id)]["NextMana"])+(max((cost-Mana_pull-1),0))*basecd
            players[str(ctx.author.id)]["ReadyDate"] = enoughmanatime
            with open("players.json", "w") as f:
                json.dump(players, f, indent=4)
            await queuenext(ctx)
            await ctx.send(f"You don't have the mana for that! The action has been queued for <t:{enoughmanatime}>.", ephemeral = True)
        else:
            await ctx.send(f"You farm!\n\nSubmit another command!",ephemeral=True)
            if Mana_pull - cost > 0:
                manamoji = await manamojiconv(Mana_pull - cost)
                await ctx.send(f"You have {manamoji} mana remaining",ephemeral=True)
            else :
                await ctx.send(f"Your next action will be queued.",ephemeral=True)
            await dofarm(ctx.author.id)
    else:
        await ctx.send(f"You aren't in the competition!" , ephemeral = True)

#aid is below

async def doaid(authorid, playertarget):
    await rage(authorid)
    players = await getplayerdata()
    user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
    location = players[str(authorid)]["Location"]
    channelid = locations[str(location)]["Channel_ID"]
    current_time = int(time.time())
    print(f"{playertarget} is the player target")
    for k,v in players.items():
        if v['Username']==str(playertarget):
            targetid=k
    print(f"{targetid} is the player target id")
    targethp=players[str(targetid)]["HP"]
    heal = min(math.ceil(int((10000 - targethp)/4)),10000)
    players[str(authorid)]["Mana"] = players[str(authorid)]["Mana"] -1
    players[str(authorid)]["Lastaction"] = "aid"
    players[str(targetid)]["HP"] = players[str(targetid)]["HP"] + heal
    targethp=players[str(targetid)]["HP"]
    hpmoji = await hpmojiconv(targethp)
    with open("players.json","w") as f:
        json.dump(players,f, indent=4)
    await send_message(f"<@{targetid}> was healed by aid from <@{authorid}>! \nNew HP: {hpmoji} ", user_id=[authorid, playertarget])
    await send_message(f"<@{authorid}> used aid on <@{targetid}> to heal them! ", channel_id=[channelid])


@bot.command(
    name="aid",
    description="1mana. heal chosen player 1/4 of their missing health.",
    scope = guildid,
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
        cost = 1
        Mana_pull = players[str(ctx.author.id)]["Mana"]
        if locations["Keep"]["Role_ID"] not in ctx.author.roles:
            await ctx.send(f"You cannot aid when you are not in the keep!", ephemeral=True)  # golive
        elif cost-Mana_pull > 0:
            enoughmanatime = (players[str(ctx.author.id)]["NextMana"])+(max((cost-Mana_pull-1),0))*basecd
            players[str(ctx.author.id)]["ReadyDate"] = enoughmanatime
            with open("players.json", "w") as f:
                json.dump(players, f, indent=4)
            await queuenexttarget("aid",ctx,playertarget)
            await ctx.send(f"You don't have the mana for that! The action has been queued for <t:{enoughmanatime}>.", ephemeral = True)
        else:
            await ctx.send(f"You aid!",ephemeral=True)
            if Mana_pull - cost > 0:
                manamoji = await manamojiconv(Mana_pull - cost)
                await ctx.send(f"You have {manamoji} mana remaining",ephemeral=True)
            else :
                await ctx.send(f"Your next action will be queued.",ephemeral=True)
            await doaid(ctx.author.id, playertarget,channelid)
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
    players = await getplayerdata()
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
    await send_message(f"One {itemtarget} was purchased by <@{authorid}> from the shop!", user_id=[authorid])
    await send_message(f"<@{authorid}> purchased an item from the shop! ", channel_id=[channelid])


@bot.command(
    name="trade",
    description="1mana. exchange seed coins for a shop item.",
    scope = guildid,
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
        manacost = 1
        Mana_pull = players[str(ctx.author.id)]["Mana"]
        if locations["Shop"]["Role_ID"] not in ctx.author.roles:
            await ctx.send(f"You cannot trade when you are not in the Shop!", ephemeral=True)  # golive
        elif players[str(authorid)]["SC"] <= shop[str(itemtarget)]["Cost"]:
            await ctx.send(f"Your {SC_pull} seed coins are not able to purchase an item that costs {cost} seed coins! ", ephemeral = True)
        elif manacost-Mana_pull > 0:
            enoughmanatime = (players[str(ctx.author.id)]["NextMana"])+(max((manacost-Mana_pull-1),0))*basecd
            players[str(ctx.author.id)]["ReadyDate"] = enoughmanatime
            with open("players.json", "w") as f:
                json.dump(players, f, indent=4)
            await queuenexttarget("trade",ctx,itemtarget)
            await ctx.send(f"You don't have the mana for that! The action has been queued for <t:{enoughmanatime}>.", ephemeral = True)
        else:
            await ctx.send(f"You trade!\n\nSubmit another command!",ephemeral=True)
            if Mana_pull - manacost > 0:
                manamoji = await manamojiconv(Mana_pull - manacost)
                await ctx.send(f"You have {manamoji} mana remaining",ephemeral=True)
            else :
                await ctx.send(f"Your next action will be queued.",ephemeral=True)
            await dotrade(ctx.author.id, itemtarget)
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

#drinkingchallenge is below

async def dodrinkingchallenge(authorid):
    await rage(authorid)
    players = await getplayerdata()
    scores = await gettaverndata()
    cooldown = basecd
    Lastaction_pull = players[str(authorid)]["Lastaction"]
    playerroll = int(int(random.randint(1,4)) + (Lastaction_pull.count("drinkingchallenge") * 1))
    print(f"playerroll = {playerroll}")
    print(f"scores = \n{scores}\n")
    current_time = int(time.time())
    players[str(authorid)]["Mana"] = players[str(authorid)]["Mana"] -1
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
        players[str(authorid)]["EquippedInventory"]=players[str(authorid)]["EquippedInventory"] + "\n        "+"drinkingmedal"
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
    description="1mana. score 1d4.high:gain drinkingmedal. heal 1/4 missing hp except low score loses 1/4hp.",
    scope = guildid,
)
async def drinkingchallenge(ctx: interactions.CommandContext):
    players = await getplayerdata()
    current_time = int(time.time())
    channelid=ctx.channel_id
    if str(ctx.author.id) in players:
        cost = 1
        Mana_pull = players[str(ctx.author.id)]["Mana"]
        if locations["Tavern"]["Role_ID"] not in ctx.author.roles:
            await ctx.send(f"You cannot drinkingchallenge when you are not in the tavern!", ephemeral=True)  # golive
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
            await dodrinkingchallenge(ctx.author.id)
    else:
        await ctx.send(f"You aren't in the competition!" , ephemeral = True)

#loot is below

async def doloot(authorid):
    await rage(authorid)
    players = await getplayerdata()
    scores = await getdungeondata()
    cooldown = basecd
    Lastaction_pull = players[str(authorid)]["Lastaction"]
    EquippedInventory_pull=players[str(authorid)]["EquippedInventory"]
    playerroll = int(int(random.randint(1,4)) + (Lastaction_pull.count("loot") * 1)) + (EquippedInventory_pull.count("adventuringgear") * 1)
    print(f"playerroll = {playerroll}")
    print(f"scores = \n{scores}\n")
    current_time = int(time.time())
    players[str(authorid)]["Mana"] = players[str(authorid)]["Mana"] -1
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
    with open("dungeon.json","w") as o:
        json.dump(scores,o, indent=4)
    print("Player dungeon Score Saved")
    #check if the max is greater than the player's roll
    if highscore > playerroll:
        print(f"playerscore is lower than highscore")
        await send_message(f"<@{authorid}>'s roll of {playerroll} failed to beat the high score of {highscore}" , channel_id=[locations["Dungeon"]["Channel_ID"]])
    else:
        print(f"playerscore is the highscore")
        await send_message(f"<@{authorid}>'s roll of {playerroll} beat the high score of {highscore} and got a random item." , channel_id=[locations["Dungeon"]["Channel_ID"]])
        shop = await getshopdata()
        randomitem = random.choice(list(shop))
        await send_message(f"<@{authorid}> you gained {randomitem} as a random item.", user_id=[authorid])
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
            await ctx.send(f"You cannot /loot when you are not in the Dungeon!", ephemeral=True)  # golive
        elif cost-Mana_pull > 0:
            enoughmanatime = (players[str(ctx.author.id)]["NextMana"])+(max((cost-Mana_pull-1),0))*basecd
            players[str(ctx.author.id)]["ReadyDate"] = enoughmanatime
            with open("players.json", "w") as f:
                json.dump(players, f, indent=4)
            await queuenext(ctx)
            await ctx.send(f"You don't have the mana for that! The action has been queued for <t:{enoughmanatime}>.", ephemeral = True)
        else:
            await ctx.send(f"You loot!\n\nSubmit another command!",ephemeral=True)
            if Mana_pull - cost > 0:
                manamoji = await manamojiconv(Mana_pull - cost)
                await ctx.send(f"You have {manamoji} mana remaining",ephemeral=True)
            else :
                await ctx.send(f"Your next action will be queued.",ephemeral=True)
            await doloot(ctx.author.id)
    else:
        await ctx.send(f"You aren't in the competition!" , ephemeral = True)

#battlelich is below

async def dobattlelich(authorid):
    await rage(authorid)
    players = await getplayerdata()
    scores = await getlichdata()
    Lastaction_pull = players[str(authorid)]["Lastaction"]
    cooldown = basecd
    playerroll = int(int(random.randint(1,4)) + (Lastaction_pull.count("battlelich") * 1))
    print(f"playerroll = {playerroll}")
    print(f"scores = \n{scores}\n")
    current_time = int(time.time())
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
        await send_message(f"<@{authorid}>'s roll of {playerroll} failed to beat the high score of {highscore}" , channel_id=[locations["Lich's Castle"]["Channel_ID"]])
    else:
        print(f"playerscore is the highscore")
        await send_message(f"<@{authorid}>'s roll of {playerroll} beat the high score of {highscore} and got the lichitem." , channel_id=[locations["Lich's Castle"]["Channel_ID"]])
        players[str(authorid)]["ReadyInventory"]=players[str(authorid)]["ReadyInventory"] + "\n        "+"lichitem"
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
    if lowscore == playerroll: #check if the min is equal to the player's roll
        print(f"lowscore is equal to playerscore")
        hp_pull = players[str(authorid)]["HP"]
        hp_pull=max(hp_pull - math.ceil(hp_pull/4),0)
        hpmoji = await hpmojiconv(hp_pull)
        await send_message(f"<@{authorid}> your roll of {playerroll} is the lowest roll. \nNew HP: {hpmoji}" , user_id=[authorid] )
        await send_message(f"<@{authorid}>'s roll of {playerroll} is the lowest roll and they lose 1/4 of their current health!" , channel_id=[locations["Lich's Castle"]["Channel_ID"]])
        players[str(authorid)]["HP"] = hp_pull
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
    else :
        return
    with open("players.json","w") as f:
        json.dump(players,f, indent=4)

async def douse(authorid, readyitem):
    players = await getplayerdata()
    shop = await getshopdata()
    user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
    location = players[str(authorid)]["Location"]
    channelid = locations[str(location)]["Channel_ID"]
    current_time = int(time.time())
    loop = asyncio.get_running_loop()
    loop.create_task(functiondict[readyitem](**{'authorid': authorid}))
    ReadyInventory_pull = str(players[str(authorid)]["ReadyInventory"])
    players[str(authorid)]["Mana"] = players[str(authorid)]["Mana"] - shop[readyitem]["ManaCost"]
    with open("players.json","w") as f:
        json.dump(players,f, indent=4)

@bot.command(
    name="use",
    description="Xmana. use or equip an item in your inventory",
    scope = guildid,
    options=[
        interactions.Option(
            type=interactions.OptionType.STRING,
            name="readyitem",
            description="the item you want to use",
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
            await ctx.send(f"You use an item!\n\nSubmit another command!",ephemeral=True)
            if Mana_pull - cost > 0:
                manamoji = await manamojiconv(Mana_pull - cost)
                await ctx.send(f"You have {manamoji} mana remaining",ephemeral=True)
            else :
                await ctx.send(f"Your next action will be queued.",ephemeral=True)
            await douse(ctx.author.id, readyitem)
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
            await ctx.send(f"You cannot battlelich when you are not in the Lich's Castle!", ephemeral=True)  # golive
        elif cost-Mana_pull > 0:
            enoughmanatime = (players[str(ctx.author.id)]["NextMana"])+(max((cost-Mana_pull-1),0))*basecd
            players[str(ctx.author.id)]["ReadyDate"] = enoughmanatime
            with open("players.json", "w") as f:
                json.dump(players, f, indent=4)
            await queuenext(ctx)
            await ctx.send(f"You don't have the mana for that! The action has been queued for <t:{enoughmanatime}>.", ephemeral = True)
        else:
            await ctx.send(f"You battle the lich!\n\nSubmit another command!",ephemeral=True)
            if Mana_pull - cost > 0:
                manamoji = await manamojiconv(Mana_pull - cost)
                await ctx.send(f"You have {manamoji} mana remaining",ephemeral=True)
            else :
                await ctx.send(f"Your next action will be queued.",ephemeral=True)
            await dobattlelich(ctx.author.id)
    else:
        await ctx.send(f"You aren't in the competition!" , ephemeral = True)

#lichitem is below

async def dolichitem(authorid):
    await rage(authorid)
    players = await getplayerdata()
    current_time = int(time.time())
    user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
    location = players[str(authorid)]["Location"]
    channelid = locations[str(location)]["Channel_ID"]
    players[str(authorid)]["Mana"] = players[str(authorid)]["Mana"] -1
    players[str(authorid)]["Lastaction"] = "lichitem"
    targethp=players[str(targetid)]["HP"]
    hpmoji = await hpmojiconv(targethp)
    user = await interactions.get(bot, interactions.Member, object_id=targetid, guild_id=guildid, force='http')
    userreadyinventory=str(players[str(authorid)]["ReadyInventory"])
    #replace first instance of item in user's readyinventory
    players[str(authorid)]["ReadyInventory"]=userreadyinventory.replace('\n        lichitem','',1)
    #add the item to the user's Equippedinventory
    players[str(authorid)]["EquippedInventory"]=players[str(authorid)]["EquippedInventory"]+"\n        lichitem"
    with open("players.json","w") as f:
        json.dump(players,f, indent=4)
    await send_message(f"<@{authorid}> equipped a lichitem to protect themselves from their next death! ", channel_id=[channelid])


#drinkingmedal is below

async def dodrinkingmedal(authorid):
    await rage(authorid)
    players = await getplayerdata()
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
    await send_message(f"<@{authorid}> used drinkingmedal to increase their lightattack damage by 420! ", channel_id=[channelid])


#goodiebag is below

async def dogoodiebag(authorid):
    await rage(authorid)
    players = await getplayerdata()
    user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
    location = players[str(authorid)]["Location"]
    channelid = locations[str(location)]["Channel_ID"]
    current_time = int(time.time())
    players[str(authorid)]["Lastaction"] = "goodiebag"
    userreadyinventory=str(players[str(authorid)]["ReadyInventory"])
    #get a randomitem
    shop = await getshopdata()
    randomitem = random.choice(list(shop))
    await send_message(f"<@{authorid}> you gained {randomitem} as a random item.", user_id=[authorid])
    players[str(authorid)]["ReadyInventory"]=players[str(authorid)]["ReadyInventory"] + "\n        "+str(randomitem)
    userreadyinventory=str(players[str(authorid)]["ReadyInventory"])
    #replace first instance of item in user's readyinventory
    players[str(authorid)]["ReadyInventory"]=userreadyinventory.replace('\n        goodiebag','',1)
    #add the item to the user's Equippedinventory
    players[str(authorid)]["EquippedInventory"]=players[str(authorid)]["EquippedInventory"] + "\n        "+"goodiebag"
    with open("players.json","w") as f:
        json.dump(players,f, indent=4)
    await send_message(f"<@{authorid}> used goodiebag to gain a random item! ", channel_id=[channelid])

#tractor is below

async def dotractor(authorid):
    await rage(authorid)
    players = await getplayerdata()
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
    await send_message(f"<@{authorid}> used tractor to increase their farm profit by 1! ", channel_id=[channelid])

#critterihardlyknowher is below

async def docritterihardlyknowher(authorid):
    await rage(authorid)
    players = await getplayerdata()
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
    await send_message(f"<@{authorid}> used critterihardlyknowher to increase their crit rolls by 1 for the rest of the game!\n(Crit is a 1d10 roll, a 10 or higher is a crit that increases damage by 50%) \n", channel_id=[channelid])

#beer-bandolier is below

async def dobeerbando(authorid):
    await rage(authorid)
    players = await getplayerdata()
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
    await send_message(f"<@{authorid}> used beerbando to increase their rage by 3! ", channel_id=[channelid])

#localligmaoutbreak is below

async def dolocalligmaoutbreak(authorid):
    await rage(authorid)
    players = await getplayerdata()
    ligma = await getligmadata()
    current_time = int(time.time())
    players[str(authorid)]["Lastaction"] = "localligmaoutbreak"
    user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
    location = players[str(authorid)]["Location"]
    channelid = locations[str(location)]["Channel_ID"]
    samelocationUserIDs = {k: v for k, v in players.items() if v['Location'] == location}
    ligmadamage_pull = ligma["ligmadamage"]
    #damage everyone in the area
    for key in players.keys():
      if key in samelocationUserIDs:
        players[key]['HP'] = players[key]['HP'] - ligmadamage_pull
    userreadyinventory=str(players[str(authorid)]["ReadyInventory"])
    #replace first instance of item in user's readyinventory
    players[str(authorid)]["ReadyInventory"]=userreadyinventory.replace('\n        localligmaoutbreak','',1)
    with open("players.json","w") as f:
        json.dump(players,f, indent=4)
    await send_message(f"<@{authorid}> used a local ligma outbreak! \n\n\n||LIGMA BALLS|| dealt {ligmadamage_pull} to @everyone in {location}!!", channel_id=[channelid])

#AWP is below

async def doAWP(authorid):
    await rage(authorid)
    players = await getplayerdata()
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
    await send_message(f"<@{authorid}> needs to pick up a weel gun! \n\nThey have equipped an AWP, to decrease the mana cost of their heavy attacks to 2! ", channel_id=[channelid])

#Crooked Abacus is below

async def docrookedabacus(authorid):
    await rage(authorid)
    players = await getplayerdata()
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
    await send_message(f"<@{authorid}> used a crookedabacus to gain a seedcoin whenever they /trade or /exchange for the rest of the game! ", channel_id=[channelid])

#adventuringgear is below

async def doadventuringgear(authorid):
    await rage(authorid)
    players = await getplayerdata()
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
    await send_message(f"<@{authorid}> used adventuringgear to score one higher whenever they /loot for the rest of the game! ", channel_id=[channelid])

actionhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="Actions",
    custom_id="Actions",
)

@bot.component("Actions")
async def button_response(ctx):
    row = interactions.spread_to_rows(lightattackhelpbutton, heavyattackhelpbutton, interrupthelpbutton, evadehelpbutton, resthelpbutton, areactionhelpbutton,useitemhelpbutton)
    await ctx.send(f"**Actions**\nActions are what players do!\n\nMost actions cost mana. You generate one mana every {int(basecd/60/60)} hours. Players can't take any actions that would make their mana negative.\n\nWhen you attempt to perform an action and you don't have the mana, you will instead queue that action. The bot will make you perform that action after you have the mana.\n\nFind out more:", components=row, ephemeral=True)


lightattackhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.DANGER,
    label="Lightattack",
    custom_id="Lightattack",
)

@bot.component("Lightattack")
async def button_response(ctx):
    await ctx.send(f"**Light Attack**\n/lightattack\n1 mana. gain 1 rage. attack a player in your area for 800 to 1100 damage.", ephemeral=True)

heavyattackhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.DANGER,
    label="Heavyattack",
    custom_id="Heavyattack",
)

@bot.component("Heavyattack")
async def button_response(ctx):
    await ctx.send(f"**Heavy Attack**\n/heavyattack\n3 mana. gain 6 rage. attack a player in your area for 3500 to 3800 damage.", ephemeral=True)

interrupthelpbutton = interactions.Button(
    style=interactions.ButtonStyle.DANGER,
    label="Interrupt",
    custom_id="Interrupt",
)

@bot.component("Interrupt")
async def button_response(ctx):
    await ctx.send(f"**Interrupt**\n/interrupt\n1 mana. hit a player in your area for 4200 if they are resting or evading.", ephemeral=True)


evadehelpbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Evade",
    custom_id="Evade",
)

@bot.component("Evade")
async def button_response(ctx):
    await ctx.send(f"**Evade**\n/evade\n1 mana. Receive no damage from light or heavy attacks for 24h.", ephemeral=True)


resthelpbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Rest",
    custom_id="Rest",
)

@bot.component("Rest")
async def button_response(ctx):
    await ctx.send(f"**Rest**\n/rest\n1 mana. Heal half of your missing health rounded up unless you used rest as your last action.", ephemeral=True)

areactionhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="AreaAction",
    custom_id="AreaAction",
)

@bot.component("AreaAction")
async def button_response(ctx):
    row = interactions.spread_to_rows(crossroadshelpbutton, dungeonhelpbutton, farmlandhelpbutton, keephelpbutton, lichcastlehelpbutton, shophelpbutton, tavernhelpbutton)
    await ctx.send(f"**Locations** \nYou can travel from any location to the Crossroads using /travel \n\nYou can travel from the Crossroads to any area using /travel \nLocations each have their own unique area action!\n\nArea actions always cost 1 mana, but have a variety of effects. \n\nUse the buttons below to learn more about the area actions:", components = row, ephemeral=True)

useitemhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="Use an Item",
    custom_id="useitem",
)

@bot.component("useitem")
async def button_response(ctx):
    row = interactions.spread_to_rows(adventuringgearhelpbutton, AWPhelpbutton, crookedabacushelpbutton, goodiebaghelpbutton, tractorhelpbutton, drinkingmedalhelpbutton, lichitemhelpbutton, beerbandohelpbutton, critterihardlyknowherhelpbutton)
    await ctx.send(f"**Items** \nItems fall into two broad categories: \n\n**Ready Items**\nItems you can use for benefits that can be instantaneous, duration, or permanent in nature.\nWhen you use a Ready Item for a passive effect, it moves to your Equipped Items.\n\n**Equipped items**\nItems you have used in the past that are giving you a passive effect.\n\nFind out more about the items below:", components = row, ephemeral=True)

locationhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="Locations",
    custom_id="Locations",
)

@bot.component("Locations")
async def button_response(ctx):
    row = interactions.spread_to_rows(crossroadshelpbutton, dungeonhelpbutton, farmlandhelpbutton, keephelpbutton, lichcastlehelpbutton, shophelpbutton, tavernhelpbutton)
    await ctx.send(f"**Locations** \nYou can travel from any location to the crossroads using /traveltocrossroads \n\nYou can travel from the crossroads to any area using /travelto \nLocations each have their own unique area action!\n\nArea actions always cost 1 mana, but have a variety of effects. \n\nUse the buttons below to learn more about the area actions:", components = row, ephemeral=True)

crossroadshelpbutton = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="Crossroads",
    custom_id="Crossroads",
)

@bot.component("Crossroads")
async def button_response(ctx):
    await ctx.send(f"**Crossroads**\n/exchange\n1 mana. give a player in your area a ready item from your inventory.", ephemeral=True)

dungeonhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="Dungeon",
    custom_id="Dungeon",
)

@bot.component("Dungeon")
async def button_response(ctx):
    await ctx.send(f"**Dungeon**\n/loot\n1 mana. score 1d4. on 4+ gain two items at random. lowest score: lose 1/4 of your current health.", ephemeral=True)

farmlandhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="Farmland",
    custom_id="Farmland",
)

@bot.component("Farmland")
async def button_response(ctx):
    await ctx.send(f"**Farmland**\n/farm\n1 mana. score 1d4. gain your score seed coins.", ephemeral=True)


keephelpbutton = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="Keep",
    custom_id="Keep",
)

@bot.component("Keep")
async def button_response(ctx):
    await ctx.send(f"**Keep**\n/aid\n1 mana. heal the chosen player 1/4 of their missing health.", ephemeral=True)


lichcastlehelpbutton = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="Lich's Castle",
    custom_id="lichcastle",
)

@bot.component("lichcastle")
async def button_response(ctx):
    await ctx.send(f"**Lich's Castle**\n/battlelich\n1 mana. score 1d4. high score: gain Lich's Item. low score: lose 1/4 current health.", ephemeral=True)

shophelpbutton = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="Shop",
    custom_id="Shop",
)

@bot.component("Shop")
async def button_response(ctx):
    await ctx.send(f"**Shop**\n/trade\n1 mana. exchange seed coins for a shop item.", ephemeral=True)

tavernhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="Tavern",
    custom_id="Tavern",
)

@bot.component("Tavern")
async def button_response(ctx):
    await ctx.send(f"**Tavern**\n/drinkingchallenge\n1 mana. score 1d4. high score: gain a Equipped drinking challenge medal. low score: loses 1/4 current health otherwise: heal 1/4 missing health.", ephemeral=True)

itemhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="Items",
    custom_id="Items",
)

@bot.component("Items")
async def button_response(ctx):
    row = interactions.spread_to_rows(adventuringgearhelpbutton, AWPhelpbutton, crookedabacushelpbutton, goodiebaghelpbutton, tractorhelpbutton, drinkingmedalhelpbutton, lichitemhelpbutton, localligmaoutbreakhelpbutton, beerbandohelpbutton, critterihardlyknowherhelpbutton)
    await ctx.send(f"**Items** \nItems fall into two broad categories: \n\n**Ready Items**\nItems you can use for benefits that can be instantaneous, duration, or permanent in nature.\nWhen you use a Ready Item it moves to your Equipped Items.\n\n**Equipped items**\nItems you have used in the past that are giving you a passive effect.\n\nFind out more about the items below:", components = row, ephemeral=True)

adventuringgearhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Adventuring Gear",
    custom_id="adventuringgear",
)

@bot.component("adventuringgear")
async def button_response(ctx):
    await ctx.send(f"**Adventuring Gear**\n5 SC cost \n2 mana. increase your loot score by 1 for the rest of the game.", ephemeral=True)


localligmaoutbreakhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Local Ligma Outbreak",
    custom_id="localligmaoutbreak",
)

@bot.component("localligmaoutbreak")
async def button_response(ctx):
    await ctx.send(f"**Local Ligma Outbreak**\n5 SC cost \n2 mana. deal the current ligma damage to everyone in your area (including yourself).", ephemeral=True)

AWPhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="AWP",
    custom_id="AWP",
)

@bot.component("AWP")
async def button_response(ctx):
    await ctx.send(f"**Aim Training**\n8 SC cost\n3 mana. Reduce heavy attack mana cost to two for the rest of the game. doesn't stack.", ephemeral=True)

crookedabacushelpbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Crooked Abacus",
    custom_id="crookedabacus",
)

@bot.component("crookedabacus")
async def button_response(ctx):
    await ctx.send(f"**Crooked Abacus**\n5 SC cost\n2 mana. Whenever you exchange or trade, gain a seed coin for the rest of the game.", ephemeral=True)

goodiebaghelpbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Goodie Bag",
    custom_id="goodiebag",
)

@bot.component("goodiebag")
async def button_response(ctx):
    await ctx.send(f"**Goodie Bag**\n8 SC cost\n1 mana. Add a random ready item to your inventory.", ephemeral=True)

tractorhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Tractor",
    custom_id="tractor",
)

@bot.component("tractor")
async def button_response(ctx):
    await ctx.send(f"**Tractor**\n5 SC cost\n2 mana. Whenever you farm, gain an additional seed coin for the rest of the game.", ephemeral=True)

drinkingmedalhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Drinking Medal ",
    custom_id="drinkingmedal",
)

@bot.component("drinkingmedal")
async def button_response(ctx):
    await ctx.send(f"**Drinking Medal**\n6 SC cost\n2 mana. Increase the damage of your light attack by 420 for the rest of the game.", ephemeral=True)

lichitemhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Lich's Item ",
    custom_id="lichitem",
)

@bot.component("lichitem")
async def button_response(ctx):
    await ctx.send(f"**Lich's Item**\n15 SC cost\n2 mana. The next time you would die, set your HP to 4200 instead.", ephemeral=True)

beerbandohelpbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Beer Bandolier",
    custom_id="beerbando",
)

@bot.component("beerbando")
async def button_response(ctx):
    await ctx.send(f"**Beer Bandolier**\n3 SC cost\n1 mana. You gain three rage.", ephemeral=True)

critterihardlyknowherhelpbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Critter? I hardly know her",
    custom_id="critterihardlyknowher",
)

@bot.component("critterihardlyknowher")
async def button_response(ctx):
    await ctx.send(f"**Critter? I hardly know her**\n6 SC cost \n2 mana. increase your crit rolls by 1 for the rest of the game.\n*(Crit rolls are made on a 1d10, rolls >=10 deal 50% extra damage)*", ephemeral=True)

Ligmahelpbutton = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Ligma",
    custom_id="Ligma",
)

@bot.component("Ligma")
async def button_response(ctx):
    await ctx.send(f"**Ligma**\n\nWhen the game starts A 7 day ligma timer starts and the ligma damage is set to 650.\n\nWhenever the ligma timer ends, the ligma damage increases by 100 then every player is damaged by the ligma.\n\nThen the ligma timer restarts with 10% less time.", ephemeral=True)

Ragehelpbutton = interactions.Button(
    style=interactions.ButtonStyle.DANGER,
    label="Rage",
    custom_id="Rage",
)

@bot.component("Rage")
async def button_response(ctx):
    await ctx.send(f"**Rage**\n\nWhenever you take an action, you heal equal to your Rage times 420hp. Then you lose one Rage.", ephemeral=True)

@bot.command(
    name="help",
    description="get info on a topic",
)
async def help(ctx: interactions.CommandContext,):
    players = await getplayerdata()
    current_time = int(time.time())
    channelid=ctx.channel_id
    row = interactions.ActionRow(
    components=[actionhelpbutton, locationhelpbutton, itemhelpbutton, Ligmahelpbutton, Ragehelpbutton ]
)
    await ctx.send(f"What would you like help with?", components = row, ephemeral = True)

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
    await ctx.send(f"How much of your HP would you like to wager?", components = row, ephemeral=True)

button5hp = interactions.Button(
    style=interactions.ButtonStyle.DANGER,
    label="5 HP",
    custom_id="button5hp",
)

@bot.component("button5hp")
async def button_response(ctx):
    flip =  int(random.randint(1, 2))
    if flip == 1:
        tag = "lost"
        players = await getplayerdata()
        players[str(ctx.author.id)]["HP"] = players[str(ctx.author.id)]["HP"] -5
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
        targethp = players[str(ctx.author.id)]["HP"]
        targetid = ctx.author.id
        authorid = ctx.author.id
        await deadcheck(targethp,targetid,authorid,players)
        await ctx.send(f"<@{ctx.author.id}> rolled ribs!", ephemeral=True)
        await send_message(f"<@{ctx.author.id}> {tag} five health with /gamble!", channel_id=[general], ephemeral=False)
    elif flip == 2:
        tag = "won"
        players = await getplayerdata()
        players[str(ctx.author.id)]["HP"] = min(players[str(ctx.author.id)]["HP"] +5, 10000)
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
        await ctx.send(f"<@{ctx.author.id}> rolled loins!", ephemeral=True)
        await send_message(f"<@{ctx.author.id}> {tag} five health with /gamble!", channel_id=[general], ephemeral=False)

button25hp = interactions.Button(
    style=interactions.ButtonStyle.DANGER,
    label="25 HP",
    custom_id="button25hp",
)

@bot.component("button25hp")
async def button_response(ctx):
    flip =  int(random.randint(1, 2))
    if flip == 1:
        tag = "lost"
        players = await getplayerdata()
        players[str(ctx.author.id)]["HP"] = players[str(ctx.author.id)]["HP"] -25
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
        targethp = players[str(ctx.author.id)]["HP"]
        targetid = ctx.author.id
        authorid = ctx.author.id
        await deadcheck(targethp,targetid,authorid,players)
        await ctx.send(f"You rolled ribs!", ephemeral=True)
        await send_message(f"You {tag} twenty-five health with /gamble!",channel_id=[general], ephemeral=False)
    elif flip == 2:
        tag = "won"
        players = await getplayerdata()
        players[str(ctx.author.id)]["HP"] = min(players[str(ctx.author.id)]["HP"] +25, 10000)
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
        await ctx.send(f"<@{ctx.author.id}> rolled loins!", ephemeral=True)
        await send_message(f"<@{ctx.author.id}> {tag} twenty-five health with /gamble!", channel_id=[general],ephemeral=False)

button50hp = interactions.Button(
    style=interactions.ButtonStyle.DANGER,
    label="50 HP",
    custom_id="button50hp",
)

@bot.component("button50hp")
async def button_response(ctx):
    flip =  int(random.randint(1, 2))
    if flip == 1:
        tag = "lost"
        players = await getplayerdata()
        players[str(ctx.author.id)]["HP"] = players[str(ctx.author.id)]["HP"] -50
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
        targethp = players[str(ctx.author.id)]["HP"]
        targetid = ctx.author.id
        authorid = ctx.author.id
        await deadcheck(targethp,targetid,authorid,players)
        await ctx.send(f"<@{ctx.author.id}> rolled ribs!", ephemeral=True)
        await send_message(f"<@{ctx.author.id}> {tag} fifty health with /gamble!", channel_id=[general], ephemeral=False)
    elif flip == 2:
        tag = "won"
        players = await getplayerdata()
        players[str(ctx.author.id)]["HP"] = min(players[str(ctx.author.id)]["HP"] +50, 10000)
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
        await ctx.send(f"<@{ctx.author.id}> rolled loins!", ephemeral=True)
        await send_message(f"<@{ctx.author.id}> {tag} fifty health with /gamble!", channel_id=[general], ephemeral=False)


button75hp = interactions.Button(
    style=interactions.ButtonStyle.DANGER,
    label="75 HP",
    custom_id="button75hp",
)

@bot.component("button75hp")
async def button_response(ctx):
    flip =  int(random.randint(1, 2))
    if flip == 1:
        tag = "lost"
        players = await getplayerdata()
        players[str(ctx.author.id)]["HP"] = players[str(ctx.author.id)]["HP"] -75
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
        targethp = players[str(ctx.author.id)]["HP"]
        targetid = ctx.author.id
        authorid = ctx.author.id
        await deadcheck(targethp,targetid,authorid,players)
        await ctx.send(f"<@{ctx.author.id}> rolled ribs!", ephemeral=True)
        await send_message(f"<@{ctx.author.id}> {tag} seventy-five health with /gamble!",channel_id=[general], ephemeral=False)
    elif flip == 2:
        tag = "won"
        players = await getplayerdata()
        players[str(ctx.author.id)]["HP"] = min(players[str(ctx.author.id)]["HP"] +75, 10000)
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
        await ctx.send(f"<@{ctx.author.id}> rolled loins!", ephemeral=True)
        await send_message(f"<@{ctx.author.id}> {tag} seventy-five health with /gamble!", channel_id=[general], ephemeral=False)

button100hp = interactions.Button(
    style=interactions.ButtonStyle.DANGER,
    label="100 HP",
    custom_id="button100hp",
)

@bot.component("button100hp")
async def button_response(ctx):
    flip =  int(random.randint(1, 2))
    if flip == 1:
        tag = "lost"
        players = await getplayerdata()
        players[str(ctx.author.id)]["HP"] = players[str(ctx.author.id)]["HP"] -100
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
        targethp = players[str(ctx.author.id)]["HP"]
        targetid = ctx.author.id
        authorid = ctx.author.id
        await deadcheck(targethp,targetid,authorid,players)
        await ctx.send(f"<@{ctx.author.id}> rolled ribs!", ephemeral=True)
        await send_message(f"<@{ctx.author.id}> {tag} one hundred health with /gamble!", channel_id=[general], ephemeral=False)
    elif flip == 2:
        tag = "won"
        players = await getplayerdata()
        players[str(ctx.author.id)]["HP"] = min(players[str(ctx.author.id)]["HP"] +100, 10000)
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
        await ctx.send(f"<@{ctx.author.id}> rolled loins!", ephemeral=True)
        await send_message(f"<@{ctx.author.id}> {tag} one hundred health with /gamble!", channel_id=[general], ephemeral=False)

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
    await ctx.send(f"How many SC would you like to wager?\n\n*p.s. beware, you can go negative*", components = row, ephemeral=True)

button1sc = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="1 SC",
    custom_id="button1sc",
)

@bot.component("button1sc")
async def button_response(ctx):
    flip =  int(random.randint(1, 2))
    if flip == 1:
        tag = "lost"
        players = await getplayerdata()
        players[str(ctx.author.id)]["SC"] = players[str(ctx.author.id)]["SC"] -1
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
        await ctx.send(f"<@{ctx.author.id}> rolled ribs!", ephemeral=True)
        await send_message(f"<@{ctx.author.id}> {tag} one SC with /gamble!", channel_id=[general], ephemeral=False)
    elif flip == 2:
        tag = "won"
        players = await getplayerdata()
        players[str(ctx.author.id)]["SC"] = players[str(ctx.author.id)]["SC"] +1
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
        await ctx.send(f"<@{ctx.author.id}> rolled loins!", ephemeral=True)
        await send_message(f"<@{ctx.author.id}> {tag} one SC with /gamble!", channel_id=[general], ephemeral=False)


button2sc = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="2 SC",
    custom_id="button2sc",
)

@bot.component("button2sc")
async def button_response(ctx):
    flip =  int(random.randint(1, 2))
    if flip == 1:
        tag = "lost"
        players = await getplayerdata()
        players[str(ctx.author.id)]["SC"] = players[str(ctx.author.id)]["SC"] -2
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
        await ctx.send(f"<@{ctx.author.id}> rolled ribs!", ephemeral=True)
        await send_message(f"<@{ctx.author.id}> {tag} two SC with /gamble!", channel_id=[general], ephemeral=False)
    elif flip == 2:
        tag = "won"
        players = await getplayerdata()
        players[str(ctx.author.id)]["SC"] = players[str(ctx.author.id)]["SC"] +2
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
        await ctx.send(f"<@{ctx.author.id}> rolled loins!", ephemeral=True)
        await send_message(f"<@{ctx.author.id}> {tag} two SC with /gamble!", channel_id=[general], ephemeral=False)


button3sc = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="3 SC",
    custom_id="button3sc",
)

@bot.component("button3sc")
async def button_response(ctx):
    flip =  int(random.randint(1, 2))
    if flip == 1:
        tag = "lost"
        players = await getplayerdata()
        players[str(ctx.author.id)]["SC"] = players[str(ctx.author.id)]["SC"] -3
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
        await ctx.send(f"<@{ctx.author.id}> rolled ribs!", ephemeral=True)
        await send_message(f"<@{ctx.author.id}> {tag} three SC with /gamble!", channel_id=[general], ephemeral=False)
    elif flip == 2:
        tag = "won"
        players = await getplayerdata()
        players[str(ctx.author.id)]["SC"] = players[str(ctx.author.id)]["SC"] +3
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
        await ctx.send(f"<@{ctx.author.id}> rolled loins!", ephemeral=True)
        await send_message(f"<@{ctx.author.id}> {tag} three SC with /gamble!", channel_id=[general], ephemeral=False)

button4sc = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="4 SC",
    custom_id="button4sc",
)

@bot.component("button4sc")
async def button_response(ctx):
    flip =  int(random.randint(1, 2))
    if flip == 1:
        tag = "lost"
        players = await getplayerdata()
        players[str(ctx.author.id)]["SC"] = players[str(ctx.author.id)]["SC"] -4
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
        await ctx.send(f"<@{ctx.author.id}> rolled ribs!", ephemeral=True)
        await send_message(f"<@{ctx.author.id}> {tag} four SC with /gamble!", channel_id=[general], ephemeral=False)
    elif flip == 2:
        tag = "won"
        players = await getplayerdata()
        players[str(ctx.author.id)]["SC"] = players[str(ctx.author.id)]["SC"] +4
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
        await ctx.send(f"<@{ctx.author.id}> rolled loins!", ephemeral=True)
        await send_message(f"<@{ctx.author.id}> {tag} four SC with /gamble!", channel_id=[general], ephemeral=False)

button5sc = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="5 SC",
    custom_id="button5sc",
)

@bot.component("button5sc")
async def button_response(ctx):
    flip =  int(random.randint(1, 2))
    if flip == 1:
        tag = "lost"
        players = await getplayerdata()
        players[str(ctx.author.id)]["SC"] = players[str(ctx.author.id)]["SC"] -5
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
        await ctx.send(f"<@{ctx.author.id}> rolled ribs!", ephemeral=True)
        await send_message(f"<@{ctx.author.id}> {tag} five SC with /gamble!", channel_id=[general], ephemeral=False)
    elif flip == 2:
        tag = "won"
        players = await getplayerdata()
        players[str(ctx.author.id)]["SC"] = players[str(ctx.author.id)]["SC"] +5
        with open("players.json","w") as f:
            json.dump(players,f, indent=4)
        await ctx.send(f"<@{ctx.author.id}> rolled loins!", ephemeral=True)
        await send_message(f"<@{ctx.author.id}> {tag} five SC with /gamble!", channel_id=[general], ephemeral=False)

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
    await ctx.send(f"What would you like to gamble?", components = row, ephemeral = True)

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
    print(f"\n the target died!")
    user = await interactions.get(bot, interactions.Member, object_id=(ctx.author.id), guild_id=guildid, force='http')
    await send_message(f"<@{ctx.author.id}> died because of quitting!", channel_id=[general])
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
    players[str(ctx.author.id)]["Location"] = "Dead"
    players[str(ctx.author.id)]["HP"] = 0
    with open("players.json","w") as f:
        json.dump(players,f, indent=4)

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
    user = await interactions.get(bot, interactions.Member, object_id=(ctx.author.id), guild_id=guildid, force='http')
    await ctx.send(f"<@{ctx.author.id}> has enabled reminders!", ephemeral = False)
    reminders[str(ctx.author.id)] = {}
    with open("reminders.json","w") as m:
        json.dump(reminders,m, indent=4)

noremindme = interactions.Button(
    style=interactions.ButtonStyle.DANGER,
    label="No, I don't want reminders",
    custom_id="noremindme",
)

@bot.component("noremindme")
async def button_response(ctx):
    await ctx.send(f"You chose to not receive reminders!", ephemeral = True)
    reminders = await getreminderdata()
    reminders.pop(str(ctx.author.id), None)
    with open("reminders.json","w") as m:
        json.dump(reminders,m, indent=4)


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
    hpmoji = await hpmojiconv(hp_pull)
    status = interactions.api.models.message.Embed(
        title = "Status",
        color = 0xf00c5f,
        fields = [interactions.EmbedField(name="HP",value=hpmoji),interactions.EmbedField(name="Mana",value=manamoji,inline=True),interactions.EmbedField(name="Next Mana",value=mana_date,inline=True),interactions.EmbedField(name="Location",value=location_pull),interactions.EmbedField(name=":fire:Rage",value=Rage_pull,inline=True),interactions.EmbedField(name=":coin:SC",value=SC_pull,inline=True),interactions.EmbedField(name=":school_satchel:Ready Inventory",value=ReadyInventory_pull),interactions.EmbedField(name=":shield:Equipped Inventory",value=EquippedInventory_pull,inline=True),interactions.EmbedField(name=":alarm_clock:Next Action:",value=displayaction)],
    )
    await ctx.send(embeds=status,ephemeral=True)

#travelto
async def dotravel(authorid,destination):
    await rage(authorid)
    players = await getplayerdata()
    current_time = int(time.time())
    user = await interactions.get(bot, interactions.Member, object_id=authorid, guild_id=guildid, force='http')
    if players[str(authorid)]["Location"] == "Crossroads" or destination == "Crossroads":
        players[str(authorid)]["Mana"] = players[str(authorid)]["Mana"] -1
        players[str(authorid)]["Lastaction"] = "travelto"
        players[str(authorid)]["Location"] = destination
        players[str(authorid)]["Nextaction"] = ""
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
        await send_message(f"<@{authorid}> traveled to {destination}! ",channel_id=[locations[destination]["Channel_ID"]])
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
            await ctx.send(f"You aren't in the Crossroads! You must travel to the Crossroads before you travel to another location!", components = row, ephemeral = True)
        else:
            row = interactions.spread_to_rows(traveltodungeonbutton, traveltofarmlandbutton, traveltokeepbutton, traveltolichcastlebutton, traveltoshopbutton, traveltotavernbutton)
            await ctx.send(f"Where would you like to travel to?", components = row, ephemeral = True)
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
        await ctx.send(f"You travel!\n\nSubmit another command!",ephemeral=True)
        if Mana_pull - cost > 0:
            manamoji = await manamojiconv(Mana_pull - cost)
            await ctx.send(f"You have {manamoji} mana remaining",ephemeral=True)
        else :
            await ctx.send(f"Your next action will be queued.",ephemeral=True)
        await dotravelto(ctx.author.id,destination)

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
        await ctx.send(f"You travel!\n\nSubmit another command!",ephemeral=True)
        if Mana_pull - cost > 0:
            manamoji = await manamojiconv(Mana_pull - cost)
            await ctx.send(f"You have {manamoji} mana remaining",ephemeral=True)
        else :
            await ctx.send(f"Your next action will be queued.",ephemeral=True)
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
        await ctx.send(f"You travel!\n\nSubmit another command!",ephemeral=True)
        if Mana_pull - cost > 0:
            manamoji = await manamojiconv(Mana_pull - cost)
            await ctx.send(f"You have {manamoji} mana remaining",ephemeral=True)
        else :
            await ctx.send(f"Your next action will be queued.",ephemeral=True)
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
        await ctx.send(f"You travel!\n\nSubmit another command!",ephemeral=True)
        if Mana_pull - cost > 0:
            manamoji = await manamojiconv(Mana_pull - cost)
            await ctx.send(f"You have {manamoji} mana remaining",ephemeral=True)
        else :
            await ctx.send(f"Your next action will be queued.",ephemeral=True)
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
        await ctx.send(f"You travel!\n\nSubmit another command!",ephemeral=True)
        if Mana_pull - cost > 0:
            manamoji = await manamojiconv(Mana_pull - cost)
            await ctx.send(f"You have {manamoji} mana remaining",ephemeral=True)
        else :
            await ctx.send(f"Your next action will be queued.",ephemeral=True)
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
        await ctx.send(f"You travel!\n\nSubmit another command!",ephemeral=True)
        if Mana_pull - cost > 0:
            manamoji = await manamojiconv(Mana_pull - cost)
            await ctx.send(f"You have {manamoji} mana remaining",ephemeral=True)
        else :
            await ctx.send(f"Your next action will be queued.",ephemeral=True)
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
        await ctx.send(f"You travel!\n\nSubmit another command!",ephemeral=True)
        if Mana_pull - cost > 0:
            manamoji = await manamojiconv(Mana_pull - cost)
            await ctx.send(f"You have {manamoji} mana remaining",ephemeral=True)
        else :
            await ctx.send(f"Your next action will be queued.",ephemeral=True)
        await dotravel(ctx.author.id,destination)

@bot.command(name="paginatortest", description="Paginator testing")
async def paginator_test(ctx: interactions.CommandContext):
    players = await getplayerdata()
    LocationPull = players[str(ctx.author.id)]["Location"]
    sameLocationUserIDs = {k: v for k, v in players.items() if v['Location'] == LocationPull}
    sameLocationUsernames = [v["Username"] for v in players.values() if v['Location'] == LocationPull]
    items = sameLocationUsernames
    lenitems = len(items)
    Content1 = "Player targets 1 to "+str(min(lenitems,25))
    Content2 = "Player targets 25 to "+str(min(lenitems,50))
    Content3 = "Player targets 50 to "+str(min(lenitems,75))
    Content4 = "Player targets 75 to "+str(min(lenitems,100))
    Content4 = "Player targets 100 to "+str(min(lenitems,125))
    Content5 = "Player targets 125 to "+str(min(lenitems,150))
    await Paginator(
        client=bot,
        ctx=ctx,
        pages=[
            Page(Content1, interactions.Embed(title="One")),
            Page(Content2, interactions.Embed(title="Two")),
            Page(Content3, interactions.Embed(title="One")),
            Page(Content4, interactions.Embed(title="Two")),
            Page(Content5, interactions.Embed(title="Two")),
            Page(embeds=[interactions.Embed(title="Four"), interactions.Embed(title="Five")]),
        ],
    ).run()


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
                'drinkingchallenge': dodrinkingchallenge,
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
                'trade':dotrade}



bot.start ()

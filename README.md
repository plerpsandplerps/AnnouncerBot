# AnnouncerBot
Announcer Bot for a rpg minigame!

Everybody starts with 10,000 hp and 10 Seed Coins (SC) (+ any previous bounties earned) in the Crossroads location!

## Ligma
When the game begins a 7-day timer starts and a random location is chosen. When the timer ends, a ligma outbreak occurs at the location. The ligma damage at the random location increases by 250. Then each location does damage to each player inside equal to its own ligma damage.

Finally, a new location is chosen at random and the timer is restarted with 10% less time.

## Rage
Whenever you take an action, you heal equal to your rage*420. Then you lose one rage.

## Bounties
When you kill a player with an attack or interrupt, you gain Seed Coins equal to their Bounty Reward!

You may increase a player's Bounty Reward by spending a coin with the /bounty command.

## Actions
Actions are what you do! Most actions cost mana. You generate one mana every 16 hours and can hold up to three mana at a time. Players can't take actions that would make their mana negative.
When you attempt to perform an action but don't have enough mana, you instead queue the action. You perform that action when you have enough mana.

### Light Attack `/lightattack` 
Spend 1 mana to gain a Rage and attack an opponent in your area for 800 to 1100 damage.
### Heavy Attack `/heavyattack` 
Spend 3 mana to gain 6 Rage and attack an opponent in your area for 3500 to 3800 damage.
### Interrupt `/interrupt` 
Spend 1 mana to attack an opponent in your area for 4200 damage if they are resting or evading. They stop resting/evading. The target loses all queued actions, regardless of whether they were resting/evading or not.
### Evade `/evade` 
Spend 1 mana to receive no damage from light or heavy attacks while you are evading. You are evading for the next 24 hours. 
You can still take actions while evading, but you are susceptible to interrupt damage.
### Rest `/rest`
Gain a mana and heal half your missing health rounded up. You are resting for the next 24 hours and cannot rest while you are resting.
You can still take actions while resting, but you are susceptible to interrupt damage.
### Recruit `/recruit`
Choose a player.
If you choose yourself and you belong to a team, you may leave your current team by spending a mana.
If you choose yourself and you don't belong to a team, you may create and join your own team by spending a mana.
If you choose another player, they may join your team by spending a mana.

*Players with the same team as you are not opponents and therefore cannot be targeted by attacks or interrupts.*
### Gamble `/gamble`
Wager your health or SC on a 50/50 chance. If you lose the 50/50, you lose that much SC/HP. If you win the 50/50, you gain that much SC/HP!

*This does not cost mana.*

### Status `/status`
Use /status to find out more information about your current status.

*Checking your status does not cost mana!*

## Locations `/travel`
You can travel from any location to the Crossroads using /travel and you can travel from the Crossroads to any location using /travel

Locations each have their own unique location action! Location actions cost 1 mana, but have a variety of effects.

### Crossroads `/exchange`
Spend 1 mana to give a player in your area a ready item from your inventory.

### Dungeon `/loot`
Spend 1 mana to roll 1d4. If you roll the highest roll, gain a random item. If you roll the lowest roll, lose 1/4 of your current health. Scores expire after 16 hours.

### Farmland `/farm`
Spend 1 mana to roll 1d4. Gain the result of that roll in SCs.

### Keep `/aid`
Spend 1 mana to heal the chosen player for 1/4 of their missing health.

### Lich's Castle `/battlelich`
Spend 1 mana to roll 1d4. If you get the high roll, gain the lich's item. If you roll the low roll, lose 1/4 of your current health. Scores expire after 16 hours.

### Shop `/trade`
Spend 1 mana to exchange seed coins for a shop item.

### Tavern `/drink`
Spend 1 mana to roll 1d4. If you get the high roll, gain a drinking medal in your equipped inventory. If you roll the low roll, lose 1/4 of your current health. If you don't roll the low roll, heal for 1/4 of your missing health. Scores expire after 16 hours.

## Items `/use`
Items are either in your:
**Ready Inventory**
Items you can use with /use to equip or consume.

**Equipped Inventory**
Items you have equipped in the past that are giving you a passive effect.

### Adventuring Gear (5 SC)
Spend 2 mana to equip this item. Increase your /loot rolls by 1 for each equipped Adventuring Gear.

### AWP (8 SC)
Spend 3 mana to equip this item. While you have an AWP equipped reduce the heavy attack mana cost to two. Doesn't stack.

### Crooked Abacus (5 SC)
Spend 2 mana to equip this item. When you /trade or /exchange gain a SC for each Crooked Abacus you have equipped.

### Goodie Bag (6 SC)
Spend 1 mana to consume this item and add a random item to your ready inventory.

### Tractor (5 SC)
Spend 2 mana to equip this item. When you farm gain a SC for each Tractor you have equipped.

### Drinking Medal (6 SC)
Spend 2 mana to equip this item. When you light attack increase the attack damage by 420 for each Drinking Medal you have equipped.

### Lich's Item (15 SC)
Spend 2 mana to equip this item. The next time you would die, prevent that death and lose an equipped Lich Item instead. This prevention sets your HP to 4200.

### Critter? I Hardly Know Her (6 SC)
Spend 2 mana to equip this item. When you roll for crit add one to your roll for each Critter? I hardly Know her you have equipped.

*(Crit rolls are made on a 1d10, rolls >=10 deal 50% extra damage)*

### Beer-bandolier (3 SC)
Spend 1 mana to consume this item and gain three rage.

### Local Ligma Outbreak (5 SC)
Spend 2 mana to consume this item and deal the current ligma damage at this location to everyone in your area (including yourself).

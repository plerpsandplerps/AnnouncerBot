# AnnouncerBot
Announcer Bot for yearly games!

Everybody starts with 10,000 hp and 10 Seed Coins (SC) (+ any previous bounties earned) in the Crossroads location!

## Poison
- A 14 day poison timer starts and the poison damage is set to zero when the bot launches.
- Whenever the poison timer ends, the poison damage increases by 100 and every player is damaged by the poison.
- Then the poison timer restarts with 25% less time. (See the image below for the poison damage over time)

https://imgur.com/a/9GK6UBP

## Actions
- Actions are what players do!
- To get started take the /join action!
- Most actions have a cooldown (such as 24h). That place the player on cooldown for the duration. The player can't take any actions with a cooldown until they are off cooldown.
- The core actions are listed below.
### Light Attack
  - /lightattack
    - 24h. attack a player in your area for 950.
### Normal Attack
  - /normalattack
    - 48h. attack a player in your area for 2300.
### Heavy Attack
  - /heavyattack
    - 72h. attack a player in your area for 3650.
### Interrupt
  - /interrupt
    - 24h. hit a player in your area for 4200 if they are resting or evading.
### Evade
  - /evade
    - 48h. receive no damage from light normal or heavy attacks.
### Rest
  - /rest
    - 48h. heal half your missing health rounded up.
### Area Action
  - see below for commands
    - 24h. see the area actions listed alongside the locations below.
### Use Item
  - see below for commands
    - Varies-h. see the items listed below.  

## Locations
- Every location has a location specific action
- You can travel from any location to the Crossroads (/traveltocrossroads)
- You can only travel from the Crossroads to any other location (/travelto)

### Crossroads
- /exchange
  - 24h. give a player in your area a ready item from your inventory.

### Dungeon
  - /loot
    - 24h. score 1d4. on 4+ gain two items at random. lowest score: lose 1/4 of your current health.

### Farmland
  - /farm
    - 24h. score 1d4. gain your score seed coins.

### Keep
  - /aid
    - 24h. score 1d4. high score: heal chosen player 1/4 of their missing health.

### Lich's Castle
  - /battlelich
    - 24h. score 1d4. high score of 5+: gain Lich's Item. low score: lose 1/4 current health.

### Shop
  - /trade
    - 24h. exchange seed coins for a shop item.

### Tavern
  - /drinkingchallenge
    - 24h. score 1d4. high score: gain a ready drinking challenge medal: see shop items. low score: lose 1/4 current health.

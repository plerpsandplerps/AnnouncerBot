# AnnouncerBot
Announcer Bot for a rpg minigame!

Everybody starts with 10,000 hp and 10 Seed Coins (SC) (+ any previous bounties earned) in the Crossroads location!

## Actions
- Actions are what players do!
- To get started take the /join action!
- Most actions place players on a cooldown (such as 24h). The player can't take any actions that would place them on cooldown until they are off cooldown.
- When you attempt to perform an action and you are on cooldown, you will instead queue that action. The bot will make you perform that action after you are off cooldown.
- The core actions are listed below:
### Join
  - /Join
    - Join the game!
### Light Attack
  - /lightattack
    - 24h.1rage. attack a player in your area for 950.
### Normal Attack
  - /normalattack
    - 48h.3rage. attack a player in your area for 2300.
### Heavy Attack
  - /heavyattack
    - 72h.6rage. attack a player in your area for 3650.
### Interrupt
  - /interrupt
    - 24h. hit a player in your area for 4200 if they are resting or evading.
### Evade
  - /evade
    - 24h. receive no damage from light normal or heavy attacks.
### Rest
  - /rest
    - 24h. heal half your missing health rounded up unless you rested last action.
### Area Action
  - see below for commands
    - 24h. see the area actions listed alongside the locations below.
### Use Item
  - see below for commands
    - Varies-h. see the items listed below.  

## Locations
- Every location has a location specific action
- You can travel from any location to the Crossroads (/traveltocrossroads)
- You can only travel to locations other than the Crossroads, from the Crossroads (/travelto)

### Crossroads
- /exchange
  - 24h. give a player in your area a ready item from your inventory.

### Dungeon
  - /loot
    - 24h. score 1d4. on 4+ gain two items at random. lowest score: lose 1/4 of your current health.
    - not live

### Farmland
  - /farm
    - 24h. score 1d4. gain your score seed coins.

### Keep
  - /aid
    - 24h. heal chosen player 1/4 of their missing health.

### Lich's Castle
  - /battlelich
    - 24h. score 1d4. high score of 5+: gain Lich's Item. low score: lose 1/4 current health.

### Shop
  - /trade
    - 24h. exchange seed coins for a shop item.

### Tavern
  - /drinkingchallenge
    - 24h. score 1d4. high score: gain a used drinking challenge medal. low score: loses 1/4 current health otherwise: heal 1/4 missing health.

## Items
- Items fall into two broad categories:
  - Ready items
    - Items you can use for benefits that can be instantaneous, duration, or permanent in nature.
    - When you use a Ready Item it moves to your Used Items.
  - Used items
    - Items you have used in the past that may or may not be providing you a benefit.
- The list of items is below.

### Adventuring Gear
  - /adventuringgear
    - 48h. increase your loot score by 1 for the rest of the game.

### Aim Training
  - /aimtrain
    - 72h. reduce heavy attacks to 24h cooldown. doesn't stack.

### Banish
  - /banish
    - 24h. choose a player in your area and an area. the chosen player travels to the chosen area.
    - not live

### Crooked Abacus
  - /crookedabacus
    - 48h. whenever you exchange or trade, gain a seed coin for the rest of the game.

### Goodie Bag
  - /goodiebag
    - 24h. add a random ready item to your inventory.

### Tractor
  - /tractor
    - 48h. whenever you farm, gain an additional seed coin for the rest of the game.

### Drinking Medal
  - /drinkingmedal
    - 48h. increase the damage of your light attack by 420 for the rest of the game.

### Lich's Item
  - /lichitem
    - 24h. set target player's HP to 4200. if the target is dead, resurrect them.

### Beer-bandolier
  - /beerbando
    - 24h. you gain three rage.

## Poison
- A 7 day poison timer starts and the poison damage is set to 650 when the bot launches.
- Whenever the poison timer ends, the poison damage increases by 100 and every player is damaged by the poison.
- Then the poison timer restarts with 10% less time.

## Rage
- Whenever you take an action, you heal equal to your rage*420. Then you lose one rage.

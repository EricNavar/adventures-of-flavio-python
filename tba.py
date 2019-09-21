iteimport random
import math
import operator

#=====monster======
class Monster:
    def __init__(self, name, boss, description, attacks, loot, xp, weakness, resistance, current_stats, base_stats):
        self.name = name
        self.boss = boss
        self.description = description
        self.attacks = attacks
        self.loot = loot
        self.xp = xp #how much xp you get for defeating it
        self.weakness = weakness
        self.resistance = resistance
        self.current_stats = current_stats#energy, sp, buff, status, and last_attack
        self.base_stats = base_stats
    
    def decide_attack(self, heroes, monsters): #monster, decides both attack and target
      possible_attacks = []
      for attack in self.attacks:
        if attack.sp <= self.current_stats["sp"]:
          possible_attacks.append(attack)
      num = random.randint(0,2)
      if num == 0:
        self.current_stats["next attack"] = normal_attack
      else:
        self.current_stats["next attack"] = random.choice(possible_attacks)
      next_attack = (self.current_stats["next attack"])
      if next_attack.targets == "foe":
        #decide target. If target is foe, one of the following has a 1 in 3 chance of occuring: weakest hero is attacked, hero with status effect is attacked, or random hero is attacked. If none have a status effect, the weakest is attacked.
        possible_targets = []
        afflicted_targets = [] #heroes with a status effect
        for hero in heroes:
          if hero.current_stats["status"] != "dead":
            possible_targets.append(hero)
          if hero.current_stats["status"] != "dead" or None:
            afflicted_targets.append(hero)
        x = random.randint (0,2)
        if x == 0:
          self.current_stats["next attack target"] = random.choice(possible_targets)
        if x == 1:
          if len(afflicted_targets) > 1:
            self.current_stats["next attack target"] = random.choice(afflicted_targets)
          else: x = 2
        if x == 2:
          weakest_hero = [[None, 1.1]]
          for hero in heroes:
            energy_ratio = hero.current_stats["energy"] / float(hero.base_stats["energy"])
            if energy_ratio < weakest_hero[0][1]:
              del weakest_hero[:]
              weakest_hero.append([hero, energy_ratio])
            elif energy_ratio == weakest_hero[0][1]:
              weakest_hero.append([hero, energy_ratio])
          self.current_stats["next attack target"] = random.choice(weakest_hero)[0]
      
      elif next_attack.targets == "ally":
        possible_targets = []
        for monster in monsters:
          if monster.name != self.name:
            possible_targets.append(monster)
        self.current_stats["next attack target"] = random.choice(possible_targets)
      elif next_attack.targets == "all foes":
        self.current_stats["next attack target"] = monsters
      elif next_attack.targets == "self":
        self.current_stats["next attack target"] = self
      elif next_attack.targets == "party":
        self.current_stats["next attack target"] = heroes
      else:
        print ("Debug. This should never print.")
    
    def attack(self, hero): #monster
      if self.current_stats["energy"] == 0:
        return False
      move = self.current_stats["next attack"]
      print ("The %s uses %s on %s." % (self.name, move.name, hero.name))
      damage = math.ceil((move.power * self.base_stats["power"] / hero.base_stats["defence"]))
      if not random.randint(0,5):
        damage = int(damage * 1.5)
        print ("Critical hit!")
      hero.change_energy_sp(-damage, "energy")
      self.current_stats["sp"] -= move.sp
  
  
#==========================================================================
#HERO======================================================================
#==========================================================================


class Hero:
    potion = False #using potion?
    inventory = []
    key_inventory = [] #for key items
    money = 0
    registry = [] # list of class objects
    def __init__(self, name, attacks, equipped, current_stats, base_stats):
        #self.registry.append(self)
        self.name = name
        self.attacks = attacks
        self.equipped = equipped
        self.current_stats = current_stats
        self.base_stats = base_stats
        
    def use_item(self, item):
      if item.type_ == "consumable":
        for key in item.bonus:
          if key == "status":
            self.current_stats["status"] -= item.bonus[key]
          else:
            new_stat = min(max(item.bonus[key] + self.current_stats[key],0),self.base_stats[key])
            change = new_stat - self.current_stats[key]
            Hero.inventory.remove(item)
            if change == 0:
              print ("%s %s is full!" % (self.name, key))
            else:
              print ("%s used the %s." % (self.name, item.name))
              self.change_energy_sp(change, key)
              Hero.inventory.remove(item)
              
      else:
        if len(self.equipped) == 4:
          print ("You can only equip four items.")
        else: 
          flag = True
          for equip in self.equipped:
            if equip.part == item.part:
              flag = False
          if flag == True:
            print ("%s equipped the %s." % (self.name, item.name))
            Hero.inventory.remove(item)
            self.equipped.append(item)
          else:
            print ("You can only equip one %s." % (item.part))
            

    def change_energy_sp(self, change, stat):
        if change > 0:
          print ("%s gained %s %s." % (self.name, str(change), stat))
        else:
          print ("%s lost %s %s." % (self.name, str(abs(change)), stat))
        self.current_stats[stat] = max( min(self.current_stats[stat] + change, self.base_stats[stat]), 0)
        if self.current_stats["energy"] <= 0:
          self.current_stats["status"] = "dead"
        
    def addBonus(self, item, show):
        for key in item.bonus:
          self.base_stats[key] += item.bonus[key]
          if show == True:
            print ("%s's %s grew by %s!" % (self.name, key, item.bonus[key]))
    
    def add_to_inventory(self, item):
      if item.type_ == "key":
        Hero.key_inventory.append(item)
      if len(Hero.inventory) < 100:
        Hero.inventory.append(item)
        print ("You added " + item.name + " to the inventory.")
      else:
        print ("You have too many items in your possession.")
      
    def changeMoney(self, amount):
      if amount > 0:
        print ("You recieved %s gold coins" % (amount))
        
      else:
        ("You turned over %s gold coins" % (amount))
    
    def add_xp(self,xp):
      Flavio.current_stats["xp"] += xp
      if self.current_stats["xp"] >= self.base_stats["max_xp"]:
        leftover = self.current_stats["xp"] - self.base_stats["max_xp"]
        self.current_stats["xp"] = 0
        self.base_stats["max_xp"] = int(pow(self.base_stats["max_xp"], 1.1))
        self.add_xp(leftover)
        self.base_stats["lvl"] += 1
        print ("%s's grew to level %s!" % (self.name, self.base_stats["lvl"]))
        
    def display_stats(self):
      print ("Energy: " + str(self.current_stats["energy"]) + "/" + str(self.base_stats["energy"]))
      print ("SP: " + str(self.current_stats["sp"]) + "/" + str(self.base_stats["sp"]))
      print ("power: " + str(self.base_stats["power"]))
      print ("defence: " + str(self.base_stats["defence"])) 
      print ("speed: " + str(self.base_stats["speed"])) 
      print ("Money: " + str(self.money))
      print ("XP: " + str(self.current_stats["xp"]))
      print ("XP to level up: " + str(self.base_stats["max_xp"] - self.current_stats["sp"]))
      print ("Energy: " + str(self.base_stats["lvl"])) 
      
      user_input = input()
      if "exit" in user_input:
        print ("Exiting stats")
        return True
    
    def display_gear(self):
      for hero in Hero.registry:
        print (hero.name + ":")
        for item in hero.equipped[0:len(hero.equipped)-1]:
          print (item.name, end = ", ")
        print (hero.equipped[-1].name)
      user_input = input()
      if "remove " in user_input:
        user_input = user_input.replace("remove ", "")
        for item in hero.equipped:
          if item.name == user_input:
            hero.equipped.remove(item)
            hero.inventory.append(item)
            print ("%s unequipped %s." % (hero.name, item.name))
            break
        else:
          print ("That item is not equipped.")
      elif "exit" in user_input:
        print ("Exiting gear")
        return True 
    
    def run(self, foes):
      if smoke_bomb in self.inventory:
          print ("You got away safely!")
          return True
      if foes[0].boss == False: 
        if random.randint(0,1):
          print ("You got away safely!")
          return True
        else:
          print ("You couldn't get away!")
          return False
      else:  
          print ("You can't run away, you coward.\n")
    
    def decide_attack(self, foes): #hero
      for attack in self.attacks[1:len(self.attacks)-1]:
        print (attack.name, end = ", ")
      print (self.attacks[-1].name)
      while True:
        user_input = input("Which skill will %s use?" % (self.name))
        for attack in self.attacks[1:len(self.attacks)]:
          if user_input == attack.name:
            if attack.sp > self.current_stats["sp"]:
              print ("You do not have enough sp for that move.")
              break
            else:
              self.decide_target(attack, foes)
              return True
        else:
            print ("That is not an attack.")
            continue
    
    def decide_target(self, move, foes): #hero
      self.current_stats["next attack"] = move
      if move.targets == "foe":
        if len(foes) == 1:
          self.current_stats["next attack target"] = foes[0]
          return
        flag2 = False
        while flag2 == False:
          user_input = input("Which foe will you attack?")
          for foe in foes:
            if user_input == foe.name:
              self.current_stats["next attack target"] = foe
              flag2 = True
          else: 
            if flag2 == False:
              print ("That is not a foe.")
      elif move.targets == "ally":
        possible_targets = []
        for member in self.registry:
          if member.name != self.name:
            possible_targets.append(member)
        while True:
          user_input = input("Which ally will you help?")
          for hero in possible_targets:
            self.current_stats["next attack target"] = hero
            #flag2 = True
            return
          else: 
            #if flag2 == False:
              print ("That is not an ally.")
              continue
      elif move.targets == "all foes":
        self.current_stats["next attack target"] = foes
      elif move.targets == "self":
        self.current_stats["next attack target"] = self
      elif move.targets == "party":
        self.current_stats["next target attack"] = self.registry
      else:
        print ("Debug. This should never print.")

    def attack(self, foe): #HERO
      if self.current_stats["energy"] == 0:
        return False
      move = self.current_stats["next attack"]
      print ("%s %s the %s." % (self.name, move.name, foe.name))
      modifier = 1
      if move.element in foe.weakness:
        modifier *= 2
      if move.element in foe.resistance:
        modifier *= .5
      damage = math.ceil((move.power * self.base_stats["power"] *  modifier/ foe.base_stats["defence"]**2 ))
      if not random.randint(0,5):
        damage*=2
        print ("Critical hit!")
      print ("The " + foe.name+ " lost " + str(damage) + " energy!")
      foe.current_stats["energy"] = min(max(foe.current_stats["energy"] - damage, 0),self.base_stats["energy"])
      self.current_stats["boost"] += 10
      self.current_stats["sp"] -= move.sp
      if foe.current_stats["energy"] <= 0:
        foe.current_stats["status"] = "dead"
        print ("You killed the " + foe.name + "!")
        

class npc:
    def __init__(self, item, greeting, goodbye, first_talk):
        self.item = item
        self.greeting = greeting
        self.goodbye = goodbye
        self.first_talk = first_talk #T/F: first time he has been talked to?
    
    def talk_with(self, hero): #hero is the guy talking to the npc
      print (self.greeting)
      end_conversation = False
      while end_conversation == False:
        user_input = input()
        if self.first_talk == False:
            print ("Here, take this money to aid you with your mission.")
            hero.changeMoney(100)
            self.first_talk = False
            print (self.goodbye)
            end_conversation = True
        elif ("hi" or "hello") in user_input:
          print (self.greeting)
        elif ("quest") in user_input:
          print ("Your quest is to ")
        else:
          print ("I don't understand.")

class item:
  def __init__(self, name, type_, bonus, part, price):
    self.name = name
    self.type_ = type_ #consumable? equippable?
    self.bonus = bonus # if item is equippable, it gives these stats a bonus
    self.part = part # if item is equippable, it goes on this body part
    self.price = price

class move:
  def __init__(self, name, description, power, element, type_, targets, effect, sp, priority):
    self.name = name
    self.description = description
    #self.battle_text = battle_text #what will show up in battle when someone uses the move 
    self.power = power
    self.element = element
    self.type_ = type_ #physical, status?
    self.targets = targets #will it attack multiple enemies, all, or one?
    self.effect = effect #will it paralyze?
    self.sp = sp #sp cost
    self.priority = priority
  
  def delayed_charge(self, hero, foe):
  	pass
  	
  def revenge_curse(self, hero, foe):
  	pass

  def suicide_curse(self, hero, foe):
    pass

  def razor_edge(self, hero, foe):
    pass

  def charging_slash(self, hero, foe):
    pass

  def nightmare_curse(self, hero, foe):
    pass
    

#GLOBAL FUNCTIONS==================

def global_query(input):
  if "inventory" in input:
    inventory()
    return True
  if "stats" in input:
    for hero in Hero.registry:
      hero.display_stats()
    return True
  if "gear" in input:
    Hero.registry[0].display_gear()
    return True
  if "monsterdex" in input:
    display_monsterdex()
    return True
    
def inventory():
  print ("  Inventory:")
  inventory2 = list(set(Hero.inventory))
  for item in inventory2:
    print (item.name + " x" + str(Hero.inventory.count(item)) )
  print ("Which item do you want to use?")
  print ("Exit inventory")
  while True:
    user_input = input()
    if "exit" in user_input:
      print ("Exiting inventory")
      return True 
    for i in Hero.inventory:
      if user_input == i.name:
        Flavio.use_item(i)
        print ("Exiting inventory")
        return True
    else:
        print ("That item is not in the inventory.")

def display_monsterdex():
  counter = 1
  for monster in monsterdex:
    print (counter, end = ": ")
    if monsterdex[monster] == "unseen":
      print ("????")
    else:
      print (monster.name)
    counter += 1


#=========AREAS==========
def scene1(been_here): #BEACH
  sceneEnd = False
  if been_here==False:
    print ("You wake up on the beach feeling waves at your feet. You quickly sit up wondering where you are. There is no boat nearby or sign of life nearby. You can go south further into the island.")
  if been_here==True:
    print("You come across the beach here you woke up. There's nothing but sand the beach. What are you still doing here?")
  while sceneEnd == False:
    user_input = input()
    print ("")
    if global_query(user_input):
      continue
    if "south" in user_input:
      sceneEnd = True
      scene2()
    elif "debug" in user_input:
        battle(Hero.registry, [golem])
    else: 
      print ("Invalid input. You can only go south.")

def scene2(): #Town
  sceneEnd = False
  print ("You walk into town. Everyone in town knows you for being the best soldier in the kingdom. There's a shop. Mount Kilea is to the east, the beach is north, and the castle is a little further south.")
  while sceneEnd == False:
    user_input = input()
    print ("")
    if global_query(user_input):
      continue
    if "south" in user_input:
      sceneEnd = True
      scene7()
    elif "east" in user_input:
      sceneEnd = True
      scene3(2)
    elif "north" in user_input:
      sceneEnd = True
      scene1(True)
    elif "shop" in user_input:
      sceneEnd = True
      scene6()
    else:
      print ("Invalid input. Go south, east, north, or go to potion shop.")

def scene3(prev_loc): #OUTSIDE OF VOLCANO
  sceneEnd = False
  potion = None
  if prev_loc == 2:
    print ("You reach the base of Mount Kilea. It's home to many flame monsters. It's steep, but you can climb it.")
    if fire_resistant_potion in Hero.inventory:
      print ("Take the potion. Go to inventory to take it.")
    else:
      print ("You can't go inside. You need a fire-resistant spell to survive the temperature.")
  elif prev_loc == 4:
    print ("You climb out the mountain. The town is to the west.")

  while sceneEnd == False:
    user_input = input()
    print ("")
    if global_query(user_input):
      continue
    if ("in" or "down") in user_input:
      if Hero.potion == True:
        sceneEnd = True
        scene4(3)
      if Hero.potion == False:
        print ("You need the fire-resistant potion to go inside the volcano.")
    elif "west" in user_input:
      sceneEnd = True
      scene2()
    else:
      print ("Invalid input. Go in or go west.")

def scene4(prev_loc): #INSIDE VOLCANO
  sceneEnd = False
  if prev_loc == 3:  
    print ("You climb down the mountain, resting on a ledge every few minutes. You reach a network of bridges passing over pools of lava. You see a fortress built along the wall of the inside of the volcano. The life gem must be there. You reach a cave entrance leading to the fortress.")
  elif prev_loc == 5:
    print ("You walk out of the tunnel and cross the bridges over the rivers of lava and reach the base of the wall of the inside of the volcano.")
  while sceneEnd == False:
    user_input = input()
    print ("")
    if global_query(user_input):
      continue
    if ("out" or "leave") in user_input:
      if life_gem in Hero.inventory:
        sceneEnd = True
        scene3_1()
      else:
        sceneEnd = True
        scene3(4)
    elif "in" in user_input:
      sceneEnd = True
      scene5()
    else:
      print ("Invalid input. Go in or go out.")

def scene5(): #FORTRESS
  sceneEnd = False
  print ("You walk into a tunnel which leads into a giant cave. The entance to the fortress is close. A flame monster guards the entrance. He's ten feet tall with a rocky body with a head and four legs made of fire.")
  while sceneEnd == False:
    user_input = input()
    print ("")
    if global_query(user_input):
      continue
    if ("leave" or "out") in user_input:
      sceneEnd = True
      scene4(5)
    elif "fight" in user_input:
      battle(Hero.registry, flame_monster)
      Hero.registry[0].add_to_inventory(life_gem)
      print ("You have the life gem. Go kill the dragon.")
      
    else:
      print ("Invalid input. Leave or fight like a true Hero.")
      
    
def scene6(): # SHOP
  sceneEnd = False
  print ("You walk into the shop. \"Buy something, will ya?\"")
  for item in shop_items:
    #print ("%s: %s coins" % (item.name, item.price))
    print (item.name + ": ", end = "")
    print (str(item.price).rjust(25 - len(item.name)))
  while sceneEnd == False:
    user_input = input()
    print ("")
    if global_query(user_input):
      continue
    if "leave" in user_input:
      sceneEnd = True
      scene2()
    a = False
    for item in shop_items:
      if user_input == item.name:
        a = True
        if Hero.money >= item.price:
          Hero.registry[0].add_to_inventory(item)
        else:
          print ("You don't have enough money!")
    if a == False:
      print ("Invalid input. Buy or leave.")
  
def scene7(): #CASTLE
  sceneEnd = False
  print ("You arrive at the castle. It looks like the King has been waiting for you. Ask him your quest.")
  while sceneEnd == False:
    user_input = input()
    print ("")
    if global_query(user_input):
      continue
    if ("talk" or "King") in user_input:
      king.talk_with(Hero.registry[0])
    elif ("leave" or "north") in user_input:
      sceneEnd = True
      scene2()
    else:
      print ("Invalid input. Leave or Talk to the King.")

def scene3_1(): #OUTSIDE MOUNTAIN 2
  sceneEnd = False
  print ("You climb down the mountain. You hear a roar that shakes the palm trees. You turn around. You look at the ocean where it seems to have come from. From the ocean emerges a massive eel with wings that it uses to crawl onto the shore. It spreads its wings and flies toward town to the west.")
  while sceneEnd == False:
    user_input = input()
    print ("")
    if global_query(user_input):
      continue
    if "west" in user_input:
      sceneEnd = True
      scene2_1()
    else:
      print ("Invalid input. Go west and fight the dragon.")

def scene2_1(): #TOWN 2
  sceneEnd = False
  print ("You run into town and see the dragon. He circling around the town blasting fire at the buildings. You are more powerful from the life gem. Go fight the dragon.")
  while sceneEnd == False:
    user_input = input()
    print ("")
    if global_query(user_input):
      continue
    if "fight" in user_input:
      battle(Flavio, dragon)
      print ("You slayed the dragon! You win!")
    else:
      print ("Invalid input. Fight the dragon.")
      
#=========combat=============
def battle(heroes, foes): # heroes and foes are a list
  battle_end = False
  turn = 1
  for foe in foes: #adds foe into monsterdex
    if monsterdex[foe] == "unseen":
      monsterdex[foe] = "seen"
  combatants = foes + heroes
  attack_order = get_attack_order(combatants)
  if len(foes) == 1:
    print ("A " + foes[0].name.lower() + " appeared!")
  while battle_end == False:
    #PRINT HP AND SP
    print ("")
    for foe in foes:
      print (foe.name, end = ":")
      string = str(foe.current_stats["energy"])
      print ( string.rjust(20 - len(foe.name) ), end = "" )
      print (">"*int((foe.current_stats["energy"]*10/foe.base_stats["energy"])))
    for hero in heroes:
      print (hero.name, end = ":")
      string = str(hero.current_stats["energy"])
      print ( string.rjust(20 - len(hero.name) ), end = "" )
      print (">"*int((hero.current_stats["energy"]*10/hero.base_stats["energy"])), end = "")
      print ("   SP: %s/%s" % ( str(hero.current_stats["sp"]), str(hero.base_stats["sp"] ) ))
    
    for hero in heroes:
      print ("\nWhat will %s do?" % (hero.name))
      print ("attack\nskills\nitems\nrun")
      flag = False
      while flag == False:
        user_input = input()
        if user_input == "attack":
          hero.decide_target(hero.attacks[0], foes)
          flag = True
        elif user_input == "skills":
          hero.decide_attack(foes)
          flag = True
        elif user_input == "items":
          inventory()
          flag = True
        elif user_input == "run":
          hero.run(foes)
          flag = True
        else:
          print ("That is not an option.")
          continue

    for foe in foes:
      foe.decide_attack(heroes, foes)
    for combatant in combatants:
      if combatant.current_stats["buff"] != None:
        attack_order = get_attack_order(combatants)
        break

    for combatant in attack_order:
      if combatant.attack(combatant.current_stats["next attack target"]) == True:
        battle_end = True
        battle_over(heroes, foes, "ran away")
        break
      
    for hero in heroes:
      flag = False #if flag is true, there is at least one live hero
      if hero.current_stats["energy"] > 0:
        flag = True
    else:
      if flag == False:
        battle_over(heroes, foes, "loss")
        battle_end = True
        
    for foe in foes:
      flag = False #if flag is true, there is at least one live hero
      if foe.current_stats["energy"] > 0:
        flag = True
    else:
      if flag == False:
        battle_over(heroes, foes, "victory")
        battle_end = True
        
    turn += 1
    print ("")
    
def get_attack_order(combatants): #combatants is a list of the heroes and foes in the battle
  attack_order = {}
  for combatant in combatants:
    attack_order[combatant] = combatant.base_stats["speed"]
  attack_order2 = sorted(attack_order.items(), key=operator.itemgetter(1), reverse = True)
  attack_order = list()
  for combatant in attack_order2:
    attack_order.append(combatant[0])
  #print (attack_order)
  return attack_order
        

def battle_over(heroes, foes, outcome): 
  if outcome == "victory":
    xp_earned = 0
    live_heroes = 0
    for foe in foes:
      xp_earned += foe.xp
      foe.current_stats["last attack"] = None
      foe.current_stats["next attack"] = None
      foe.current_stats["next attack"] = None
      foe.current_stats["buff"] = None
      if foe.loot != None:
        heroes[0].add_to_inventory(foe.loot)
    for hero in heroes:
      hero.current_stats["last attack"] = None
      hero.current_stats["next attack"] = None
      foe.current_stats["next attack"] = None
      hero.current_stats["buff"] = None
      if hero.current_stats["status"] != "dead":
        live_heroes += 1
        foe.base_stats["status"] = None
    xp_share = xp_earned / live_heroes # how much xp each hero gets
    for hero in heroes:
      hero.add_xp(xp_share)
    
  if outcome == "loss":
      for foe in foes:
        foe.current_stats["last attack"] = None
        foe.current_stats["next attack"] = None
        foe.current_stats["next attack"] = None
        foe.current_stats["buff"] = None
      print ("Your team has falen...")
      print ("You lost 100 coins.")
      hero[0].money -= 100
      scene1(True)
  
#attack functions
def make_invincible(user):
  pass

#=======================================================================
#INITIALIZATION=========================================================
#=======================================================================

#ITEM INITIALIZATION: name("string"), type_("string"), bonus(dictionary), part(string), price(int)
#fire_resistant_potion = item("fire-resistant potion", "consumable", {}, None, 0)
healing_potion = item("healing potion", "consumable", {"energy": 20}, None, 20)
super_potion = item("super potion", "consumable", {"energy": 50}, None, 100)
#max_potion = item("max potion", "consumable", {"energy": 999}, None, 500)
#antidote = item("antidote", "consumable", {"status": "paralyzed"}, None, 50)
amirita = item("amirita", "consumable", {"sp": 50}, None, 400)# restores sp
#revive_item = item("revive", "consumable", {"status": "dead", "energy": 50}, None, 500)
#max_revive = item("max revive", "consumable", {"status": "dead", "energy": 999}, None, 1000)
#ariadne_thread = item("ariadne thread", "consumable", {}, None, 100)
#soma = item("soma", "consumable", {"energy": 50}, None, 500)#party effect
super_soma = item("super soma", "consumable", {"energy": 100}, None, 1000)#party effect
#hamao = item("hamao", "consumable", {"sp": 50}, None, 600)#party effect
#cake = item("cake", "consumable", {"energy": 200, "sp": 200}, None, 1000) # restores hp and sp
#cookie = item("cookie", "consumable", {"energy": 80, "sp": 80}, None, 500)#restores 1 hp
repel = item("repel", "consumable", {}, None, 250)#restores party hp
divine_gift = item("divine gift", "consumable", {}, None, 1000) # boosts xp recieved for that battle or maybe the next 30 minutes or whatever


  #Battle items, none have bonuses
#smoke_bomb= item("smoke bomb", "battle", {}, None, 0)# guarantees escape except for boss
#analysis_lens = item("analysis lens", "battle", {}, None, 0) #see weakness of enemy
#nerve_gas = item("nerve gas", "battle", {}, None, 0) # might paralyze enemy
#toxic_gas = item("toxic gas", "battle", {}, None, 0) #might poison enemy
#XStrength = item("XStrength", "battle", {}, None, 0) #increases strength for just that battle
#XDefense = item("XDefense", "battle", {}, None, 0) #increases strength for just that battle
#XAccuracy = item("XAccuracy", "battle", {}, None, 0) #increases strength for just that battle

  #equippable (armor and weapons)
#battle_axe = item("battle axe", "equippable", {"power":5}, "weapon", 0)

#wooden_shield = item("wooden shield", "equippable", {"defence":5}, "shield", 200)
iron_shield = item("iron shield", "equippable", {"defence":10}, "shield", 600)
steel_shield = item("steel shield", "equippable", {"defence":15}, "shield", 1200)
#platinum_shield = item("platinum shield", "equippable", {"defence":20}, "shield", 2000)
#crystal_shield = item("crytsal shield", "equippable", {"defence":25}, "shield", 4000)

#steel_armor = item("steel armor", "equippable", {"power":5}, "armor", 200)

  #hold items
#cloak = item("cloak", "hold", {}, False, 0) #increases evasiveness
#leftovers = item("leftovers", "hold", {}, False, 0) #restores 5% of HP every turn
#life_gem = item("life gem", "hold", {"power":30}, True, 0)
#zoom_lens = item("zoom lens", "hold", {}, None, 0)#increases accuracy
ghost_heart = item("ghost heart", "hold", {}, None, 0) #like life orb of pokemon


  #general
#gold_nugget = item("gold nugget", "general", {}, None, 2000) #sell it for money

  #key items



#====================
#MOVES===============
#====================
# = move(name, description, power, element, type_, targets, effect, sp, priority)

#normal_attack = move("attack", "standard attack", 20, None, "physical", "foe", {"effect": "defence", "accuracy": 100, "duration": 1}, 0, 0)

#defend = move("defend", "standard defend", 20, None, "stats", "self", None, 0, 0)

#quick_attack = move("quick attack", "stab an enemy", 40, None, "physical", "foe", None, 0, 1)

#stab = move("stab", "stab an enemy", 40, None, "physical", "foe", None, 4, 1)

#slash = move("slash", "slash with your sword", 30, None, "physical", "foe", None, 3, 0)

#flamethrower = move("flamethrower", "A powerful flame attack. May burn.", 100, "flame", "special", "foe", {"effect": "burn", "accuracy": 15}, 10, 0)

#ice_beam = move("ice beam", "A powerful ice attack. May freeze", 100, "ice", "special", "foe", {"effect": "freeze", "accuracy": 15}, 10, 0)

dark_pulse = move("dark pulse", "A powerful dark attack", 90, None, "special", "foe", None, 9, 0)

#raging_edge = move("razor edge", "A powerful slash attack", 100, None, "physical", "all foes", None, 10, 0)

#front_guard = move("front guard", "raises defence of party at the start of this turn", 1.2, None, "stats", "party", {"effect": "defence", "accuracy": 100}, 6, 1)

parry = move("parry", "May block attacks from whole party. ", None, None, "stats", "party", {"effect": "invincible", "accuracy": 25}, 15, 1)

fortify = move("foortify", "Raises defence of user", 1.5, None, "stats", "self", {"effect": "defence", "accuracy": 100}, 6, 0)

salve = move("salve", "Heals energy for entire party", .5, None, "status", "party", {"effect": "heal", "accuracy": 100}, 20, 0)

#heal = move("heal", "heals half of an ally's energy", 50, None, "status", "ally", {"effect": "heal", "accuracy": 100}, 15, 0)

#revive_move = move("revive", "revives an ally", None, None, "status", "ally", {"effect": "dead", "accuracy": 100}, 20, 0)

#cure = move("curse", "removes an ailment", None, None, "status", "ally", {"effect": "status", "accuracy": 90}, 8, 0)

anesthetic = move("anesthetic", "May make the enemy fall asleep", None, None, "status", "one", {"effect": "sleep", "accuracy": 50}, 8, 0)

#toxin = move("toxin", "May poison the enemy", None, None, "status", "foe", {"effect": "poison", "accuracy": 50}, 8, 0)

curare = move("curare", "May paralyze the enemy", None, None, "status", "foe", {"effect": "paralyze", "accuracy": 50}, 8, 0)

toxic_curse = move("toxin", "May poison all enemies", None, None, "status", "all foes", {"effect": "poison", "accuracy": 25}, 10, 0)

#luring_whisper = move("anesthetic", "May make all enemies asleep", None, None, "status", "all foes", {"effect": "sleep", "accuracy": 25}, 10, 0)

#retaliate = move("retaliate", "retaliates a physical attack with a stronger attack", 1.5, None, "physical", "foe", {"effect": "retaliate", "accuracy": 25}, 15, -1)

#fire_formula = move("fire formula", "A flame attack at one enemy", 70, "flame", "special", "foe", {"effect": "burn", "accuracy": 10}, 8, 0)

#inferno_formula = move("fire formula", "A flame attack at all enemies", 70, "flame", "special", "all foes", {"effect": "burn", "accuracy": 20}, 25, 0)

#ice_formula = move("ic formula", "An ice attack at one enemy", 70, "ice", "special", "foe", {"effect": "freeze", "accuracy": 10}, 8, 0)

#blizzard_formula = move("blizzard formula", "An ice attack at all enemies", 70, "ice", "special", "all foes", {"effect": "freeze", "accuracy": 20}, 20, 0)

#volt_formula = move("volt formula", "A volt attack at one enemy", 70, "volt", "special", "foe", {"effect": "paralyze", "accuracy": 10}, 8, 0)

#thor_formula = move("thor formula", "A volt attack at all enemies", 70, "volt", "special", "all foes", {"effect": "paralyze", "accuracy": 20}, 25, 0)

sapping_curse = move("sapping curse", "absorbs an enemy's power", 80, None, "special", "foe", {"effect": "drain", "accuracy": 100}, 15, 0)

void_curse = move("void curse", "absorbs all enemies' power", 70, None, "special", "all foes", {"effect": "drain", "accuracy": 100}, 25, 0)

#suicide_curse = move("void curse", "doubles power but dies after 3 turns", 2, None, "status", "self", {"effect": "attack", "effect2": "suicide", "accuracy": 100}, 15) #special function

sapping_curse = move("leech curse", "saps enemy's energy every turn", None, None, "status", "foe", {"effect": "drain", "accuracy": 50}, 8, 0)

#revenge_curse = move("revenge curse", "The weaker you are, the more powerful this attack is", (1 - hero.base_stats["energy"] / hero.current_stats["energy"]) * 100, None, "special", "one", None, 10) #revenge curse

blinding_curse = move("blinding curse", "lowers the accuracy of the enemy", None, None, "stat", "foe", {"effect": "accuracy", "accuracy": 100}, 8, 0)

#corrupt_curse = move("corrupt curse", "Can curse an enemy", None, None, None, 1, {"effect": "curse", "accuracy": 50}, 8, 0)

#nightmare_curse = move("corrupt curse", "absorbs energy of sleeping enemies", 90, None, "special", "foe", None, 6, 0)

madness_curse = move("madness curse", "A powerful curse to an enemy. Must recharge the next turn", 150, None, "special", "foe", {"effect": "recharge", "accuracy": 100}, 15, 0)

long_thrust = move("long thrust", "A powerfuul attack to an enemy", 120, None, "physical", "foe", None, 15, 0)

draining_thrust = move("draining thrust", "Sword attack to an enemy. Absorbs some energy taken.", 50, None, "physical", "foe", {"effect": "drain", "accuracy": 100}, 9, 0)

#charging_slash = move("charging slash", description, power, None, "physical", targets, effect)

#beheading_cut = move("beheading cut", "A slice at the enemy's head. May KO.", 50, None, "physical", "f0e", {"effect": "dead", "accuracy": 25}, 10, 0)

#aegis = move("aegis", "The user can be able to survive a KO", power, None, type_, "foe", effect) 

#shield_rush = move("shield rush", "bash attack with shield to all enemies", 60, None, "physical", "all foes", {"effect": "attack", "accuracy": 25}, 20)

#flame_grater = move("flame grater", "elemental sword attack to an enemy. Attacks first.", 55, "flame", "physical", "foe", None, 7, 1)

#lighning_stab = move("lightning stab", "elemental sword attack to an enemy. Attacks first.", 55, "volt", "physical", "foe", None, 7, 1)

#frigid_slash = move("frigid slash", "elemental sword attack to an enemy. Attacks first", 55, "ice", "physical", "foe", None, 7, 1)

#drawing_stance = move("drawing stance", "increases attack", 1.5, None, "stats", "foe", {"effect": "attack", "accuracy": 100}, 5, 0)

#clear_stance = move("clear stance", "Increases accuracy", 1.5, None, "stats", 1, {"effect": "accuracy", "accuracy": 100}, 5, 0)

upper_stance = move("upper stance", "description", 1.5, None, "stats", "self", {"effect": "defence", "accuracy": 100}, 5, 0)

#razor_dodge = move("razor edge", "blocks physical attacks and retaliates", 40, None, "physical", target, {"effect": "invincible", "accuracy": 25}, 20)

##take_down = move("take down", "A strng attack but takes recoil", 120, None, "physical", "foe", {"effect": "recoil", "accuracy": 100}, 8, 0) 

#delayed_charge = move("delayed charge", "charges for one turn for massive damage the next turn", 200, None, "physical", "foe", None, 20) # special function

#legion_thrust = move("legion thrust", "A physical attack toward all enemies", 50, None, "physical", "all foes", None, 15, 0)

#MONSTER ATTACKS
#name, description, power, element, type_, targets, effect, sp, priority
#wing_slash = move("wing slash", "", 60, None, "physical", "foe", None, 6, 0)

tail_whip = move("tail whip", "", 100, None, "physical", "foe", None, 10, 0)

#body_slam = move("body slam", "All of the user's weight is slammed against the foe. May paralyze", 90, None, "physical", "foe", {"effect": "paralyze", "accuracy": 10}, 9, 0)

#boulder_fist = move("boulder fist", "", 80, None, "physical", "foe", None, 8, 0)

#bite = move("bite", description, power, element, type_, targets, effect, sp, priority)

#ice_shard = move("ice shard", "Shoots a wave of icecicles to random enemies", 40, "ice", type_, "random", effect, 20, 0)

#hammer_arm = move("hammer arm", description, power, element, type_, targets, effect, sp, priority)

#poison_sting = move("poison sting", "A stab with a needle covered in poison. May poison.", power, element, type_, targets, effect, sp, priority)

#rock_blast = move("rock blast", description, power, element, type_, targets, effect, sp, priority)

water_spout = move("water spout", "Shoots a barage of water in the air. Hits one turn later.", 150, "water", type_, targets, effect, 12, "delay")

shockwave = move("shockwave", "description", power, "volt", type_, targets, effect, sp, priority)

#fly = move("fly", "Flies in the air and attacks one turn later", 60, element, type_, "foe", effect, sp, "delay")

#dig = move("dig", "Digs into the ground and attacks one turn later", 60, element, type_, "foe", effect, sp, "delay")

#dive = move("dive", "Dives into water and attacks one turn later", 60, "water", type_, "foe", effect, sp, "delay")

#minimize = move("minimize", "Increases evasiveness", None, None, "stats", "self", effect, sp, 0)

rest = move("rest", "Falls asleep for two turns but restores HP", None, None, "status", "self", {"effect": "rest"}, 10, 0)

#particle_beam = move("particle beam", "A beam of charged particles to an enemy", power, "volt", "special", "foe", effect, sp, 0)

#mimic = move("mimic", "Mimics the attack of a foe.", power, element, type_, targets, effect, sp, priority)

cuddle = move("cuddle", "The most cutest and most innocent cuddle in the whole world.", power, element, type_, targets, effect, 0, 0) #restores energy for the foe

#lick = move("lick", "The friendly lick of the cutest puppy in the world.", 1, None, "physical", "foe", effect, sp, -1)

water_cannon = move("water cannon", "A very powerful shot of high pressure water. Hits first.", 150, "water", type_, "foe", effect, 25, 1)

sting = move("sting", "May prralyze", power, element, type_, targets, effect, sp, priority)

#poison_shot = move("poison shot", description, power, element, type_, targets, effect, sp, priority)

#earthquake = move("earthquake", "A powerful earthquake hits all foes but also allies.", 50, element, "physical", "everyone", effect, 30, 0)

#flee = move("flee", "Recklessly flee the battle losing some coins on the way.", power, element, type_, targets, effect, sp, 0)

#steal = move("steal", "Steals the hold item of the foe", 15, element, type_, "foe", effect, sp, priority)

#blinding_light = move("blinding light", "Lowers accuracy of foes.", power, element, type_, targets, effect, sp, priority)

#dragon_claw = move("dragon claw", "description", 95, element, "physical", targets, effect, sp, priority)

#dragon_descent = move("dragon descent", "A reckless charge to an enemy. Lowers defence for a turn.", 200, element, type_, targets, effect, sp, priority)

#charged shot = move("charged shot", "A powerful shot to an enemy. Lowers defence until activation.", 150, element, type_, targets, effect, sp, 0)

ricochet  = move("rocochet", "Shots toward random enemies", 30, element, type_, "random", effect, 15, 0)

surf = move("surf", "Summons a tall wave and hits all foes.", 30, "water", "special", "random", effect, 15, 0)

#ghastly_claw = move("ghastly claw", "Summons a ghastly claw to attack an enemy", 30, "dark", "physical", "foe", effect, 15, 0)

#void_sneak  = move("void sneak", "Disappears for a turn then attacks an enemy", 30, "water", "physical", "foe", effect, 15, 0)

#swift = move("swift", "Cannot miss", 50, None, "special", "fie", effect, 8, 0) #cannot miss

#head_bash = move("head bash", "Powerful bash against enemy. Low hit rate.", 140, None, "physical", "foe", effect, 15, 0) #low accuracy

#transform = move("transform", "Transforms into an enemy", None, None, "physical", "foe", effect, 15, 0) #low accuracy

#==============================
#CHARACTER INITIALIZATIONS=====
#==============================
#MONSTER INITIALIZATIONS
dragon = Monster(
  name = "Seaborne dragon",
  boss = True,
  description = "This dragon has the form of giant eel. It can hide its wings along its body and swim through the ocean.",
  attacks = [normal_attack, tail_whip, wing_slash],
  loot = life_gem,
  xp = 500,
  weakness = ["volt"],
  resistance = [],
  current_stats = {"energy": 100, "sp": 20, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy" : 100, "sp": 20, "power" : 20, "defence" : 20, "speed" : 11, "accuracy": 100})

flame_monster = Monster(
  name = "Flame monster",
  boss = False,
  description = "A flame monster is a fiery beast with a rocky body and a head and four legs made of fire. He can spit out lava.",
  attacks = [normal_attack, flamethrower, flame_grater, inferno_formula],
  loot = healing_potion,
  xp = 250,
  weakness = ["ice"],
  resistance = ["fire"],
  current_stats = {"energy": 35, "sp": 20, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 35, "sp": 20, "power": 10, "defence": 15, "speed": 5, "accuracy": 100}
)

golem = Monster(
  name = "golem", 
  boss = False,
  description = "Monster make of rocks. Has a shield.",
  attacks = [body_slam, boulder_fist],
  loot = steel_shield, 
  xp = 10,
  weakness = ["ice"],
  resistance = ["fire"],
  current_stats = {"energy": 35, "sp": 20, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 35, "sp": 20, "power": 10, "defence": 25, "speed": 5, "accuracy": 100}
)

Flame_Rhino = Monster(  
  name = "Flame Rhino", 
  boss = False,
  description = "A rhino with its horn made of fire.",
  attacks = [],
  loot = charcoal, 
  xp = 20,
  weakness = ["ice"],
  resistance = ["fire"],
  current_stats = {"energy": 70, "sp": 40, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 40, "sp": 40, "power": 20, "defence": 50, "speed": 10, "accuracy": 100}
)

puppy = Monster(  
  name = "puppy", 
  boss = False,
  description = "The cutest puppy you have ever seen. It spreads joy to everyone it encounters and should never be harmed ever.",
  attacks = [bite, scratch, howl],
  loot = puppy_skull, 
  xp = 20,
  weakness = ["fire", "ice", "dark", "volt", "water"],
  resistance = [""],
  current_stats = {"energy": 50, "sp": 40, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 9000, "sp": 40, "power": 1, "defence": 5, "speed": 20, "accuracy": 100}
)

ice_monster= Monster(  
  name = "Ice Monster", 
  boss = False,
  description = "Rivals of the flame monsters",
  attacks = [ice_beam, ice_formula, frigid_slash, blizzard_formula],
  loot = "icecicle", 
  xp = 10,
  weakness = ["fire"],
  resistance = ["ice"],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

Gunner = Monster(
  name = "Gunner", 
  boss = False,
  description = "",
  attacks = [],
  loot = ammo, 
  xp = 10,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

Python = Monster( 
  name = "Gunner", 
  boss = False,
  description = "",
  attacks = [bite, poison_shot],
  loot = snake_skin, 
  xp = 10,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

flame_puff = Monster(
  name = "Gunner", 
  boss = False,
  description = "",
  attacks = [fire_formula],
  loot = charcoal, 
  xp = 10,
  weakness = ["water", "dark"],
  resistance = ["fire", "rock"],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

ice_puff = Monster( 
  name = "Gunner", 
  boss = False,
  description = "",
  attacks = [ice_formula],
  loot = ice_stone, 
  xp = 10,
  weakness = ["fire", "dark"],
  resistance = ["ice", "water"],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

fire_wolf = Monster( 
  name = "Gunner", 
  boss = False,
  description = "",
  attacks = [slash],
  loot = wolf_pelt, 
  xp = 10,
  weakness = ["water"],
  resistance = ["fire"],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

ice_bird = Monster(  
  name = "Gunner", 
  boss = False,
  description = "",
  attacks = [fly],
  loot = white_feather, 
  xp = 10,
  weakness = ["fire"],
  resistance = ["ice"],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

sea_serpent = Monster( 
  name = "Gunner", 
  boss = False,
  description = "",
  attacks = [dive],
  loot = sea_scale, 
  xp = 10,
  weakness = ["volt"],
  resistance = ["water"],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

Sorcerer = Monster(
  name = "Gunner", 
  boss = True,
  description = "",
  attacks = [],
  loot = wand, 
  xp = 10,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

Skeleton = Monster(
  name = "Gunner", 
  boss = False,
  description = "",
  attacks = [],
  loot = rib, 
  xp = 10,
  weakness = ["rock"],
  resistance = ["dark"],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

castle_guards = Monster(
  name = "Gunner", 
  boss = False,
  description = "",
  attacks = [],
  loot = leather, 
  xp = 10,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

gorrilla = Monster(  #changes type each turn because it's cute
  name = "Gunner", 
  boss = False,
  description = "",
  attacks = [hammer_arm],
  loot = gorrilla_butt, 
  xp = 10,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

aagron = Monster( 
  name = "Gunner", 
  boss = False,
  description = "",
  attacks = [head_bash],
  loot = horn, 
  xp = 10,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

bee = Monster(  
  name = "Gunner", 
  boss = False,
  description = "",
  attacks = [],
  loot = magic_wings, 
  xp = 10,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

T_rex = Monster( 
  name = "Gunner", 
  boss = False,
  description = "",
  attacks = [bite],
  loot = large_tooth, 
  xp = 10,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

hexer_monster = Monster( 
  name = "Gunner", 
  boss = False,
  description = "",
  attacks = [],
  loot = cloak, #make some human foes drop equippable items
  xp = 10,
  weakness = ["fire"],
  resistance = ["dark"],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

knight = Monster( 
  name = "Gunner", 
  boss = False,
  description = "",
  attacks = [slash, stab, drawing_stance],
  loot = helmet,
  xp = 10,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

warrior = Monster(  #has axes
  name = "Gunner", 
  boss = False,
  description = "",
  attacks = [shield_rush, fortify],
  loot = steel_shield, 
  xp = iron_scrap,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

magician = Monster(  #original character
  name = "Gunner", 
  boss = False,
  description = "",
  attacks = [minimize],
  loot = crystal_staff, 
  xp = 10,
  weakness = ["dark"],
  resistance = ["fire"],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

pirate = Monster(  #original character
  name = "Gunner", 
  boss = False,
  description = "",
  attacks = [],
  loot = "30 gold coins", 
  xp = 10,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

captain = Monster(  #original character
  name = "Gunner", 
  boss = False,
  description = "",
  attacks = [],
  loot = parrot, 
  xp = 10,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

sailor = Monster(  #original character
  name = "Gunner", 
  boss = False,
  description = "",
  attacks = [],
  loot = gold_nugget, 
  xp = 10,
  weakness = [""],
  resistance = ["water"],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

penguin = Monster(  #original character
  name = "Gunner", 
  boss = False,
  description = "",
  attacks = [ice_formula, ice_shard],
  loot = ice_stone, 
  xp = 10,
  weakness = ["fire"],
  resistance = ["ice"],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

tiger = Monster(  #original character
  name = "Gunner", 
  boss = False,
  description = "",
  attacks = [],
  loot = fang, 
  xp = 10,
  weakness = [""],
  resistance = ["volt"],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

whale = Monster(  #original character
  name = "Gunner", 
  boss = False,
  description = "",
  attacks = [water_spout, water_cannon, dive],
  loot = blubber, 
  xp = 10,
  weakness = [""],
  resistance = ["water"],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

thief = Monster(  #original character
  name = "Gunner", 
  boss = False,
  description = "",
  attacks = [steal],
  loot = "800 coins", 
  xp = 10,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

baby_dragon = Monster(  #original character
  name = "Gunner", 
  boss = False,
  description = "",
  attacks = [bite],
  loot = dragon_scale, 
  xp = 10,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

flame_dragon = Monster(  #original character
  name = "Gunner", 
  boss = False,
  description = "",
  attacks = [inferno_formula, fly, dragon_claw],
  loot = dragon_butt, 
  xp = 10,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

digger = Monster(  #original character
  name = "Gunner", 
  boss = False,
  description = "",
  attacks = [dig],
  loot = shovel, 
  xp = 10,
  weakness = ["water"],
  resistance = ["volt", "fire"],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

alien = Monster(  #original character
  name = "Gunner", 
  boss = False,
  description = "",
  attacks = [particle_beam],
  loot = unknown_substance, 
  xp = 10,
  weakness = ["fire"],
  resistance = ["dark"],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

rock_dragon = Monster(  #original character
  name = "Gunner", 
  boss = False,
  description = "",
  attacks = [rock_blast, earthquake],
  loot = diamond, 
  xp = 10,
  weakness = ["ice"],
  resistance = ["fire"],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

ice_snake = Monster(  #original character
  name = "Gunner", 
  boss = False,
  description = "",
  attacks = [],
  loot = crystal_scale, 
  xp = 10,
  weakness = ["fire"],
  resistance = ["ice"],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

storm_dragon = Monster(  #has two heads, one is fire type, the other ice type
  name = "Gunner", 
  boss = False,
  description = "",
  attacks = [frigid_slash, flame_grater, flamethrower, ice_beam],
  loot = extinguished_ice, 
  xp = 10,
  weakness = [],
  resistance = [],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

butterfly = Monster(  #original character
  name = "Gunner", 
  boss = False,
  description = "",
  attacks = [],
  loot = insect_eye, 
  xp = 10,
  weakness = ["fire", "ice"],
  resistance = [],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

bug = Monster(  #original character
  name = "Gunner", 
  boss = False,
  description = "",
  attacks = [],
  loot = insect_eye, 
  xp = 10,
  weakness = ["fire"],
  resistance = [""],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

tank = Monster(  #original character
  name = "Gunner", 
  boss = False,
  description = "",
  attacks = [particle_beam],
  loot = torpedo, 
  xp = 10,
  weakness = ["volt"],
  resistance = ["water"],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

robot = Monster(  #original character
  name = "Gunner", 
  boss = False,
  description = "",
  attacks = [],
  loot = circuit_board, 
  xp = 10,
  weakness = ["volt", "water"],
  resistance = [],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

chameleon = Monster(  #
  name = "Gunner", 
  boss = False,
  description = "",
  attacks = [mimic, transform],
  loot = rainbow_pelt, 
  xp = 10,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

leaf_bird = Monster(  #a bird with wings that look like a leaf
  name = "Gunner", 
  boss = False,
  description = "",
  attacks = [],
  loot = bird_limb, 
  xp = 10,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

eel = Monster(  #body of dark green and zigzag blue line across its body.
  name = "Gunner", 
  boss = False,
  description = "An electric eel",
  attacks = [],
  loot = battery, 
  xp = 10,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

flaresaur = Monster(  #looks like a red bulbasaur standing up but it has fire on its back instead of a leaf
  name = "Gunner", 
  boss = False,
  description = "",
  attacks = [],
  loot = extinguished_wood, 
  xp = 10,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

infernosaur = Monster(  #flaming triceratops
  name = "Gunner", 
  boss = False,
  description = "",
  attacks = [],
  loot = extinguished_wood, 
  xp = 10,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

panda = Monster(
  name = "Gunner", 
  boss = False,
  description = "",
  attacks = [],
  loot = leftover_panda_express_meal, bamboo,
  xp = 10,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

angler = Monster(  
  name = "Gunner", 
  boss = False,
  description = "",
  attacks = [blinding_light],
  loot = lightbulb, 
  xp = 10,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

shark = Monster( 
  name = "Gunner", 
  boss = False,
  description = "",
  attacks = [],
  loot = shark_fin, 
  xp = 10,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

ladybug = Monster(
  name = "Gunner", 
  boss = False,
  description = "",
  attacks = [],
  loot = polka_dot_shirt, 
  xp = 10,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

lava_turtle = Monster(  #A lava turtle with a cannon on its back
  name = "Gunner", 
  boss = False,
  description = "This turtle has a powerful cannon on its back that can shoot balls of lava.",
  attacks = [],
  loot = molten_shell, canonball,
  xp = 10,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

starfish = Monster(  #original character
  name = "Gunner", 
  boss = False,
  description = "",
  attacks = [],
  loot = amber_lump, 
  xp = 10,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

bear = Monster(  #original character
  name = "Gunner", 
  boss = False,
  description = "",
  attacks = [rest, slash],
  loot = honey_nut_cherios, 
  xp = 10,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

pirahna = Monster(  #original character
  name = "Gunner", 
  boss = False,
  description = "",
  attacks = [bite],
  loot = fang, 
  xp = 10,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

glowfish = Monster(  #original character
  name = "Gunner", 
  boss = False,
  description = "",
  attacks = [blinding_light],
  loot = glow_fin, 
  xp = 10,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

fire_macaw = Monster(  #A macaw with wings of fire
  name = "Gunner", 
  boss = False,
  description = "",
  attacks = [fly],
  loot = carminite, 
  xp = 10,
  weakness = ["ice"],
  resistance = [""],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)

pufferfish = Monster(  #original character
  name = "Gunner", 
  boss = False,
  description = "",
  attacks = [],
  loot = pillow, 
  xp = 10,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": 60, "sp": 60, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": 60, "sp": 60, "power": 30, "defence": 55, "speed": 25, "accuracy": 100}
)



'''
STUPID MONSTERS

Lightning_mcqueen = Monster(  #original character
  name = "Gunner", 
  boss = False,
  description = "",
  attacks = [],
  loot = , 
  xp = ,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": , "sp": , "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": , "sp": , "power": , "defence": , "speed": , "accuracy": 100}
)

goomba = Monster(
  name = "Goomba", 
  boss = False,
  description = "An ugly mushroom",
  attacks = [],
  loot = "10 coins", 
  xp = 10,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": , "sp": , "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": , "sp": , "power": , "defence": , "speed": , "accuracy": 100}
)

Mewtwo = Monster(
  name = "Mewtwo", 
  boss = True,
  description = "It was created by a scientist after years of horrific gene-splicing and DNA-engineering experiments.",
  attacks = [aura_sphere, psychic, volt_formula, fortify],
  loot = , 
  xp = 10000,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": , "sp": , "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": , "sp": , "power": , "defence": , "speed": , "accuracy": 100}
)

Bowser = Monster(
  name = "", 
  boss = False,
  description = "",
  attacks = [],
  loot = , 
  xp = ,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": , "sp": , "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": , "sp": , "power": , "defence": , "speed": , "accuracy": 100}
)

Dark_bowser = Monster(
  name = "", 
  boss = True,
  description = "",
  attacks = [],
  loot = , 
  xp = ,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": , "sp": , "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": , "sp": , "power": , "defence": , "speed": , "accuracy": 100}
)

Metroid = Monster(
  name = "", 
  boss = True,
  description = "",
  attacks = [],
  loot = , 
  xp = ,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": , "sp": , "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": , "sp": , "power": , "defence": , "speed": , "accuracy": 100}
)

Ganon = Monster(
  name = "", 
  boss = False,
  description = "",
  attacks = [],
  loot = , 
  xp = ,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": , "sp": , "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": , "sp": , "power": , "defence": , "speed": , "accuracy": 100}
)

King_Dedede = Monster(
  name = "", 
  boss = False,
  description = "",
  attacks = [],
  loot = , 
  xp = ,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": , "sp": , "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": , "sp": , "power": , "defence": , "speed": , "accuracy": 100}
)

Master_Hand = Monster(
  name = "", 
  boss = False,
  description = "",
  attacks = [],
  loot = , 
  xp = ,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": , "sp": , "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": , "sp": , "power": , "defence": , "speed": , "accuracy": 100}
)

Pirahna_plant = Monster(
  name = "", 
  boss = False,
  description = "",
  attacks = [],
  loot = , 
  xp = ,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": , "sp": , "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": , "sp": , "power": , "defence": , "speed": , "accuracy": 100}
)

Ridley = Monster(
  name = "", 
  boss = False,
  description = "",
  attacks = [],
  loot = , 
  xp = ,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": , "sp": , "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": , "sp": , "power": , "defence": , "speed": , "accuracy": 100}
)

Boo = Monster(
  name = "", 
  boss = False,
  description = "",
  attacks = [],
  loot = , 
  xp = ,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": , "sp": , "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": , "sp": , "power": , "defence": , "speed": , "accuracy": 100}
)

King_k_rool = Monster(
  name = "", 
  boss = False,
  description = "",
  attacks = [],
  loot = , 
  xp = ,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": , "sp": , "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": , "sp": , "power": , "defence": , "speed": , "accuracy": 100}
)

Waddle_dee = Monster(
  name = "", 
  boss = False,
  description = "",
  attacks = [],
  loot = , 
  xp = ,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": , "sp": , "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": , "sp": , "power": , "defence": , "speed": , "accuracy": 100}

Pac_ghost= Monster(
  name = "", 
  boss = False,
  description = "",
  attacks = [],
  loot = , 
  xp = ,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": , "sp": , "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": , "sp": , "power": , "defence": , "speed": , "accuracy": 100}

space_invader = Monster(
  name = "", 
  boss = False,
  description = "",
  attacks = [],
  loot = , 
  xp = ,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": , "sp": , "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": , "sp": , "power": , "defence": , "speed": , "accuracy": 100}

virus = Monster( #from Dr. Mario
  name = "", 
  boss = False,
  description = "",
  attacks = [],
  loot = , 
  xp = ,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": , "sp": , "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": , "sp": , "power": , "defence": , "speed": , "accuracy": 100}

Crocodile = Monster(  #from Donkey Kong
  name = "", 
  boss = False,
  description = "",
  attacks = [],
  loot = , 
  xp = ,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": , "sp": , "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": , "sp": , "power": , "defence": , "speed": , "accuracy": 100}

Koopa =  = Monster(  
  name = "", 
  boss = False,
  description = "",
  attacks = [],
  loot = , 
  xp = ,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": , "sp": , "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": , "sp": , "power": , "defence": , "speed": , "accuracy": 100}

Cheep_cheep = Monster(  
  name = "", 
  boss = False,
  description = "",
  attacks = [],
  loot = , 
  xp = ,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": , "sp": , "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": , "sp": , "power": , "defence": , "speed": , "accuracy": 100}

shroom = Monster(  # from partners in time
  name = "", 
  boss = False,
  description = "",
  attacks = [],
  loot = , 
  xp = ,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": , "sp": , "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": , "sp": , "power": , "defence": , "speed": , "accuracy": 100}

Hammer_bros = Monster(  
  name = "", 
  boss = False,
  description = "",
  attacks = [],
  loot = , 
  xp = ,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": , "sp": , "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": , "sp": , "power": , "defence": , "speed": , "accuracy": 100}

Shadow_the_hedgehog = Monster(  
  name = "", 
  boss = False,
  description = "",
  attacks = [],
  loot = , 
  xp = ,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": , "sp": , "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": , "sp": , "power": , "defence": , "speed": , "accuracy": 100}

Waluigi = Monster(  
  name = "", 
  boss = False,
  description = "",
  attacks = [],
  loot = , 
  xp = ,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": , "sp": , "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": , "sp": , "power": , "defence": , "speed": , "accuracy": 100}

Chain_Chomp = Monster(  
  name = "", 
  boss = False,
  description = "",
  attacks = [],
  loot = , 
  xp = ,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": , "sp": , "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": , "sp": , "power": , "defence": , "speed": , "accuracy": 100}

Dark_Samus = Monster(  
  name = "", 
  boss = False,
  description = "",
  attacks = [],
  loot = , 
  xp = ,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": , "sp": , "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": , "sp": , "power": , "defence": , "speed": , "accuracy": 100}

Lakitu = Monster(  
  name = "", 
  boss = False,
  description = "",
  attacks = [],
  loot = , 
  xp = ,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": , "sp": , "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": , "sp": , "power": , "defence": , "speed": , "accuracy": 100}
'''




'''
example monster initialization:

golem = Monster(
  name = "", 
  boss = False,
  description = "",
  attacks = [],
  loot = , 
  xp = ,
  weakness = [""],
  resistance = [""],
  current_stats = {"energy": , "sp": , "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None},
  base_stats = {"energy": , "sp": , "power": , "defence": , "speed": , "accuracy": 100}
)

'''



monsterdex = {
  golem: "unseen",
  flame_monster: "unseen",
  dragon: "unseen"
}
#======================================================================
#HEROES================================================================
#======================================================================
Flavio = Hero(
  name = "Flavio",
  attacks = [normal_attack, stab, slash], #first attack must be normal_attack
  equipped = [battle_axe, wooden_shield, steel_armor],
  current_stats = {"energy" : 100, "sp" : 25, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None, "boost" : 0, "xp": 0},
  base_stats = {"energy" : 100, "sp": 25, "power" : 10, "defence" : 20, "speed": 10, "max_xp" : 100, "accuracy": 100, "lvl" : 1},
)

Scorpion = Hero(
name = "Scorpion",
  attacks = [normal_attack, raging_edge, drawing_stance, upper_stance, clear_stance], 
  equipped = [],
  current_stats = {"energy": 60 , "sp" : 20, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None, "boost" : 0, "xp": 0},
  base_stats = {"energy" : 60, "sp": 20, "power" :15, "defence":12, "speed": 14, "max_xp" : 100, "accuracy": 100, "lvl" : 1},
)

Vivian = Hero(
name = "Vivian",
  attacks = [], 
  equipped = [],
  current_stats = {"energy": 60 , "sp" : 20, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None, "boost" : 0, "xp": 0},
  base_stats = {"energy" : 60, "sp": 20, "power" :15, "defence":12, "speed": 14, "max_xp" : 100, "accuracy": 100, "lvl" : 1},
)

Lazarus = Hero(
name = "Lazarus",
  attacks = [], 
  equipped = [],
  current_stats = {"energy": 60 , "sp" : 20, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None, "boost" : 0, "xp": 0},
  base_stats = {"energy" : 60, "sp": 20, "power" :15, "defence":12, "speed": 14, "max_xp" : 100, "accuracy": 100, "lvl" : 1},
)

Flame_monster_hero = Hero(
name = "Flame monster",
  attacks = [], 
  equipped = [],
  current_stats = {"energy": 60 , "sp" : 20, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None, "boost" : 0, "xp": 0},
  base_stats = {"energy" : 60, "sp": 20, "power" :15, "defence":12, "speed": 14, "max_xp" : 100, "accuracy": 100, "lvl" : 1},
)

Hexer = Hero(
name = "Hexer",
  attacks = [], 
  equipped = [],
  current_stats = {"energy": 60 , "sp" : 20, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None, "boost" : 0, "xp": 0},
  base_stats = {"energy" : 60, "sp": 20, "power" :15, "defence":12, "speed": 14, "max_xp" : 100, "accuracy": 100, "lvl" : 1},
)

Mario = Hero(
name = "Mario",
  attacks = [], 
  equipped = [],
  current_stats = {"energy": 60 , "sp" : 20, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None, "boost" : 0, "xp": 0},
  base_stats = {"energy" : 60, "sp": 20, "power" :15, "defence":12, "speed": 14, "max_xp" : 100, "accuracy": 100, "lvl" : 1},
)

Link = Hero(
name = "Link",
  attacks = [], 
  equipped = [],
  current_stats = {"energy": 60 , "sp" : 20, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None, "boost" : 0, "xp": 0},
  base_stats = {"energy" : 60, "sp": 20, "power" :15, "defence":12, "speed": 14, "max_xp" : 100, "accuracy": 100, "lvl" : 1},
)

Kirby = Hero(
name = "Kirby",
  attacks = [], 
  equipped = [],
  current_stats = {"energy": 60 , "sp" : 20, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None, "boost" : 0, "xp": 0},
  base_stats = {"energy" : 60, "sp": 20, "power" :15, "defence":12, "speed": 14, "max_xp" : 100, "accuracy": 100, "lvl" : 1},
)

Little_mac = Hero(
name = "Kirby",
  attacks = [], 
  equipped = [],
  current_stats = {"energy": 60 , "sp" : 20, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None, "boost" : 0, "xp": 0},
  base_stats = {"energy" : 60, "sp": 20, "power" :15, "defence":12, "speed": 14, "max_xp" : 100, "accuracy": 100, "lvl" : 1},
)

Fox = Hero(
name = "Kirby",
  attacks = [], 
  equipped = [],
  current_stats = {"energy": 60 , "sp" : 20, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None, "boost" : 0, "xp": 0},
  base_stats = {"energy" : 60, "sp": 20, "power" :15, "defence":12, "speed": 14, "max_xp" : 100, "accuracy": 100, "lvl" : 1},
)

Donkey_Kong = Hero(
name = "Kirby",
  attacks = [], 
  equipped = [],
  current_stats = {"energy": 60 , "sp" : 20, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None, "boost" : 0, "xp": 0},
  base_stats = {"energy" : 60, "sp": 20, "power" :15, "defence":12, "speed": 14, "max_xp" : 100, "accuracy": 100, "lvl" : 1},
)


Samus = Hero(
name = "Samus",
  attacks = [], 
  equipped = [],
  current_stats = {"energy": 60 , "sp" : 20, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None, "boost" : 0, "xp": 0},
  base_stats = {"energy" : 60, "sp": 20, "power" :15, "defence":12, "speed": 14, "max_xp" : 100, "accuracy": 100, "lvl" : 1},
)

Captain_Falcon = Hero(
name = "Captain Falcon",
  attacks = [], 
  equipped = [],
  current_stats = {"energy": 60 , "sp" : 20, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None, "boost" : 0, "xp": 0},
  base_stats = {"energy" : 60, "sp": 20, "power" :15, "defence":12, "speed": 14, "max_xp" : 100, "accuracy": 100, "lvl" : 1},
)

Charizard = Hero(
name = "Charizard",
  attacks = [], 
  equipped = [],
  current_stats = {"energy": 60 , "sp" : 20, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None, "boost" : 0, "xp": 0},
  base_stats = {"energy" : 60, "sp": 20, "power" :15, "defence":12, "speed": 14, "max_xp" : 100, "accuracy": 100, "lvl" : 1},
)

Mega_man = Hero(
name = "Mega Man",
  attacks = [], 
  equipped = [],
  current_stats = {"energy": 60 , "sp" : 20, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None, "boost" : 0, "xp": 0},
  base_stats = {"energy" : 60, "sp": 20, "power" :15, "defence":12, "speed": 14, "max_xp" : 100, "accuracy": 100, "lvl" : 1},
)

Glitch_man = Hero(
name = "Glitch Man",
  attacks = [], 
  equipped = [],
  current_stats = {"energy": 60 , "sp" : 20, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None, "boost" : 0, "xp": 0},
  base_stats = {"energy" : 60, "sp": 20, "power" :15, "defence":12, "speed": 14, "max_xp" : 100, "accuracy": 100, "lvl" : 1},
)

Duck_hunt = Hero(
name = "Duck Hunt Dog",
  attacks = [], 
  equipped = [],
  current_stats = {"energy": 60 , "sp" : 20, "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None, "boost" : 0, "xp": 0},
  base_stats = {"energy" : 60, "sp": 20, "power" :15, "defence":12, "speed": 14, "max_xp" : 100, "accuracy": 100, "lvl" : 1},
)



'''
example hero initialization:

Scorpion = Hero(
name = ,
  attacks = [], 
  equipped = [],
  current_stats = {"energy" : , "sp" : , "status": None, "buff": None, "next attack": None, "next attack target": None, "last attack":None, "boost" : 0, "xp": 0},
  base_stats = {"energy" : , "sp": , "power" : , "defence" : , "speed": , "max_xp" 100: , "accuracy": 100, "lvl" : 1},
)
'''


Hero.inventory = [cake, cake, cake, amirita, amirita, steel_shield]
Hero.money = 4000


#NPCS
king = npc(None, "Hello, general.", "Good Luck!", False)


#==============================
#==========INITIALIZE GAME=====
#==============================

for item in Flavio.equipped:
    Flavio.addBonus(item, False)

shop_items = [fire_resistant_potion, healing_potion, revive_item, soma, steel_shield]

#hero.add_to_inventory(fire_resistant_potion)
Flavio.base_stats["power"] = 500
Flavio.current_stats["sp"] = 0
Hero.registry = [Flavio]

scene1(False)

#================== ( ͡° ͜ʖ ͡°) ============
'''
        List of heroes


        List of monsters
dragon
flame_monster
golem
Flame_Rhino  
puppy  
ice_monster
Gunner
Python
flame_puff
ice_puff
fire_wolf
ice_bird
sea_serpent
Sorcerer
Skeleton 
castle_guards
gorrilla
aagron
bee
T_rex
hexer_monster
knight
warrior
magician
pirate
captain
sailor
penguin
tiger
whale
thief
baby_dragon
flame_dragon
digger
alien
rock_dragon
ice_snake
storm_dragon  #has two heads, one is fire type, the other ice type
butterfly
bug
tank
robot
chameleon  #
leaf_bird  #a bird with wings that look like a leaf
eel  #body of dark green and zigzag blue line across its body.
flaresaur  #looks like a red bulbasaur standing up but it has fire on its back instead of a leaf
infernosaur  #flaming triceratops
panda
angler  
shark 
ladybug
lava_turtle  #A lava turtle with a cannon on its back
starfish
bear
pirahna
glowfish
fire_macaw  #A macaw with wings of fire
pufferfish



        List of moves






				Things left to do:
fix equipping system
update combatant system
add moves information
make items work
make moves work 
be able to get new moves when you level up
add more npcs
fix add_to_inventory() and when you add more heroes make it so that the game takes that into account
get background music
add weakness, resistance system
add a full menu
be able to access inventory during battle
get better system for determining how much damage a move will cause
add key items list

				resources
Pylint
https://www.gamefaqs.com/3ds/709464-etrian-odyssey-untold-the-millennium-girl/faqs/68469

'''
import entity
import traps
import ethereal

import random


class Humanoid(entity.Mob):

    def __init__(self,parent,id):
        super(Humanoid,self).__init__(parent,id)

    def init(self):
        super(Humanoid,self).init()
        self.name = "humanoid"
        self.nodes = { }
        self.bodyparts = ['head', 'hands', 'chest', 'back', 'legs']
        for part in self.bodyparts:
            self.add_node(part)

    def was_collided(self, id, type):
        if type == self.parent.ATTEMPTED_INTERACTION:
            ent = self.parent.get_ent(id)
            if isinstance(ent, entity.Mob):
                return self.check_damage()

    def get_injury(self,node):
        node = self.get_node(node)
        ents = self.parent.get_in(node)
        if ents:
            for id in self.parent.get_in(node):
                ent = self.parent.get_ent(id)
                if isinstance(ent, ethereal.Wound):
                    return ent
        return None

    def get_injury_amount(self,node):
        node = self.get_node(node)
        total = 0
        ents = self.parent.get_in(node)
        if ents:
            for id in self.parent.get_in(node):
                ent = self.parent.get_ent(id)
                if isinstance(ent, ethereal.Wound):
                    total += ent.damage
        return total

    def get_injuries(self):
        total = 0
        for part in self.bodyparts:
            total += self.get_injury_amount(part)
        return total

    def get_node(self,name):
        if name not in self.nodes:
            raise IDNotAssignedError
        return self.nodes[name]

    def get_nodes(self):
        return self.nodes

    def add_node(self,name):
        id = self.parent.add_entity('bodypart')
        #self.parent.set_parent(id, self.id)
        self.parent.ent_equip(self.id, id)
        self.parent.get_ent(id).name = name
        self.nodes[name] = id

    def deal_damage(self, amount, target=None):
        if not target:
            target = random.choice(self.bodyparts)
        if not self.get_injury(target):
            wound = self.parent.add_entity('wound')
            self.parent.get_ent(wound).set_damage(amount)
            self.parent.set_parent(wound,self.get_node(target))
        else:
            wound = self.get_injury(target)
            wound.set_damage(wound.damage + amount)
        return self.check_damage()

    def check_damage(self):
        amount = self.get_injuries()
        if amount >= 100:
            self.die()
            return True
        return False

    def update(self):
        self.check_damage()

class Player(Humanoid):
    """Simple player class."""

    def __init__(self,parent,id):
        super(Player,self).__init__(parent,id)

    def init(self):
        super(Player,self).init()
        self.char = '@'
        self.fgcol = (255, 255, 255)
        self.name = "Player"
        self.pickup_queue = [ ]
        self.inventory = self.parent.add_entity("backpack")
        self.parent.set_parent(self.inventory, self.nodes["back"])
        self.jumping = False
        self.jumping_ticker = 15

    def jump(self):
        if not self.jumping:
            if not self.jumping_ticker:
                self.jumping = True
                self.parent.post_message("You get ready to jump.")
                self.jumping_ticker = 15
            else:
                self.parent.post_message("You're too exhausted!")
        else:
            self.parent.post_message("You're already ready to jump!")

    def add_pickup(self, obj):
        self.pickup_queue.append(obj)

    def handle_pickups(self):
        if self.pickup_queue:
            s = "You lift the "
            for ent in self.pickup_queue:
                self.parent.set_parent(ent,self.inventory)
                s += self.parent.get_ent(ent).name +', '
            self.parent.post_message(s[:-2]+".")
            self.pickup_queue = [ ]

    def can_lift(self):
        #if not self.parent.get_in(self.inventory):
        #    return True
        #return False
        return True

    def finished_lifting(self, id, success_value, metadata=None):
        super(Player,self).finished_lifting(id, type)
        ent = self.parent.get_ent(id)
        if isinstance(ent, entity.Item):
            if self.can_lift():
                self.add_pickup(id)

    def collided(self, id, type):
        super(Player,self).collided(id, type)
        ent = self.parent.get_ent(id)
        if type == self.parent.ATTEMPTED_INTERACTION:
            if isinstance(ent, entity.Mob):
                self.parent.post_message("You slice at the "+self.parent.get_name(id)+'.')

    def was_collided(self, id, type):
        super(Player,self).was_collided(id, type)
        ent = self.parent.get_ent(id)
        if type == self.parent.DIRECT_INTERACTION:
            if isinstance(ent, traps.BladeTrap):
                self.parent.post_message("The blade cuts straight through your flesh.")
        elif type == self.parent.ATTEMPTED_INTERACTION:
            if isinstance(ent, traps.PillarTrap):
                self.parent.post_message("The pillar barrels into you, throwing you backwards.")

    def finished_colliding(self, id, success_value, metadata=None):
        super(Player,self).finished_colliding(id, success_value, metadata)
        ent = self.parent.get_ent(id)
        if isinstance(ent,ethereal.LevelEnd):
            if success_value:
                self.parent.post_message("You slip and start sliding down the tunnel.")
                self.parent.parent.layout = "level_"+str(int(self.parent.parent.layout.split('_',1)[1])+1)
                self.parent.parent.destroy_ents()
                self.parent.parent.generate_map(self.parent.parent.get_map().width, self.parent.parent.get_map().height, set=True)
                self.parent.parent.place_player(1)
        elif isinstance(ent,traps.Door):
            if success_value:
                self.parent.post_message("You open the "+self.parent.get_name(id)+'.')
        elif isinstance(ent, entity.Mob):
            if success_value:
                self.parent.post_message("You kill the "+self.parent.get_name(id)+'.')
        elif isinstance(ent,traps.ArrowTrap):
            if success_value:
                self.parent.post_message("You're hit by an arrow.")
        elif isinstance(ent,traps.StoneTrap):
            if success_value:
                self.parent.post_message("A stone falls on your head.")
        elif isinstance(ent,traps.TripTrap):
            if success_value:
                self.parent.post_message("You trip on a wire and stumble.")
            else:
                self.parent.post_message("You notice a loose wire around your feet.")
        elif isinstance(ent,traps.MoveTrap):
            if success_value:
                self.parent.post_message("You feel yourself being pushed around.")
        elif isinstance(ent,traps.GrateTrap):
            self.parent.post_message("You slip and collapse onto the grate.")
            if success_value:
                 self.parent.post_message("You get up, but feel somehow lighter.")
            else:
                self.parent.post_message("You get back to your feet.")

    def move(self,x,y):
        if self.jumping:
            self.parent.post_message("You leap through the air.")
            ok = self.parent.move_ent(self.id,x,y)
            ok = ok and self.parent.move_ent(self.id,x,y)
            self.jumping = False
            return ok
        else:
            return self.parent.move_ent(self.id,x, y)

    def die(self):
        if not self.dead:
            self.dead = 1
            self.parent.set_parent(self.id,0)

    def update(self):
        super(Player,self).update()
        self.handle_pickups()
        if not self.jumping and self.jumping_ticker:
            self.jumping_ticker -= 1

class IDNotAssignedError(Exception):
    """Raised when an entity was asked to give its ID, but it has none assigned."""
    pass
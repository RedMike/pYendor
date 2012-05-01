from data.entities import Entity

import random

class Mob(Entity):

    def init(self):
        super(Mob,self).init()
        self.set_attributes('01100')
        self.char = '@'
        self.name = 'mob'
        self.fgcol = (0,255,255)
        self.dead = 0

    def collide(self, id):
        ent = self.parent[id]
        if self.parent.is_instance(id, "mob"):
            hit = ent.deal_damage(10)

    def was_collided(self, id):
        return False

    def deal_damage(self, amount, target=None):
        self.die()
        return self.check_damage()

    def check_damage(self):
        if not self.dead:
            return False
        return True

    def die(self):
        """Verify if not already dead, and change into corpse of being."""
        if not self.dead:
            self.dead = 1
            id = self.parent.add_entity("item")
            self.parent.set_pos(id,self.parent.get_pos(self.id))
            self.parent[id].name = self.name + " corpse"
            self.parent.set_parent(self.id,0)

    def update(self):
        if not self.check_damage():
            dx, dy = random.randint(-1,1), random.randint(-1,1)
            self.move(dx, dy)

class Humanoid(Mob):

    def init(self):
        super(Humanoid,self).init()
        self.name = "humanoid"
        self.nodes = { }
        self.bodyparts = ['head', 'neck', 'chest', 'back', 'left hand', 'right hand', 'left leg', 'right leg']
        for id in range(len(self.bodyparts)):
            self.add_node(self.bodyparts[id])

    def was_collided(self, id):
        success = super(Humanoid,self).was_collided(id)
        ent = self.parent[id]
        if self.parent.is_instance(id, "mob"):
            success = self.check_damage()
        return success

    def get_injury(self,node):
        node = self.get_node(node)
        ents = self.parent.get_in(node)
        if ents:
            for id in self.parent.get_in(node):
                if self.parent.is_instance(id, "wound"):
                    ent = self.parent.get_ent(id)
                    return ent
        return None

    def get_injury_amount(self,node):
        node = self.get_node(node)
        total = 0
        ents = self.parent.get_in(node)
        if ents:
            for id in self.parent.get_in(node):
                if self.parent.is_instance(id, "wound"):
                    ent = self.parent[id]
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
        ent_id = self.parent.add_entity('bodypart')
        self.parent.ent_equip(self.id, ent_id)
        self.parent[ent_id].name = name
        self.nodes[name] = ent_id

    def deal_damage(self, amount, target=None):
        if not target:
            target = random.choice(self.bodyparts)
        if not self.get_injury(target):
            wound = self.parent.add_entity('wound')
            self.parent[wound].set_damage(amount)
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

    def init(self):
        super(Player,self).init()
        self.char = '@'
        self.fgcol = (255,255,255)
        self.name = "Player"
        self.pickup_queue = [ ]
        self.inventory = self.nodes['right hand']
        back_id = self.parent.add_entity("backpack")
        self.parent.set_parent(back_id, self.nodes["back"])
        self.inventory = back_id

    def add_pickup(self, obj):
        self.pickup_queue.append(obj)

    def handle_pickups(self):
        if self.pickup_queue:
            s = "You lift the "
            for ent in self.pickup_queue:
                self.parent.set_parent(ent,self.inventory)
                s += self.parent[ent].name +', '
            self.parent.post_message(s[:-2]+".")
            self.pickup_queue = [ ]

    def can_lift(self):
        #if not self.parent.get_in(self.inventory):
        #    return True
        #return False
        return True

    def finished_dropping(self, id, success_value):
        super(Player,self).finished_dropping(id, success_value)
        if success_value:
            if self.inventory == id:
                self.inventory = self.nodes['right hand']
            self.parent.post_message("You drop the "+self.parent.get_name(id)+".")

    def finished_lifting(self, id, success_value):
        super(Player,self).finished_lifting(id, success_value)
        if self.parent.is_instance(id, "item"):
            if self.can_lift() and success_value:
                self.add_pickup(id)

    def collide(self, id):
        super(Player,self).collide(id)
        if self.parent.is_instance(id, "mob"):
            ent = self.parent[id]
            self.parent.post_message("You slice at the "+self.parent.get_name(id)+'.')

    def finished_colliding(self, id, success_value):
        super(Player,self).finished_colliding(id, success_value)
        if success_value:
            if self.parent.is_instance(id, "level_end"):
                pass
                #to add level end code here
            elif self.parent.is_instance(id, "game_end"):
                pass
                #to add game end code here
            elif self.parent.is_instance(id, "mob"):
                self.parent.post_message("You kill the "+self.parent.get_name(id)+".")
                #to add enemy kill code here (xp?)
        else:
            if self.parent.is_instance(id, "door"):
                self.parent.post_message("You open the "+self.parent.get_name(id)+".")

    def die(self):
        if not self.dead:
            self.dead = 1
            self.parent.set_parent(self.id,0)

    def update(self):
        super(Player,self).update()
        self.handle_pickups()

class IDNotAssignedError(Exception):
    """Raised when an entity was asked to give its ID, but it has none assigned."""
    pass
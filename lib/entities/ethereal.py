import entity

import random
from lib.entities import items

class PlayerSpawn(entity.Ethereal):

    def init(self):
        super(PlayerSpawn,self).init()
        self.name = "player_spawn"

class Wound(entity.Ethereal):
    """Class for simulating injuries."""

    def init(self):
        self.set_attributes('00000')
        self.damage = None
        self.threshold = 25
        self.worsen_chance = 0.02
        self.heal_chance = 0.05
        self.name = "Wound"
        self.treated = None
        self.updating = True

    def finished_equipping(self, id, success_value, metadata=None):
        """Callback for when the entity has finished trying to attach an entity to itself."""
        ent = self.parent.get_ent(id)
        if success_value:
            if isinstance(ent, items.HealingSalve):
                self.parent.post_message("You apply the salve.")
            else:
                #self.parent.set_parent(id, self.id)
                pass
        else:
            if isinstance(ent, items.HealingSalve):
                self.parent.post_message("You fail to apply the salve.")

    def treat(self,potency):
        self.treated = potency
        self.set_damage(self.damage-potency)

    def set_damage(self,amount):
        self.damage = amount
        if not self.treated:
            self.name = "Wound ("+str(amount)+")"
        else:
            self.name = "Treated Wound ("+str(amount)+")"

    def update(self):
        if self.damage:
            if 100 > self.damage > self.threshold and not self.treated:
                if random.random()  < self.worsen_chance:
                    self.set_damage(self.damage+1)
            elif self.damage <= self.threshold or self.treated:
                if random.random() < self.heal_chance:
                    self.set_damage(self.damage-1)
        if self.damage <= 0:
            self.parent.set_parent(self.id, 0)


class Bodypart(entity.Ethereal):
    """Class for simulating bodyparts."""

    def __init__(self, parent,id):
        super(Bodypart,self).__init__(parent,id)
        self.name = "bodypart"


class Camera(entity.Ethereal):
    """Simple camera class."""

    def __init__(self, parent,id):
        super(Camera,self).__init__(parent,id)
        self.name = "camera"

    def sync_camera(self, pid):
        """Try to move to player's location."""
        self.parent.move_ent_to_ent(self.id,pid)

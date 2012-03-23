import random
from data.entities import Entity

class Ethereal(Entity):
    """Class for entities like cameras, with which you don't interact ingame."""

    def init(self):
        super(Ethereal,self).init()
        self.set_attributes('00000')

class Wound(Ethereal):
    """Class for simulating injuries."""

    def init(self):
        super(Wound,self).init()
        self.set_attributes('00000')
        self.damage = None
        self.worsen_chance = 20
        self.heal_chance = 20
        self.low_threshold = 25
        self.high_threshold = 50
        self.name = "Wound"
        self.listed = True

    def set_damage(self,amount):
        self.damage = amount
        self.name = "Wound ("+str(amount)+")"

    def update(self):
        if self.damage:
            if 100 > self.damage > self.high_threshold:
                if random.randint(0,100) < self.worsen_chance:
                    self.set_damage(self.damage+1)
            elif self.damage < self.low_threshold:
                if random.randint(0,100) < self.heal_chance:
                    self.set_damage(self.damage-1)
        if self.damage <= 0:
            self.parent.set_parent(self.id, self.parent.garbage_id)

class Bodypart(Ethereal):
    """Class for simulating bodyparts."""

    def init(self):
        super(Bodypart,self).init()
        self.name = "bodypart"
        self.listed = True
        self.acceptable_nodes = None

    def was_equipped(self, id, type):
        """Callback for when entity is being equipped to another entity."""
        success = False
        if self.parent.is_instance(id, "player"):
            self.parent.set_parent(self.id, id)
            success = True
        return success

class Camera(Ethereal):
    """Simple camera class."""

    def init(self):
        super(Camera,self).init()
        self.name = "camera"

class PlayerSpawn(Ethereal):

    def init(self):
        super(PlayerSpawn,self).init()
        self.name = "player_spawn"
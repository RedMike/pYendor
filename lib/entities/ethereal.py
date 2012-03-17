import entity

import random

class Wound(entity.Ethereal):
    """Class for simulating injuries."""

    def init(self):
        super(Wound,self).init()
        self.set_attributes('00000')
        self.damage = None
        self.worsen_chance = 20
        self.heal_chance = 20
        self.name = "Wound"
        self.listed = True

    def set_damage(self,amount):
        self.damage = amount
        self.name = "Wound ("+str(amount)+")"

    def update(self):
        if self.damage:
            if 100 > self.damage > 50:    # TODO: Turn into global constant for ease of use.
                if random.randint(0,100) < self.worsen_chance:
                    self.set_damage(self.damage+1)
            elif self.damage < 20:        # TODO: Turn into global constant for ease of use.
                if random.randint(0,100) < self.heal_chance:
                    self.set_damage(self.damage-1)
        if not self.damage:
            self.parent.set_parent(self.id, 0)


class Bodypart(entity.Ethereal):
    """Class for simulating bodyparts."""

    def init(self):
        super(Bodypart,self).init()
        self.name = "bodypart"
        self.listed = True


class Camera(entity.Ethereal):
    """Simple camera class."""

    def __init__(self, parent,id):
        super(Camera,self).__init__(parent,id)
        self.name = "camera"

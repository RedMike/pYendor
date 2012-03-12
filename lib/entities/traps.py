import entity
import mobs

import random

class Door(entity.Trap):
    """Simple door class, subclass of X{Entity.Trap}."""

    def __init__(self,parent,id):
        super(Door,self).__init__(parent,id)

    def init(self):
        super(Door,self).init()
        self.opened = 0
        self.char = "+"
        self.name = "door"
        self.fgcol = (64, 141, 210)

    def was_collided(self,id,type):
        if type == self.parent.ATTEMPTED_INTERACTION:
            ent = self.parent.get_ent(id)
            if isinstance(ent, mobs.Humanoid) and not self.opened:
                self.open()
                return True
        return False

    def open(self):
        if not self.opened:
            self.opened = 1
            self.char = " "
            self.set_attribute("blocking",0)

    def close(self):
        if self.opened:
            self.opened = 0
            self.char = "+"
            self.set_attribute("blocking",1)

    def door_toggle(self):
        if self.opened:
            self.close()
        else:
            self.open()

class AutoDoor(Door):
    """Automatically-closing door."""

    def __init__(self,parent,id):
        super(AutoDoor,self).__init__(parent,id)

    def init(self):
        super(AutoDoor,self).init()
        self.ticker = -1
        self.timer = 5
        self.updating = True

    def open(self):
        super(AutoDoor,self).open()
        if self.opened:
            self.ticker = self.timer

    def update(self):
        if self.ticker>0:
            self.ticker -= 1
        if not self.ticker:
            self.close()
            self.ticker = -1

class StepTrap(entity.Trap):
    """Trap activated when an NPC steps onto it; subclass and replace was_collided."""

    def __init__(self,parent,id):
        super(StepTrap,self).__init__(parent,id)
        self.set_attribute("blocking", 0)
        self.set_attribute("visible", 0)

    def init(self):
        super(StepTrap,self).init()
        self.targets = ("head", "chest", "back", "hands", "legs")


    def was_collided(self, id, type):
        """When subclassing, remember that a DIRECT interaction type means the entity has successfully moved."""
        pass

    def update(self):
        pass

class TutorialSign1(StepTrap):

    def init(self):
        super(TutorialSign1,self).init()
        self.set_attribute("visible", 1)
        self.char = "T"

    def was_collided(self, id, type):
        ent = self.parent.get_ent(id)
        if isinstance(ent,mobs.Player):
            self.parent.post_message("These next few rooms should prepare you for what's ahead.")
            self.parent.post_message("Be careful.")
        return True


class TutorialSign2(StepTrap):

    def init(self):
        super(TutorialSign2,self).init()
        self.set_attribute("visible", 1)
        self.char = "T"

    def was_collided(self, id, type):
        ent = self.parent.get_ent(id)
        if isinstance(ent,mobs.Player):
            self.parent.post_message("Remember you can press F to jump, and I to interact with your inventory, in which F examines.")
            self.parent.post_message("E to pick up, and E in your inventory to try and mix the two selected items.")
        return True


class TutorialSign3(StepTrap):

    def init(self):
        super(TutorialSign3,self).init()
        self.set_attribute("visible", 1)
        self.char = "T"

    def was_collided(self, id, type):
        ent = self.parent.get_ent(id)
        if isinstance(ent,mobs.Player):
            self.parent.post_message("Press . to pass time. Do this often, as often as you need.")
            self.parent.post_message("Be patient.")
        return True


class ArrowTrap(StepTrap):
    """Arrow trap activated when an NPC steps onto it, then halts for 5 ticks."""

    def init(self):
        super(ArrowTrap,self).init()
        self.ticker = 0
        self.can_fire = True
        self.updating = True
        self.targets = ("chest","back","hands")

    def fire(self,ent):
        self.ticker = 5
        self.can_fire = False
        ent.deal_damage(2,random.choice(self.targets))
        self.char = "!"
        self.set_attribute('visible',True)

    def was_collided(self, id, type):
        if type == self.parent.DIRECT_INTERACTION and self.can_fire:
            ent = self.parent.get_ent(id)
            if isinstance(ent, mobs.Player):
                if not ent.jumping:
                    self.fire(ent)
                    return True
            elif isinstance(ent, entity.Mob):
                self.fire(ent)
                return True
        return False

    def update(self):
        if self.ticker:
            self.ticker -= 1
        if not self.ticker and not self.can_fire:
            self.can_fire = True


class StoneTrap(StepTrap):

    def init(self):
        super(StoneTrap,self).init()
        self.can_fire = True
        self.targets = ("head","legs")

    def fire(self,ent):
        if self.can_fire:
            ent.deal_damage(2, random.choice(self.targets))
            self.can_fire = False
            id = self.parent.add_entity("boulder")
            pos = self.parent.get_pos(self.id)
            self.parent.set_pos(id,pos)

    def was_collided(self, id, type):
        if type == self.parent.DIRECT_INTERACTION and self.can_fire:
            ent = self.parent.get_ent(id)
            if isinstance(ent, mobs.Player):
                if not ent.jumping:
                    self.fire(ent)
                    return True
            elif isinstance(ent, entity.Mob):
                self.fire(ent)
                return True
        return False


class TripTrap(StepTrap):

    def init(self):
        super(TripTrap,self).init()
        self.triggered = False
        self.targets = ("head","legs")

    def fire(self,ent):
        if not self.triggered:
            ent.deal_damage(5, random.choice(self.targets))
            return True
        return False

    def was_collided(self, id, type):
        if type == self.parent.DIRECT_INTERACTION:
            ent = self.parent.get_ent(id)
            if isinstance(ent, mobs.Player):
                if not ent.jumping:
                    return self.fire(ent)
            elif isinstance(ent, entity.Mob):
                return self.fire(ent)
        return False

class MoveTrap(StepTrap):

    def init(self):
        super(MoveTrap,self).init()
        self.direction = random.randint(0,3)

    def fire(self,ent):
        dx, dy = 0,0
        if not self.direction:
            dx, dy = 0, -1
            self.char = chr(24)
        elif self.direction == 1:
            dx, dy = 0, 1
            self.char = chr(25)
        elif self.direction == 2:
            dx, dy = 1, 0
            self.char = chr(26)
        elif self.direction == 3:
            dx, dy = -1, 0
            self.char = chr(27)
        self.set_attribute('visible',True)
        self.parent.move_ent(ent.id,dx,dy)

    def was_collided(self, id, type):
        if type == self.parent.DIRECT_INTERACTION:
            ent = self.parent.get_ent(id)
            if isinstance(ent, mobs.Player):
                if not ent.jumping:
                    self.fire(ent)
                    return True
            elif isinstance(ent, entity.Mob):
                self.fire(ent)
                return True
        return False


class GrateTrap(StepTrap):

    def init(self):
        super(GrateTrap,self).init()
        self.chance = 0.1
        self.char = '#'
        self.set_attribute('visible',True)

    def fire(self,ent):
        dropped = False
        for id in self.parent.get_all_in(ent.id):
            e = self.parent.get_ent(id)
            if isinstance(e, entity.Item):
                if random.random() < self.chance:
                    self.parent.set_pos(id,0)
                    dropped = True
        return dropped

    def was_collided(self, id, type):
        if type == self.parent.DIRECT_INTERACTION:
            ent = self.parent.get_ent(id)
            if isinstance(ent, mobs.Player):
                if not ent.jumping:
                    return self.fire(ent)
            elif isinstance(ent, entity.Mob):
                return self.fire(ent)
        return False


class PillarTrap(entity.Trap):

    def init(self):
        super(PillarTrap,self).init()
        self.set_attribute('fixed', False)
        self.set_attribute('blocking',True)
        self.direction = 0
        self.updating = True
        self.char = "*"

    def was_collided(self, id, type):
        if type == self.parent.ATTEMPTED_INTERACTION:
            ent = self.parent.get_ent(id)
#            if isinstance(ent, entity.Mob):
#                ent.deal_damage(14)
#                return True

    def finished_colliding(self, id, success_value, metadata=None):
        ent = self.parent.get_ent(id)
        if isinstance(ent, entity.Mob):
            ent.deal_damage(14)
            if not self.direction :
                while ent.move(0, -1):
                    pass
            elif self.direction == 1:
                while ent.move(0, 1):
                    pass
            elif self.direction == 2:
                while ent.move(1, 0):
                    pass
            elif self.direction == 3:
                while ent.move(-1, 0):
                    pass
        elif not success_value:
            if self.direction in (0, 2):
                self.direction += 1
            else:
                self.direction -= 1

    def update(self):
        self.direction = int(self.direction)
        if not self.direction :
            if not self.move(0, -1):
                self.direction = 1
        elif self.direction == 1:
            if not self.move(0, 1):
                self.direction = 0
        elif self.direction == 2:
            if not self.move(1, 0):
                self.direction = 3
        elif self.direction == 3:
            if not self.move(-1, 0):
                self.direction = 2

class BladeTrap(entity.Trap):

    def init(self):
        super(BladeTrap,self).init()
        self.set_attribute('fixed', False)
        self.set_attribute('blocking',False)
        self.direction = 0
        self.updating = True
        self.char = "*"
        self.started = False

    def was_collided(self, id, type):
        if type == self.parent.DIRECT_INTERACTION:
            ent = self.parent.get_ent(id)
            if isinstance(ent, mobs.Player):
                if not ent.jumping:
                    ent.deal_damage(15)
                    return True
            elif isinstance(ent, entity.Mob):
                ent.deal_damage(15)

    def finished_colliding(self, id, success_value, metadata=None):
        ent = self.parent.get_ent(id)
        if isinstance(ent, mobs.Player):
            if not ent.jumping:
                ent.deal_damage(20)
                return True
        elif isinstance(ent, entity.Mob):
            ent.deal_damage(20)

    def update(self):
        if self.started:
            self.direction = int(self.direction)
            if not self.direction :
                if self.move(1, 0):
                    self.char = "\\"
            elif self.direction == 1:
                if self.move(0, -1):
                    self.char = "-"
            elif self.direction == 2:
                if self.move(0, -1):
                    self.char = "/"
            elif self.direction == 3:
                if self.move(-1, 0):
                    self.char = "|"
            elif self.direction == 4:
                if self.move(-1, 0):
                    self.char = "\\"
            elif self.direction == 5:
                if self.move(0, 1):
                    self.char = "-"
            elif self.direction == 6:
                if self.move(0, 1):
                    self.char = "/"
            elif self.direction == 7:
                if self.move(1, 0):
                    self.char = "|"
            self.direction += 1
            if self.direction == 8:
                self.direction = 0
        else:
            self.started = True
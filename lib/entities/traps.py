import entity
import mobs

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
        self.timer = 5
        self.updating = True

    def init(self):
        super(AutoDoor,self).init()
        self.ticker = -1

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


    def was_collided(self, id, type):
        """When subclassing, remember that a DIRECT interaction type means the entity has successfully moved."""
        pass

    def update(self):
        pass

class ArrowTrap(StepTrap):
    """Arrow trap activated when an NPC steps onto it, then halts for 5 ticks."""

    def __init__(self,parent,id):
        super(ArrowTrap,self).__init__(parent,id)

    def init(self):
        super(ArrowTrap,self).init()
        self.ticker = 0
        self.can_fire = True
        self.updating = True

    def was_collided(self, id, type):
        if type == self.parent.DIRECT_INTERACTION and self.can_fire:
            ent = self.parent.get_ent(id)
            if isinstance(ent, entity.Mob):
                self.ticker = 5
                self.can_fire = False
                ent.deal_damage(10)
                return True
        return False

    def update(self):
        if self.ticker:
            self.ticker -= 1
        if not self.ticker and not self.can_fire:
            self.can_fire = True

class StoneTrap(StepTrap):

    def __init__(self,parent,id):
        super(StoneTrap,self).__init__(parent,id)

    def init(self):
        super(StoneTrap,self).init()
        self.can_fire = True

    def fire(self,ent):
        ent.deal_damage(100)
        self.can_fire = False
        id = self.parent.add_entity("boulder")
        pos = self.parent.get_pos(self.id)
        self.parent.set_pos(id,pos)

    def was_collided(self, id, type):
        if type == self.parent.DIRECT_INTERACTION and self.can_fire:
            ent = self.parent.get_ent(id)
            if isinstance(ent, entity.Mob):
                self.fire(ent)
                return True
        return False


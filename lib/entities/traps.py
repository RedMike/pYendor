import lib.entity

class Door(lib.entity.Trap):
    """Simple door class, subclass of X{Entity.Trap}."""

    def __init__(self,parent,id):
        super(Door,self).__init__(parent,id)
        self.opened = 0
        self.char = "+"
        self.name = "door"
        self.fgcol = (255, 150, 0)

    def was_collided(self,id,type):
        if type == self.parent.RANGED_INTERACTION:
            ent = self.parent.get_ent(id)
            if isinstance(ent, lib.entity.Humanoid) and not self.opened:
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
        self.ticker = -1

    def open(self):
        super(AutoDoor,self).open()
        if self.opened:
            self.ticker = 5

    def update(self):
        if self.ticker>0:
            self.ticker -= 1
        if not self.ticker:
            self.close()
            self.ticker = -1

class StepTrap(lib.entity.Trap):
    """Trap activated when an NPC steps onto it; subclass and replace was_collided."""

    def __init__(self,parent,id):
        super(StepTrap,self).__init__(parent,id)
        self.set_attribute("blocking", False)

    def was_collided(self, id, type):
        """When subclassing, remember that a DIRECT interaction type means the entity has successfully moved."""
        pass

    def update(self):
        pass

class ArrowTrap(StepTrap):
    """Arrow trap activated when an NPC steps onto it, then halts for 5 ticks."""

    def __init__(self,parent,id):
        super(ArrowTrap,self).__init__(parent,id)
        self.ticker = 0
        self.can_fire = True

    def was_collided(self, id, type):
        if type == self.parent.DIRECT_INTERACTION and self.can_fire:
            ent = self.parent.get_ent(id)
            if isinstance(ent, lib.entity.NPC):
                self.ticker = 5
                self.can_fire = False
                ent.deal_damage(1)
                return True
        return False

    def update(self):
        if self.ticker:
            self.ticker -= 1
        if not self.ticker and not self.can_fire:
            self.can_fire = True

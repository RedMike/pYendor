from data.entities import Entity

class Trap(Entity):
    """Base class for fixed, blocking, unliftable, unusable ents for subclass."""

    def init(self):
        super(Trap,self).init()
        self.set_attributes('11100')

class Door(Trap):
    """Simple door class, subclass of X{Entity.Trap}."""

    def __init__(self,parent,id):
        super(Door,self).__init__(parent,id)

    def init(self):
        super(Door,self).init()
        self.opened = 0
        self.char = "+"
        self.name = "door"
        self.fgcol = (255, 150, 0)

    def was_collided(self,id):
        success = True
        if self.parent.is_instance(id,"mob") and not self.opened:
            self.open()
            success = False
        return success

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

import lib.entity

class Door(lib.entity.Trap):
    """Simple door class, subclass of X{Entity.Trap}."""

    def __init__(self,parent,id):
        super(Door,self).__init__(parent,id)
        self.open = 0
        self.char = "+"
        self.name = "door"
        self.fgcol = (255, 150, 0)

    def was_collided(self,id):
        ent = self.parent.get_ent(id)
        if isinstance(ent, lib.entity.Humanoid) and not self.open:
            self.door_toggle()

    def door_toggle(self):
        if self.open:
            self.open = 0
            self.char = "+"
            self.set_attribute('blocking',1)
        else:
            self.open = 1
            self.char = " "
            self.set_attribute('blocking',0)
import entity
import ethereal

class EquippableItem(entity.Item):

    def __init__(self,parent,id):
        super(EquippableItem,self).__init__(parent,id)


    def init(self):
        super(EquippableItem,self).init()
        self.name = "generic equippable item"

    def check_acceptable(self,node):
        if self.acceptable_nodes:
            return node in self.acceptable_nodes
        return True

class Armor(EquippableItem):

    def __init__(self,parent,id):
        super(Armor,self).__init__(parent,id)

    def init(self):
        super(Armor,self).init()
        self.name = "armor"
        self.rating = 10

class Glove(Armor):

    def __init__(self,parent,id):
        super(Glove,self).__init__(parent,id)

    def init(self):
        super(Glove,self).init()
        self.name = "glove"
        self.acceptable_nodes = ("hands")

class Breastplate(Armor):

    def __init__(self,parent,id):
        super(Breastplate,self).__init__(parent,id)

    def init(self):
        super(Breastplate,self).init()
        self.name = "breastplate"
        self.acceptable_nodes = ("chest")

class Weapon(EquippableItem):

    def __init__(self,parent,id):
        super(Weapon,self).__init__(parent,id)

    def init(self):
        super(Weapon,self).init()
        self.name = "generic weapon"
        self.acceptable_nodes = ("hands")

class Sword(Weapon):

    def init(self):
        super(Sword,self).init()
        self.name = "sword"
        self.char = "/"

class NonEquippableItem(entity.Item):

    def __init__(self,parent,id):
        super(NonEquippableItem,self).__init__(parent,id)

    def init(self):
        super(NonEquippableItem,self).init()
        self.name = "generic unequippable item"

class Backpack(NonEquippableItem):

    def __init__(self,parent,id):
        super(Backpack,self).__init__(parent,id)

    def init(self):
        super(Backpack,self).init()
        self.name = "backpack"

class ClothStrips(NonEquippableItem):

    def init(self):
        super(ClothStrips,self).init()
        self.amount = 5

    def update(self):
        super(ClothStrips,self).update()
        self.amount = int(self.amount)
        if self.amount <= 0:
            self.parent.set_parent(self.id,0)
        self.name = "cloth strips ("+str(self.amount)+")"

    def finished_equipping(self, id, success_value, metadata=None):
        ent = self.parent.get_ent(id)
        if success_value:
            if isinstance(ent, HerbPacket):
                return
            self.parent.set_parent(id, self.id)

    def was_equipped(self, id, type):
        success = False
        ent = self.parent.get_ent(id)
        if isinstance(ent, HerbPacket):
            if self.amount >= 2:
                success = True
                self.amount -= 2
                ent.amount -= 1
                self.update()
                ent.update()
                salve_id = self.parent.add_entity("salve")
                e = self.parent.get_ent(salve_id)
                e.potency = ent.potency
                self.parent.set_parent(salve_id, self.parent.get_parent(self.id))
        return success


class HerbPacket(NonEquippableItem):

    def init(self):
        super(HerbPacket,self).init()
        self.amount = 1
        self.potency = 5

    def update(self):
        super(HerbPacket,self).update()
        self.potency = int(self.potency)
        self.amount = int(self.amount)
        if self.amount <= 0:
            self.parent.set_parent(self.id,0)
        self.name = "herb packet ("+str(self.amount)+")"

    def finished_equipping(self, id, success_value, metadata=None):
        ent = self.parent.get_ent(id)
        if success_value:
            if isinstance(ent, ClothStrips):
                return
            self.parent.set_parent(id, self.id)

    def was_equipped(self, id, type):
        success = False
        ent = self.parent.get_ent(id)
        if isinstance(ent, ClothStrips):
            if ent.amount >= 2:
                success = True
                self.amount -= 1
                ent.amount -= 2
                self.update()
                ent.update()
                salve_id = self.parent.add_entity("salve")
                e = self.parent.get_ent(salve_id)
                e.potency = self.potency
                self.parent.set_parent(salve_id, self.parent.get_parent(self.id))
        return success


class HealingSalve(NonEquippableItem):

    def __init__(self,parent,id):
        super(HealingSalve,self).__init__(parent,id)

    def init(self):
        super(HealingSalve,self).init()
        self.potency = 5
        self.name = "healing salve"

    def was_equipped(self, id, type):
        success = False
        ent = self.parent.get_ent(id)
        if isinstance(ent, ethereal.Wound):
            if self.potency > 4 < ent.damage <= 15:
                success = True
                self.parent.set_parent(self.id, 0)
                ent.treat(self.potency)
        return success
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

    def examine(self):
        s = "It's a bag with "+str(self.amount)+" cloth strips."
        self.parent.post_message(s)

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
                self.parent.post_message("You put together a simple medicinal patch.")
                return
            elif isinstance(ent, ClothStrips):
                self.parent.post_message("You put the strips together in a single bag.")
                return
            elif isinstance(ent, NonEquippableItem):
                return
            self.parent.set_parent(id, self.id)

    def was_equipped(self, id, type):
        success = False
        ent = self.parent.get_ent(id)
        if self != ent:
            if isinstance(ent, HerbPacket):
                if self.amount >= 2:
                    success = True
                    self.amount -= 2
                    ent.amount -= 1
                    salve_id = self.parent.add_entity("salve")
                    e = self.parent.get_ent(salve_id)
                    e.potency = ent.potency
                    self.parent.set_parent(salve_id, self.parent.get_parent(self.id))
                    self.update()
                    ent.update()
            elif isinstance(ent, ClothStrips):
                success = True
                self.amount += ent.amount
                ent.amount -= ent.amount
                self.update()
                ent.update()
        return success


class HerbPacket(NonEquippableItem):

    def init(self):
        super(HerbPacket,self).init()
        self.amount = 1
        self.potency = 5

    def examine(self):
        s = "It's a bag of "+str(self.amount)+" herbs."
        self.parent.post_message(s)
        if self.potency <= 10:
            s = "They don't seem that good for treating wounds."
        elif 10 < self.potency <= 25:
            s = "You think some of them might help treat wounds."
        elif 25 < self.potency <= 50:
            s = "You recognise some of them as effective against infection."
        elif 50 < self.potency <= 70:
            s = "It seems like a good mix for treating wounds."
        elif 70 < self.potency:
            s = "You're confident they're extremely effective."
        self.parent.post_message(s)

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
                self.parent.post_message("You put together a simple medicinal patch.")
                return
            elif isinstance(ent, HerbPacket):
                self.parent.post_message("You mix the herbs from the packets together.")
                return
            elif isinstance(ent, NonEquippableItem):
                return
            self.parent.set_parent(id, self.id)

    def was_equipped(self, id, type):
        success = False
        ent = self.parent.get_ent(id)
        if self != ent:
            if isinstance(ent, ClothStrips):
                if ent.amount >= 2:
                    success = True
                    self.amount -= 1
                    ent.amount -= 2
                    salve_id = self.parent.add_entity("salve")
                    e = self.parent.get_ent(salve_id)
                    e.potency = self.potency
                    self.parent.set_parent(salve_id, self.parent.get_parent(self.id))
                    self.update()
                    ent.update()
            elif isinstance(ent, HerbPacket):
                success = True
                self.amount += ent.amount
                ent.amount -= ent.amount
                self.potency += ent.potency
                self.potency = int(self.potency/2)
                self.update()
                ent.update()
        return success


class HealingSalve(NonEquippableItem):

    def __init__(self,parent,id):
        super(HealingSalve,self).__init__(parent,id)

    def init(self):
        super(HealingSalve,self).init()
        self.potency = 5
        self.name = "healing salve"

    def examine(self):
        s = "It's a bandage covered with herb sprinklings. "
        self.parent.post_message(s)
        if self.potency <= 25:
            s = "It doesn't look like it'll help with anything bigger than a papercut."
        elif 25 < self.potency <= 50:
            s = "It does seem like it'd help with wounds."
        elif 50 < self.potency <= 70:
            s = "It looks effective against wounds."
        elif 70 < self.potency:
            s = "It could probably treat anything short of decapitation."
        self.parent.post_message(s)

    def was_equipped(self, id, type):
        success = False
        ent = self.parent.get_ent(id)
        if isinstance(ent, ethereal.Wound):
            if ent.damage <= 25 or self.potency - 25 >= ent.damage or self.potency > 75:
                if not ent.treated:
                    success = True
                    self.parent.set_parent(self.id, 0)
                    ent.treat(self.potency)
        return success
import entity

class EquippableItem(entity.Item):

    def init(self):
        super(EquippableItem,self).init()
        self.name = "generic equippable item"

class Armor(EquippableItem):

    def init(self):
        super(Armor,self).init()
        self.name = "armor"
        self.rating = 10

    def check_acceptable(self,node):
        if self.acceptable_nodes:
            return node in self.acceptable_nodes
        return True

class Glove(Armor):

    def init(self):
        super(Glove,self).init()
        self.name = "glove"
        self.acceptable_nodes = ("r_hand", "l_hand")

class Breastplate(Armor):

    def init(self):
        super(Breastplate,self).init()
        self.name = "breastplate"
        self.acceptable_nodes = ("chest")

class Weapon(EquippableItem):

    def init(self):
        super(Weapon,self).init()
        self.name = "generic weapon"
        self.acceptable_nodes = ("r_hand", "l_hand")


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

class Container(NonEquippableItem):

    def init(self):
        super(Container,self).init()
        self.name = "box"

class Backpack(Container):

    def init(self):
        super(Backpack,self).init()
        self.name = "backpack"
        self.acceptable_nodes = ['back']
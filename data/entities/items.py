from data.entities import Entity

class Item(Entity):
    """Base non-blocking, visible, liftable and usable entity for subclassing."""

    def init(self):
        super(Item,self).init()
        self.set_attributes('00111')
        self.char = '('
        self.listed = True


class EquippableItem(Item):

    def init(self):
        super(EquippableItem,self).init()
        self.name = "generic equippable item"

    def check_acceptable(self,node):
        if self.acceptable_nodes:
            return node in self.acceptable_nodes
        return False

class Armor(EquippableItem):

    def init(self):
        super(Armor,self).init()
        self.name = "armor"

class Glove(Armor):

    def init(self):
        super(Glove,self).init()
        self.name = "glove"
        self.acceptable_nodes = ("right hand", "left hand")

class Helmet(Armor):

    def init(self):
        super(Helmet,self).init()
        self.name = "helmet"
        self.acceptable_nodes = ("head",)

class Breastplate(Armor):

    def init(self):
        super(Breastplate,self).init()
        self.name = "breastplate"
        self.acceptable_nodes = ("chest")

class Weapon(EquippableItem):

    def init(self):
        super(Weapon,self).init()
        self.name = "generic weapon"
        self.acceptable_nodes = ("right hand", "left hand")

class Sword(Weapon):

    def init(self):
        super(Sword,self).init()
        self.name = "sword"
        self.char = "/"

class NonEquippableItem(Item):

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
        self.acceptable_nodes = ('back',)

    def activated(self, interaction):
        self.parent.post_message("You dump the contents of the backpack onto the floor.")
        for id in self.parent.get_in(self.id):
            self.parent.ent_drop(id)
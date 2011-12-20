
import random

#  Entity has:
#    - attributes = anything from speed to stats to visibility
#
#  EntityMan has:
#    - getClass(str): which returns the class associated with str
#
# Entity DOES NOT care about its position or graphical representation.

class EntityLookup:
    """Simple entity lookup class.

    Subclass and replace getClass with own classes as needed.
    Actual entity management is done in Application.
    """

    def __init__(self):
        pass

    def get_class(self,str):
        """Returns a class as associated by lookup."""
        ret = Entity
        str = str.lower()
        if str == "item":
            ret = Item
        elif str == "npc":
            ret = NPC
        elif str == "beast":
            ret = Beast
        elif str == "player":
            ret = Player
        elif str == "trap":
            ret = Trap
        elif str == "door":
            ret = Door
        return ret


class Entity:
    """Base entity class.

    Basically various attributes and utility methods and callbacks.
    """
    
    def __init__(self, parent):
        """Replace attributes, name and callbacks with ones needed after creation."""
        self.attributes = { 'solid' : 1, 'visible' : 1, 'collidable' : 0,
            'liftable' : 1, 'usable' : 1, 'hidden' : 0}
        self.name = "generic"
        self.parent = parent

    def get_attribute(self, att):
        """Return wanted attribute, or None."""
        if att in self.attributes:
            return self.attributes[att]
        else:
            return None
    
    def set_attribute(self,att,val):
        """Set an attribute to given value."""
        self.attributes[att] = val

    def move(self,x,y):
        self.parent.entity_move(self,x,y)

    def update(self):
        pass


class Item(Entity):
    """Base non-blocking, visible, liftable and usable entity for subclassing."""

    def __init__(self,x,y,tile):
        Entity.__init__(self,x,y,tile)
        self.set_attribute('solid',0)
        self.set_attribute('visible',1)
        self.set_attribute('collidable',0)
        self.set_attribute('liftable',1)
        self.set_attribute('usable',1)


class NPC(Entity):

    def __init__(self,x,y,tile):
        """Base blocking, collidable, unliftable, unusable entity for subclass.

        Also has hp and maximum hp and alive/dead state by default."""
        Entity.__init__(self,x,y,tile)
        self.set_attribute('solid',1)
        self.set_attribute('collidable',1)
        self.set_attribute('liftable',0)
        self.set_attribute('usable',0)

        self.maxhp = 5
        self.hp = 5
        self.dead = 0

    def check_health(self):
        """Verify if dead, and change into corpse of being."""
        if self.hp <= 0 and not self.dead:
            self.dead = 1
            self.set_attribute('liftable',1)
            self.set_attribute('solid',0)
            self.set_attribute('collidable',1)
            self.name += ' corpse'

class Beast(NPC):
    """Subclassed beast entity, can be hit by player."""

    def __init__(self,x,y,tile):
        """Set name afterwards directly, or defaults to 'beast'."""
        NPC.__init__(self,x,y,tile)
        self.name = "beast"

    def update(self):
        """Walks around in circles and regenerates a hitpoint on random chance."""
        if not self.dead:
            dx = random.randint(-1,1)
            dy = random.randint(-1,1)
            regen = random.randint(0,50)
            if regen == 1 and self.hp<5:
                self.hp += 1
            self.move(dx,dy)

class Trap(Entity):
    """Base class for solid, collidable, unliftable, unusable ents for subclass."""

    def __init__(self,x,y,tile):
        Entity.__init__(self,x,y,tile)
        self.set_attribute('solid',1)
        self.set_attribute('collidable',1)
        self.set_attribute('liftable',0)
        self.set_attribute('usable',0)

class Door(Trap):
    """Simple door class openable only by player, subclass of Trap."""

    def __init__(self,x,y,tile):
        Trap.__init__(self,x,y,tile)
        self.open = 0

    def toggle(self):
        if self.open:
            self.open = 0
            self.set_attribute('solid',1)
        else:
            self.open = 1
            self.set_attribute('solid',0)

class Player(NPC):
    """Simple player class."""

    def __init__(self,x,y,tile):
        NPC.__init__(self,x,y,tile)
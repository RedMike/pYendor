
import random

#  Entity has:
#    - attributes = anything from speed to stats to visibility
#
#  EntityMan has:
#    - getClass(str): which returns the class associated with str
#
# Entity DOES NOT care about its position or graphical representation.

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
        self.id = None
        self.drawn = 1
        self.char = '?'
        self.fgcol = (255,255,255)

    def get_id(self):
        if self.id is not None:
            return self.id
        raise IDNotAssignedError

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
        self.parent.try_entity_move_relative(self.id,x,y)

    def update(self):
        pass


class Item(Entity):
    """Base non-blocking, visible, liftable and usable entity for subclassing."""

    def __init__(self,parent):
        Entity.__init__(self,parent)
        self.set_attribute('solid',0)
        self.set_attribute('visible',1)
        self.set_attribute('collidable',0)
        self.set_attribute('liftable',1)
        self.set_attribute('usable',1)
        self.char = '('


class NPC(Entity):

    def __init__(self,parent):
        """Base blocking, collidable, unliftable, unusable entity for subclass.

        Also has hp and maximum hp and alive/dead state by default."""
        Entity.__init__(self,parent)
        self.set_attribute('solid',1)
        self.set_attribute('collidable',1)
        self.set_attribute('liftable',0)
        self.set_attribute('usable',0)
        self.char = '@'
        self.fgcol = (0,255,255)

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

    def __init__(self,parent):
        """Set name afterwards directly, or defaults to 'beast'."""
        NPC.__init__(self,parent)
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

    def __init__(self,parent):
        Entity.__init__(self,parent)
        self.set_attribute('solid',1)
        self.set_attribute('collidable',1)
        self.set_attribute('liftable',0)
        self.set_attribute('usable',0)

class Door(Trap):
    """Simple door class openable only by player, subclass of Trap."""

    def __init__(self,parent):
        Trap.__init__(self,parent)
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

    def __init__(self,parent):
        NPC.__init__(self,parent)
        self.char = '@'
        self.fgcol = (255,255,255)

class Ethereal(Entity):
    """Class for entities like cameras, with which you don't interact ingame."""

    def __init__(self, parent):
        Entity.__init__(self,parent)
        self.set_attribute('solid', 0)
        self.set_attribute('liftable', 0)
        self.set_attribute('collidable', 0)
        self.set_attribute('usable', 0)
        self.set_attribute('visible', 0)
        self.drawn = 0

class Camera(Ethereal):
    """Simple camera class."""

    def __init__(self, parent):
        Ethereal.__init__(self,parent)

    def sync_camera(self, pid):
        """Try to move to player's location."""
        self.parent.try_entity_move_to_entity(self.id,pid)


class EntityError(Entity):
    """Base class for entity errors."""
    pass

class IDNotAssignedError(EntityError):
    """Raised when an entity was asked to give its ID, but it has none assigned."""
    pass
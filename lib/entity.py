#  Entity has:
#    - attributes = anything from speed to stats to visibilities
#
# Entity DOES NOT care about its position.

import random

import entities

class Entity(object):
    """Base entity class.

    Basically various attributes and utility methods.
    """

    def __init__(self, parent, id):
        """Replace attributes, name and callbacks with ones needed after creation."""
        self.attributes = {
                'fixed' : 0,
                'blocking' : 0,
                'visible' : 1,
                'liftable' : 1,
                'usable' : 1
            }
        self.name = "generic"
        self.id = id
        self.char = '?'
        self.fgcol = (255,255,255)
        self.parent = parent

    def was_lifted(self, id, type):
        """Callback for when entity was picked up by another entity."""
        return self.get_attribute('liftable')

    def lifted(self, id, type):
        """Callback for when entity picks up another entity."""
        pass

    def finished_lifting(self, id, success_value, metadata=None):
        """Callback for when the entity has finished trying to pick up another entity."""
        pass

    def collided(self, id, type):
        """Callback for when entity moves I{into} another entity."""
        pass

    def was_collided(self, id, type):
        """Callback for when another entity moves into this entity, returns True for success."""
        return False

    def finished_colliding(self, id, success_value, metadata=None):
        """Callback for when the entity has finished trying to move I{into} another entity."""
        pass

    def get_id(self):
        """Return entity ID, or raise IDNotAssigned."""
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

    def set_attributes(self,atts):
        """Set default attributes; takes a string of the form: 'FBVLU'.

        Fixed, Blocking, Visible, Liftable, Usable.
        """
        if len(atts) != 5:
            return
        assoc = {0:'fixed', 1:'blocking', 2:'visible', 3:'liftable', 4:'usable'}
        for id in range(len(atts)):
            self.attributes[assoc[id]] = int(atts[id])

    def set_name(self,name):
        """Set the entity's name."""
        self.name = name

    def get_name(self):
        """Returns the name of the entity."""
        # TODO: add stuff like a/an, etc.
        return self.name

    def move(self,x,y):
        """Try to move in the (x,y) direction."""
        self.parent.move_ent(self.id,x,y)

    def update(self):
        pass


class Item(Entity):
    """Base non-blocking, visible, liftable and usable entity for subclassing."""

    def __init__(self,parent,id):
        super(Item,self).__init__(parent,id)
        self.set_attributes('00111')
        self.char = '('

class Obstacle(Entity):
    """Base blocking, visible, non-liftable, non-usable entity for subclassing."""

    def __init__(self,parent,id):
        super(Obstacle,self).__init__(parent,id)
        self.set_attributes('01100')
        self.char = 'O'

class Boulder(Obstacle):

    pass

class Trap(Entity):
    """Base class for fixed, blocking, unliftable, unusable ents for subclass."""

    def __init__(self,parent,id):
        super(Trap,self).__init__(parent,id)
        self.set_attributes('11100')


class Ethereal(Entity):
    """Class for entities like cameras, with which you don't interact ingame."""

    def __init__(self, parent,id):
        super(Ethereal,self).__init__(parent,id)
        self.set_attributes('00000')

class Wound(Ethereal):
    """Class for simulating injuries."""

    def __init__(self,parent,id):
        super(Wound,self).__init__(parent,id)
        self.set_attributes('00000')
        self.damage = None
        self.worsen_chance = 20
        self.heal_chance = 20
        self.name = "Wound"

    def set_damage(self,amount):
        self.damage = amount
        self.name = "Wound ("+str(amount)+")"

    def update(self):
        if self.damage:
            if 100 > self.damage > 50:    # TODO: Turn into global constant for ease of use.
                if random.randint(0,100) < self.worsen_chance:
                    self.set_damage(self.damage+1)
            elif self.damage < 20:        # TODO: Turn into global constant for ease of use.
                if random.randint(0,100) < self.heal_chance:
                    self.set_damage(self.damage-1)
        if not self.damage:
            self.parent.set_parent(self.id, 0)


class Bodypart(Ethereal):
    """Class for simulating bodyparts."""

    def __init__(self, parent,id):
        super(Bodypart,self).__init__(parent,id)
        self.name = "bodypart"

class Camera(Ethereal):
    """Simple camera class."""

    def __init__(self, parent,id):
        super(Camera,self).__init__(parent,id)
        self.name = "camera"

    def sync_camera(self, pid):
        """Try to move to player's location."""
        self.parent.move_ent_to_ent(self.id,pid)

class EntityError(Exception):
    """Base class for entity errors."""
    pass

class IDNotAssignedError(EntityError):
    """Raised when an entity was asked to give its ID, but it has none assigned."""
    pass
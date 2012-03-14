#  Entity has:
#    - attributes = anything from speed to stats to visibilities
#
# Entity DOES NOT care about its position.

import random


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
        self.id = id
        self.parent = parent

    def init(self):
        self.name = "generic"
        self.char = '?'
        self.fgcol = (255, 255, 255)
        self.acceptable_nodes = None
        self.updating = False

    def was_equipped(self, id, type):
        """Callback for when entity is being equipped to a humanoid node."""
        success = True
        if self.acceptable_nodes:
            if self.parent.get_name(id) not in self.acceptable_nodes:
                success = False
        return success

    def equipped(self, id, type):
        """Callback for when entity is attaching another entity to itself."""
        pass

    def finished_equipping(self, id, success_value, metadata=None):
        """Callback for when the entity has finished trying to attach an entity to itself."""
        if success_value:
            self.parent.set_parent(id, self.id)

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

    def examine(self):
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
        return self.parent.move_ent(self.id,x,y)

    def update(self):
        if self.parent.parent.distance_from_player(self.id) > 5:
            return


class Mob(Entity):

    def init(self):
        super(Mob,self).init()
        self.set_attributes('01100')
        self.char = '@'
        self.name = 'mob'
        self.fgcol = (0,255,255)
        self.dead = 0
        self.updating = True

    def collided(self, id, type):
        if type == self.parent.ATTEMPTED_INTERACTION:
            ent = self.parent.get_ent(id)
            if isinstance(ent, Mob):
                hit = ent.deal_damage(10)

    def was_collided(self, id, type):
        return True

    def deal_damage(self, amount, target=None):
        # TODO: Add more return information than a boolean.
        self.die()
        return self.check_damage()

    def check_damage(self):
        if not self.dead:
            return False
        return True

    def die(self):
        """Verify if not already dead, and change into corpse of being."""
        if not self.dead:
            self.dead = 1
            id = self.parent.add_entity("item")
            self.parent.set_pos(id,self.parent.get_pos(self.id))
            self.parent.get_ent(id).name = self.name + " corpse"
            self.parent.set_parent(self.id,0)

    def update(self):
        if self.parent.parent.distance_from_player(self.id) > 5:
            return
        if not self.check_damage():
            dx, dy = random.randint(-1,1), random.randint(-1,1)
            self.move(dx, dy)


class Item(Entity):
    """Base non-blocking, visible, liftable and usable entity for subclassing."""

    def __init__(self,parent,id):
        super(Item,self).__init__(parent,id)
        self.set_attributes('00111')

    def init(self):
        super(Item,self).init()
        self.char = '('


class Obstacle(Entity):
    """Base blocking, visible, non-liftable, non-usable entity for subclassing."""

    def __init__(self,parent,id):
        super(Obstacle,self).__init__(parent,id)
        self.set_attributes('01100')

    def init(self):
        super(Obstacle,self).init()
        self.char = 'O'


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


class EntityError(Exception):
    """Base class for entity errors."""
    pass

class IDNotAssignedError(EntityError):
    """Raised when an entity was asked to give its ID, but it has none assigned."""
    pass
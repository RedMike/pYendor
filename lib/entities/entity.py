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
        self.fgcol = (255,255,255)
        self.acceptable_nodes = None
        self.listed = False

    def set_meta_attribute(self,meta,val):
        setattr(self,meta,val)

    def was_equipped(self, id, type):
        """Callback for when entity is being equipped to another entity."""
        success = False
        if self.acceptable_nodes:
            if self.parent.get_name(id) in self.acceptable_nodes:
                self.parent.set_parent(self.id, id)
                success = True
        return success

    def equipped(self, id, type):
        """Callback for when entity is attaching another entity to itself."""
        pass

    def finished_equipping(self, id, success_value, metadata=None):
        """Callback for when the entity has finished trying to attach an entity to itself."""
        pass

    def was_lifted(self, id, type):
        """Callback for when entity was picked up by another entity."""
        if self.get_attribute('liftable'):
            if self.parent.is_instance(id, 'container'):
                self.parent.set_parent(self.id, id)
                return True

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


class Mob(Entity):

    def init(self):
        super(Mob,self).init()
        self.set_attributes('01100')
        self.char = '@'
        self.name = 'mob'
        self.fgcol = (0,255,255)
        self.dead = 0

    def collided(self, id, type):
        if type == self.parent.ATTEMPTED_INTERACTION:
            ent = self.parent.get_ent(id)
            if isinstance(ent, Mob):
                hit = ent.deal_damage(10)

    def was_collided(self, id, type):
        return True

    def deal_damage(self, amount):
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
        if not self.check_damage():
            dx, dy = random.randint(-1,1), random.randint(-1,1)
            self.move(dx, dy)


class Item(Entity):
    """Base non-blocking, visible, liftable and usable entity for subclassing."""

    def init(self):
        super(Item,self).init()
        self.set_attributes('00111')
        self.char = '('
        self.listed = True


class Obstacle(Entity):
    """Base blocking, visible, non-liftable, non-usable entity for subclassing."""

    def init(self):
        super(Obstacle,self).init()
        self.set_attributes('01100')
        self.char = 'O'


class Trap(Entity):
    """Base class for fixed, blocking, unliftable, unusable ents for subclass."""

    def init(self):
        super(Trap,self).init()
        self.set_attributes('11100')


class Ethereal(Entity):
    """Class for entities like cameras, with which you don't interact ingame."""

    def init(self):
        super(Ethereal,self).init()
        self.set_attributes('00000')


class EntityError(Exception):
    """Base class for entity errors."""
    pass

class IDNotAssignedError(EntityError):
    """Raised when an entity was asked to give its ID, but it has none assigned."""
    pass
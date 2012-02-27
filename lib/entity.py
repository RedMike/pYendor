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

    def collided(self, id):
        """Callback for when entity moves I{into} another entity."""
        pass

    def was_collided(self, id):
        """Callback for when another entity moves into this entity."""
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

class Trap(Entity):
    """Base class for fixed, blocking, unliftable, unusable ents for subclass."""

    def __init__(self,parent,id):
        super(Trap,self).__init__(parent,id)
        self.set_attributes('11100')



class NPC(Entity):

    def __init__(self,parent,id):
        """Base blocking, unliftable, unusable entity for subclass."""
        super(NPC,self).__init__(parent,id)
        self.set_attributes('01100')
        self.char = '@'
        self.name = 'kobold'
        self.fgcol = (0,255,255)
        self.dead = 0

    def was_collided(self, id):
        ent = self.parent.get_ent(id)
        if isinstance(ent,NPC):
            self.die()

    def die(self):
        """Verify if dead, and change into corpse of being."""
        if not self.dead:
            self.dead = 1
            self.set_attributes('00110')
            self.name += ' corpse'  # TODO: generalise!

    def update(self):
        if not self.dead:
            dx, dy = random.randint(-1,1), random.randint(-1,1)
            self.move(dx, dy)

class Humanoid(NPC):

    def __init__(self,parent,id):
        super(Humanoid,self).__init__(parent,id)
        self.nodes = { }
        for part in ['head', 'neck', 'chest', 'l_hand', 'r_hand', 'l_leg', 'r_leg', 'back']:
            self.add_node(part)

    def get_node(self,name):
        if name not in self.nodes:
            raise IDNotAssignedError
        return self.nodes[name]

    def get_nodes(self):
        return self.nodes

    def add_node(self,name):
        id = self.parent.add_entity('bodypart')
        self.parent.set_parent(id, self.id)
        self.parent.get_ent(id).name = name
        self.nodes[name] = id

class Player(Humanoid):
    """Simple player class."""

    def __init__(self,parent,id):
        super(Player,self).__init__(parent,id)
        self.char = '@'
        self.fgcol = (255,100,100)
        self.name = "Player"

    def collided(self, id):
        """Called BEFORE interaction itself."""
        super(Player,self).collided(id)
        ent = self.parent.get_ent(id)
        if isinstance(ent,entities.traps.Door):
            if not ent.open:
                self.parent.post_message("You open the "+self.parent.get_name(id)+".")
        elif isinstance(ent,NPC):
            if not ent.dead:
                self.parent.post_message("You slice at the "+self.parent.get_name(id)+".")

    def update(self):
        pass


class Ethereal(Entity):
    """Class for entities like cameras, with which you don't interact ingame."""

    def __init__(self, parent,id):
        super(Ethereal,self).__init__(parent,id)
        self.set_attributes('00000')

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
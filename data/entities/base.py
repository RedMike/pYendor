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

    def finished_dropping(self, id, success_value):
        pass

    def was_dropped(self, ancestor):
        success = False
        if self.get_attribute('liftable'):
            self.parent.set_pos(self.id,self.parent.get_abs_pos(ancestor))
            success = True
        return success

    def activated(self, id):
        """Callback for when entity is activated."""
        return self.get_attribute('usable')

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
        return False

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

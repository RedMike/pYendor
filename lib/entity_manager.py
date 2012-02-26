import entity


# Entities are kept in a dictionary as an id.
# This allows for fast checking for entities in tiles, and raises
# only a slight problem in keeping them in sync. Picking a class for
# add_entity is done via the entity manager transparently. Send a string
# like 'item'. ID lookup is in entity_list. Scheduling IDs are in entity_schedules.
# If the value in entity_pos is a single int, it is an ID and the entity is CONTAINED
# by that other entity. If you call get_ent_pos, it will return the position of the
# container, recursing up to the top-level entity. Call get_ent_contain returns the ID
# of the containing entity, or None if not contained.

class EntityManager(object):
    """Manager class for Entities.

    Contains class_lookup for string<->class associations.
    lookup contains the ID <-> object referencing.
    positions contains the position of the entity, as either a tuple (x,y) or an int id. For IDs, get_pos searches
    recursively and returns the position of the top-level container.
    schedules contains the IDs of the scheduling tasks assigned to each entity.
    cur_id is the current free ID to be assigned.
    """

    def __init__(self,parent):
        self.class_lookup = EntityLookup()
        self.lookup = { }
        self.positions = { }
        self.schedules = { }
        self.parent = parent
        self.scheduler = parent.scheduler
        self.cur_id = 0

    def add_entity(self, type,delay=None):
        """Adds a new entity of type to entity_list, and returns its ID.

        Sets the parent property of the entity.
        """
        id = self.cur_id
        type = self.class_lookup.get_class(type)
        self.lookup[id] = type(self,id)
        self.set_attribute(id, 'delay', delay)
        if delay is not None:
            self.schedule(self.scheduler, id)
        self.adjust_cur_id()
        return id

    def get_ids(self):
        """Returns an iterator over the ids of entities."""
        return self.lookup.iterkeys()

    def get_ent(self,id):
        """Returns entity of id or None."""
        return self.lookup.get(id,None)

    def get_at(self,x,y):
        """Returns list of ids of entities at a position or None."""
        if (x,y) in self.positions.itervalues():
            ret = [ ]
            for id in self.positions:
                if self.positions[id] == (x,y):
                    ret.append(id)
            return ret
        return None

    def get_in(self,ent):
        """Returns list of ids of entities contained directly by ent or None."""
        if ent in self.positions.itervalues():
            ret = [ ]
            for id in self.positions:
                if self.positions[id] == ent:
                    ret.append(id)
            return ret
        return None

    def get_pos(self,id):
        """Returns (x,y) or id of container for entity."""
        ent = self.get_ent(id)
        if ent is None:
            raise IDNotFound
        pos = self.positions[id]
        if isinstance(pos,int):
            pos = self.get_pos(pos)
        return pos

    def set_attribute(self, id, att, val):
        """Sets the entity's attribute to the given value."""
        ent = self.get_ent(id)
        if ent is None:
            raise IDNotFound
        ent.set_attribute(att, val)

    def get_attribute(self, id, att):
        """Returns the entity's attribute or None."""
        ent = self.get_ent(id)
        if ent is None:
            raise IDNotFound
        return ent.get_attribute(att)

    def get_name(self, id):
        """Returns the entity's name."""
        ent = self.get_ent(id)
        if ent is None:
            raise IDNotFound
        return ent.get_name()

    def set_sched(self, ent, sched):
        """Cancels the current schedule for an entity and sets a new id as its main."""
        if ent in self.schedules:
            if self.schedules[ent] is not None:
                sched.cancel_schedule(self.schedules[ent])
        self.schedules[ent] = sched

    def get_sched(self, ent):
        """Returns the scheduler id for entity or None."""
        if ent in self.schedules:
            return self.schedules[ent]
        return None

    def schedule(self, sched, id):
        """Schedules the entity in the scheduler according to its current delay."""
        if id in self.schedules:
            if self.schedules[id] is not None:
                sched.cancel_schedule(self.schedules[id])
        ent = self.get_ent(id)
        if ent is None:
            raise IDNotFound
        delay = ent.get_attribute('delay')
        if delay is not None:
            self.schedules[id] = sched.add_schedule((ent.update, (), delay))

    def move_ent_to_ent(self,id,id2):
        """Passes call to try to move an entity to another into relative coords."""
        ret = self.get_pos(id2)
        x, y = ret
        ret = self.get_pos(id)
        ex, ey = ret
        self.move_ent(id, x-ex, y-ey)

    def move_ent(self,id,x,y):
        """Tries to move an entity in a relative direction, with collision checking."""
        if self.parent.collision_check(id,x,y):
            pos = self.get_pos(id)
            pos = (pos[0]+x, pos[1]+y)
            self.set_pos(id,pos)

    def set_pos(self, id, obj):
        """Sets the entity's position to the given obj; can be tuple (x, y), or id of other entity."""
        if isinstance(obj,int):
            if self.get_ent(obj) is None:
                raise IDNotFound
        self.positions[id] = obj

    def adjust_cur_id(self):
        self.cur_id += 1  # TODO: Make it so it fills back gaps in IDs by destroyed ents.

class EntityLookup:
    """Simple entity lookup class.

    Subclass and replace initialisation with own classes as needed.
    Actual entity management is done in EntityManager.
    """

    def __init__(self):
        self.lookup = dict()
        self.lookup['item'] = entity.Item
        self.lookup['npc'] = entity.NPC
        self.lookup['player'] = entity.Player
        self.lookup['camera'] = entity.Camera
        self.lookup['bodypart'] = entity.Bodypart

    def get_class(self,str):
        """Returns a class as associated by lookup."""
        return self.lookup.get(str.lower(),entity.Entity)


class IDNotFound(Exception):
    """An inexistent ID was used."""
    pass


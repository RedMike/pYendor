from data.entities import Lookup

class EntityManager(object):
    """Manager class for Entities.

    Contains class_lookup for string <-> class associations/instance type checking.
    lookup contains the ID <-> object referencing.
    positions contains the position of the entity, or None.
    parents contains the ID of the containing entity, or None.
    schedules contains the IDs of the scheduling tasks assigned to each entity.
    cur_id is the current free ID to be assigned.
    Entity ID #0 is 'garbage collection' of entities. Parent to this to remove next tick.
    """

    def __init__(self,parent):
        self.class_lookup = Lookup()
        self.lookup = { }
        self.positions = { }
        self.parents = { }
        self.schedules = { }
        self.parent = parent
        self.scheduler = parent.scheduler

        self.cur_id = 0
        self.garbage_id = self.add_entity("ethereal")
        self.set_pos(self.garbage_id,(0, 0))

    def __len__(self):
        return len(self.lookup)

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.lookup[item]
        elif isinstance(item, tuple) and len(item) == 2:
            return self.get_at(*item)
        else:
            raise NotImplemented

    def __iter__(self):
        return self.lookup.iterkeys()

    def __contains__(self, item):
        return item in self.lookup

    def is_instance(self, id, lookup):
        return isinstance(self[id], self.class_lookup.get_class(lookup))

    def post_message(self, msg):
        """Convenience method for entities to call to post messages to the message window."""
        self.parent.add_messages((msg,))

    def add_entity(self, type, delay=10):
        """Adds a new entity of type to entity_list, and returns its ID."""
        id = self.cur_id
        self.adjust_cur_id()
        type = self.class_lookup.get_class(type)
        self.lookup[id] = type(self,id)
        self.lookup[id].init()
        self.set_attribute(id, 'delay', delay)
        if delay is not None:
            self.schedule(self.scheduler, id)
        return id

    def get_at(self,x,y):
        """Returns list of ids of entities at a position or an empty tuple."""
        if (x,y) in self.positions.itervalues():
            ret = [ ]
            for id in self.positions:
                if self.positions[id] == (x,y):
                    ret.append(id)
            return ret
        return ()

    def get_in(self,ent):
        """Returns list of ids of entities contained directly by ent or an empty tuple."""
        if ent in self.parents.itervalues():
            ret = [ ]
            for id in self.parents:
                if self.parents[id] == ent:
                    ret.append(id)
            return ret
        return ()

    def get_pos(self,id):
        """Returns (x,y) of entity if not contained, or None."""
        if id not in self:
            raise IDNotFound
        return self.positions[id]

    def get_abs_pos(self,id):
        """Returns (x,y) of entity; Recurses up container entities to return real position."""
        if id not in self:
            raise IDNotFound
        cur_id = id
        pos = None
        while not pos and cur_id is not None:
            pos = self.positions[cur_id]
            cur_id = self.parents[cur_id]
        return pos

    def get_parent(self,id):
        """Returns ID of directly containing entity or None."""
        if id not in self:
            raise IDNotFound
        return self.parents[id]

    def get_ancestor(self,id):
        """Returns ID of top containing entity or None."""
        if id not in self:
            raise IDNotFound
        if self.parents[id] is None:
            return id
        return self.get_ancestor(self.parents[id])

    def set_attribute(self, id, att, val):
        """Sets the entity's attribute to the given value."""
        if id not in self:
            raise IDNotFound
        self[id].set_attribute(att, val)

    def get_attribute(self, id, att):
        """Returns the entity's attribute or None."""
        if id not in self:
            raise IDNotFound
        return self[id].get_attribute(att)

    def get_name(self, id):
        """Returns the entity's name."""
        if id not in self:
            raise IDNotFound
        return self[id].get_name()

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
        if id not in self:
            raise IDNotFound
        delay = self[id].get_attribute('delay')
        if delay is not None:
            self.schedules[id] = sched.add_schedule((self[id].update, (), delay))


    def ent_lift(self, ent1, ent2):
        """Lifter ent1 attempts to lift liftee ent2."""
        ent = self[ent1]
        victim = self[ent2]
        ent.lift(ent2)
        success = victim.was_lifted(ent1)
        ent.finished_lifting(ent2,success)
        return success

    def ent_equip(self, ent1, ent2):
        """Equipper ent1 attempts to equip equipment to ent2."""
        ent = self[ent1]
        victim = self[ent2]
        ent.equip(ent2)
        success = victim.was_equipped(ent1)
        ent.finished_equipping(ent2, success)
        return success

    def ent_collide(self, ent1, ent2):
        """Collider ent1 attempts to move onto tile of ent2."""
        ent = self[ent1]
        victim = self[ent2]
        ent.collide(ent2)
        success = victim.was_collided(ent1)
        ent.finished_colliding(ent2, success)
        return success

    def ent_activate(self, id):
        return self[id].activated()

    def ent_drop(self, ent_id):
        ent = self[ent_id]
        ancestor = self.get_ancestor(ent_id)
        self[ancestor].drop(ent_id)
        success = ent.was_dropped(ancestor)
        self[ancestor].finished_dropping(ent_id, success)

    def ent_use(self, ent1, ent2):
        """Used ent1 attempts to use target ent2."""
        ent = self[ent1]
        victim = self[ent2]
        if ent != victim:
            ok = self.ent_equip(ent1, ent2)
            if not ok:
                self.ent_lift(ent1, ent2)
        else:
            self.ent_activate(ent1)

    def move_ent(self,id,x,y):
        """Tries to move an entity in a relative direction, with collision checking and interaction."""
        pos = self.get_pos(id) or (0,0)
        pos = (pos[0] + x, pos[1] + y)
        can_move = True
        #check for interactions to raise
        for victim_id in self[(pos[0],pos[1])]:
            if id is not victim_id:
                can_move = self.ent_collide(id, victim_id)
        #check for collisions
        if self.parent.collision_check(id,x,y) and can_move:
            self.set_pos(id,pos)

    def move_ent_to_ent(self,id,id2):
        """Passes call to try to move an entity to another into relative coords."""
        x, y = self.get_pos(id2) or (0,0)
        ex, ey = self.get_pos(id) or (0,0)
        self.move_ent(id, x-ex, y-ey)

    def set_pos(self, id, pos):
        """Sets the entity's position to the given tuple, unsetting parent."""
        if id not in self:
            raise IDNotFound
        self.positions[id] = pos
        self.parents[id] = None

    def set_parent(self, id, parent_id):
        """Sets the entity's containing entity to the given ID, unsetting its position."""
        if id not in self and parent_id not in self:
            raise IDNotFound
        self.positions[id] = None
        self.parents[id] = parent_id

    def adjust_cur_id(self):
        self.cur_id += 1  # TODO: Make it so it fills back gaps in IDs by destroyed ents.

    def save(self):
        """Returns a list of strings representing save-format data."""
        return ["Testing ents.", "Done."]



class IDNotFound(Exception):
    """An inexistent ID was used."""
    pass


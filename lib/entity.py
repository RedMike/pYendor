
import random

#  Entity has:
#    - tile = graphical representation
#    - x
#    - y
#    - attributes = anything from speed to stats to visibility
#
#  EntityMan has:
#    - getClass(str): which returns the class associated with str
#
#  Entity
#  |
#  +-Mob
#  |
#  +-Camera

class EntityMan:
    """Simple entity manager class.

    Subclass and replace getClass with own classes as needed.
    Actual entity management is done in Application.
    """

    def __init__(self):
        pass

    def getClass(self,str):
        """Returns a class as associated by the manager."""
        ret = Entity
        if str == "item":
            ret = Item
        elif str == "talker":
            ret = Talker
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

class Tile:
    """Tile utility class.

    Contains information about a tile. Standardised to:
        * x
        * y
        * background color
        * character
        * foreground color
        * background set (1 = sets, 0 = doesn't set)
        * blocks (1 = wall-like, 0 = floor-like)
        * blocks light ((unused))
    """

    def __init__(self,x,y,bgcol,char,fgcol,bgset,blocks,blocksLight):
        (self.x, self.y, self.bgcol, self.char, self.fgcol, self.bgset,
            self.blocks, self.blocksLight) = (x,y,bgcol,char,fgcol,bgset,
            blocks,blocksLight)

    def copy(self):
        """Returns a new instance copy of the tile."""
        return Tile(self.x,self.y,self.bgcol,self.char,self.fgcol,self.bgset,self.blocks,self.blocksLight)



class Entity:
    """Base entity class.

    Basically a tile with a position and various attributes.
    Can contain other entities and return its inventory, and can be scheduled."""
    
    def __init__(self,x,y,tile):
        """Initialisation method.

        Tile can be a tuple or a tile with irrelevant x and y properties.
        List is in the format (bgcol, char, fgcol, bgset, blocks, blocksLight).
        Contained objects are given an internal inventory ID.
        Events are by default triggered when the entity is collided with."""
        if isinstance(tile,Tile):
            tile = [tile.bgcol,tile.char,tile.fgcol,tile.bgset,tile.blocks,tile.blocksLight]
        tile = [x,y] + tile
        self.tile = Tile(*tile)
        self.x, self.y = x, y
        self.atts = { 'solid' : 1, 'visible' : 1, 'collidable' : 0,
            'liftable' : 1, 'usable' : 1, 'givelight' : 0, 'hidden' : 0}
        self.collision, self.contained = -1, 0
        self.contains, self.events = [], []
        self.moveCallback = -1
        self.name = "generic"
        
    def contain(self,ent):
        """Entity has been contained, makes itself disappear."""
        self.contained = 1
        self.setAttribute('hidden',1)
        self.x = -1
        self.y = -1

    def removed(self,ent):
        """Entity has been removed from inventory, unhide and update position."""
        self.contained = 0
        self.setAttribute('hidden',0)
        self.x = ent.x
        self.y = ent.y

    def getContained(self,ent):
        """Return the internal ID of the given entity or -1."""
        for i in range(len(self.contains)-1):
            if self.contains[i] == ent:
                return i
        return -1

    def containObject(self,ent):
        """Contain an entity in inventory and return its id."""
        self.contains.append(ent)
        ent.contain(self)
        return len(self.contains)-1

    def uncontainObject(self,id):
        """Remove an entity from inventory."""
        self.contains[id].removed(self)
        del self.contains[id]

    def returnInventory(self):
        """Return inventory as simple list."""
        return self.contains

    def gridInventory(self):
        """Return inventory in format: [ id : [character, color, name, obj] ]."""
        id = 1
        ret = []
        for ent in self.contains:
            it = [ent.tile.char, ent.tile.fgcol, ent.name, ent]
            ret.append([id, it])
            id += 1
        return ret

    def getTile(self):
        """Return tile."""
        return self.tile
    
    def getAttribute(self,att):
        """Return wanted attribute, or -1."""
        if att in self.atts:
            return self.atts[att]
        else:
            return -1
    
    def setAttribute(self,att,val):
        """Set an attribute to given value."""
        self.atts[att] = val

    def setCollisionCheck(self,fct):
        """Set the current collision check.

        This function gets evaluated on every movement.
        On returned 1, movement is allowed.
        On returned 0, movement is stopped.
        Set to -1 for no collision checking."""
        self.collision = fct

    def collidedWith(self,ent):
        """Default collided checking runs events in self.events.

        Events are in format (function, (arg1, arg2, arg3))."""
        for set in self.events:
            fct = set[0]
            opts = set[1]
            fct(*opts)
        return []

    def relMove(self,dx,dy):
        """Try to move in the relative direction (dx, dy)."""
        self.move(self.x+dx,self.y+dy)

    def move(self,x,y):
        """Try to move to (x, y).

        If the collision function is not -1, call. Actually move on returned 1.
        If the move callback is not -1, call it with self and position moved to.
        """
        #print 'Trying to move to ' + str(x)+':'+str(y)
        if not isinstance(self.collision,int):
            #print 'Collision testing.'
            if self.collision(self,x,y):
                if self.moveCallback != -1:
                    self.moveCallback(self,x,y)
                #print 'No collision.'
                self.x = x
                self.y = y
                self.tile.x = x
                self.tile.y = y
        else:
            if self.moveCallback != -1:
                self.moveCallback(self,x,y)
            self.x = x
            self.y = y
            self.tile.x = x
            self.tile.y = y
    
    def copy(self):
        """Return a copy of the entity."""
        return Entity(self.x,self.y,self.tile.toList())

    def update(self):
        pass


class Item(Entity):
    """Base non-blocking, visible, liftable and usable entity for subclassing."""

    def __init__(self,x,y,tile):
        Entity.__init__(self,x,y,tile)
        self.setAttribute('solid',0)
        self.setAttribute('visible',1)
        self.setAttribute('collidable',0)
        self.setAttribute('liftable',1)
        self.setAttribute('usable',1)


class NPC(Entity):

    def __init__(self,x,y,tile):
        """Base blocking, collidable, unliftable, unusable entity for subclass.

        Also has hp and maximum hp and alive/dead state by default."""
        Entity.__init__(self,x,y,tile)
        self.setAttribute('solid',1)
        self.setAttribute('collidable',1)
        self.setAttribute('liftable',0)
        self.setAttribute('usable',0)

        self.maxhp = 5
        self.hp = 5
        self.dead = 0

    def checkHealth(self):
        """Verify if dead, and change into corpse of being."""
        if self.hp <= 0 and not self.dead:
            self.dead = 1
            self.setAttribute('liftable',1)
            self.setAttribute('solid',0)
            self.setAttribute('collidable',1)
            self.name += ' corpse'
            
    def pickUp(self,objs):
        """Pick up object, return list of messages to display."""
        for obj in objs:
            self.containObject(obj)
        return []

    def drop(self,ids):
        """Drop objects in list of inventory ids."""
        for id in ids:
            self.uncontainObject(id)


class Beast(NPC):
    """Subclassed beast entity, can be hit by player."""

    def __init__(self,x,y,tile):
        """Initialisation method.

        Set name afterwards directly, or defaults to 'beast'."""
        NPC.__init__(self,x,y,tile)
        self.name = "beast"


    def collidedWith(self,ent):
        """Subclassed collision method returning player messages.

        Only good for a game where only the player can hurt things.
        To be used as an example or a debugging test only."""
        ret = []
        if isinstance(ent,Player):
            if not self.dead:
                self.hp -= 1
                first = "You hit the "+self.name+". "
                self.checkHealth()
                if self.dead:
                    first += "It dies."
                    self.setAttribute('solid',0)
                    self.setAttribute('liftable',1)
                    self.tile.char = "%"
                    self.tile.blocks = 0
                ret.append(first)
            else:
                first = "You trample the corpse."
                ret.append(first)
        return ret

    def update(self):
        """Walks around in circles and regenerates a hitpoint on random chance."""
        if not self.dead:
            dx = random.randint(-1,1)
            dy = random.randint(-1,1)
            regen = random.randint(0,50)
            if regen == 1 and self.hp<5:
                self.hp += 1
            self.relMove(dx,dy)

class Trap(Entity):
    """Base class for solid, collidable, unliftable, unusable ents for subclass."""

    def __init__(self,x,y,tile):
        Entity.__init__(self,x,y,tile)
        self.setAttribute('solid',1)
        self.setAttribute('collidable',1)
        self.setAttribute('liftable',0)
        self.setAttribute('usable',0)


class Door(Trap):
    """Simple door class openable only by player, subclass of Trap."""

    def __init__(self,x,y,tile):
        Trap.__init__(self,x,y,tile)
        self.open = 0

    def collidedWith(self,ent):
        """Collision function only for player, until opened."""
        ret = []
        if isinstance(ent,Player) and not self.open:
            self.open = 1
            self.tile.char = ' '
            self.tile.blocks = 0
            self.tile.blocksLight = 0
            self.setAttribute('solid',0)
            self.setAttribute('collidable',0)
            ret.append('You open the door.')
        return ret


class Player(NPC):
    """Simple player class."""

    def __init__(self,x,y,tile):
        NPC.__init__(self,x,y,tile)

    def pickUp(self,objs):
        """Pick up object, return list of messages to display."""
        x = 'You pick up '
        for obj in objs:
            x += 'the '+obj.name+', '
            self.containObject(obj)
        if len(objs) != 0:
            x = x[:-2] + '.'
            return [x]
        return []

    def collidedWith(self,ent):
        """Collision method has every NPC or subclass ignore player."""
        ret = []
        if isinstance(ent,NPC):
            ret.append("The "+ent.name+" brushes against you, then walks away.")
        return ret

class Talker(Item):
    """Simple entity that prints a message on collision, collidable by default.
    
    Use setMessage to set the message it prints after creating.
    Use setToggled to set if it always fires, or just the first time."""

    def __init__(self,x,y,tile):
        """Initialisation method.

        Can't set message or firing type during initialisation, call afterwards."""
        Item.__init__(self,x,y,tile)
        self.setAttribute('collidable',1)
        self.msg = "Generic message. Something went wrong."
        self.fired = -1

    def setMessage(self,str):
        """Set message to be printed, single line by default."""
        self.msg = str

    def setToggled(self,nr):
        """Set firing type, -1 means toggle every time, 0 means fire once."""
        self.fired = nr

    def collidedWith(self,ent):
        """Default collision method that only prints the message for a Player."""
        ret = []
        if (self.fired == 0 or self.fired == -1) and not self.contained:
            if isinstance(ent,Player):
                ret.append(self.msg)
                if not self.fired:
                    self.fired = 1
        return ret
    
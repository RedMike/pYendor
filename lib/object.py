
import entity

#Objects are game entities with special conditions
#They're independent from entities and are generally customised to a particular
#  purpose. Like a camera that follows a player. They're also not graphical.
#
# Object
# |
# +-Camera

class Object:

    def __init__(self,x,y,delay=1):
        self.x = x
        self.y = y
        self.delay = delay

    def getAttribute(self,att):
        if att=='delay':
            return self.delay

    def update(self):
        pass

class Camera(Object):

    def __init__(self,x,y,delay=1,player=0):
        Object.__init__(self,x,y,delay)
        self.player = player

    def sortTiles(self,tiles,dx,dy):
        #x,y,bgcol,char,fgcol,bgset,blocks,blocksLight
        ret = []
        for tile in tiles:
            tile = tile.copy()
            x1 = tile.x
            y1 = tile.y
            x2 = self.x
            y2 = self.y
            if abs(x2-x1)<=dx/2 and abs(y2-y1)<=dy/2:
                tile.x = dx/2 - (x2-x1)
                tile.y = dy/2 - (y2-y1)
                ret.append(tile)
        return ret


    def sortEnts(self,tiles,dx,dy):
        #x,y,bgcol,char,fgcol,bgset,blocks,blocksLight
        ret = []
        for ent in tiles:
            ent = entity.Entity(ent.x,ent.y,ent.tile)
            tile = ent.tile
            x1 = ent.x
            y1 = ent.y
            x2 = self.x
            y2 = self.y
            if (abs(x2-x1)<=dx/2 and abs(y2-y1)<=dy/2):
                ent.x = dx/2 - (x2-x1)
                ent.tile.x = dx/2 - (x2-x1)
                ent.y = dy/2 - (y2-y1)
                ent.tile.y = dy/2 - (y2-y1)
                if ent.tile.bgset == 1 or ent.tile.char != ' ':
                    ret.append(ent)
        return ret

    def update(self):
        if self.player != 0:
            self.x = self.player.x
            self.y = self.player.y
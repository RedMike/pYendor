

import random
import data.libtcodpy as libtcod

# Generator -> Map -> Tile
# Tiles are ONLY tiles. They don't care about what is on them.
#   The Application worries about that and sorts what gets shown,
#   and what not.
#
# They do, however, have a base colour (bg) and a preferred fg,
#   if no items are on it, that's the fg chosen.

# Tiles have:
#    - bgcol
#    - char
#    - fgcol
#    - blocks
#    - blocksLight
# (bgcol, char, fgcol, blocks, blocksLight)

# (basic) Generator has:
#    - floorTile
#    - wallTile
#    - width
#    - height

class Generator:
    
    def __init__(self,floor,wall,w,h):
        self.floor = Tile(*floor)
        self.wall = Tile(*wall)
        self.width = w
        self.height = h
        self.map = Map(w,h)
    
    def genMap(self):
        #generation algorithm
        #floor = Tile(0,0,(200,200,200),' ',(100,100,100),1,0,0)
        #wall = Tile(0,0,(50,50,80),'#',(0,0,0),1,1,1)
        self.map.clear()
        self.map.addRect(self.floor,2,2,10,12)
        self.map.addRect(self.floor,25,4,12,15)
        self.map.addRect(self.floor,10,8,20,1)
        self.map.addRect(self.wall,32,9,2,4)
        self.map.addRect(self.wall,5,8,2,1)
        return self.map

class BasicGenerator(Generator):

    def genMap(self):
        self.map.clear()
        roughness = 50
        length = 100
        wind = 100
        if length>=self.width-2:
            length = self.width-3
        startx = 1
        x = startx
        y = self.height/2-2
        height = 3
        for i in range(length):
            self.map.addRect(self.floor,x,y,1,height)

            ##extensions
            #pillars
            if height>6:
                nrPillars = random.randint(0,3)
                for i in range(nrPillars):
                    ty = random.randint(0,height)
                    ty += y
                    self.map.addRect(self.wall,x,ty,1,1)

            #roughness
            if random.randint(0,100)<roughness:
                #increase/decrease width
                height += random.randint(-2,2)
                if height<3:
                    height = 3
                if y+height>=self.height:
                    height = self.height-y-1

            #windyness
            if random.randint(0,100)<wind:
                #move left/right
                y += random.randint(-2,2)
                if y<1:
                    y = 1
                if y+height>=self.height:
                    y = self.height-height-1
            
            x+=1
        return self.map


class Map:
    
    def __init__(self,w,h):
        self.tiles = []
        self.width = w
        self.height = h


    def addTile(self,tile):
        if tile.x>0 and tile.x<self.width:
            if tile.y>0 and tile.y<self.height:
                if self.getTile(tile.x,tile.y) != None:
                    self.tiles.remove(self.getTile(tile.x,tile.y))
                self.tiles.append(tile.copy())
    
    def addRect(self,tile,x,y,w,h):
        for i in range(w):
            for j in range(h):
                tile.x = x+i
                tile.y = y+j
                self.addTile(tile)

    def addCircle(self,tile,x,y,r):
        r = r/2
        for i in range(-r,r):
            for j in range(-r,r):
                if float((i*i+j*j)**(1/2.0)) < r:
                    tile.x = i+x
                    tile.y = j+y
                    self.addTile(tile)
    
    def getTiles(self):
        ret = []
        ret = self.tiles
        return ret

    
    def getRect(self,x,y,r,onlyFree=0):
        ret = []
        for tile in self.tiles:
            if abs(x-tile.x)<r and abs(y-tile.y)<r:
                if (onlyFree and not tile.blocks) or (not onlyFree):
                    ret.append(tile)
        return ret

    def getRightRect(self,x,y,w,h):
        ret = []
        for tile in self.tiles:
            if tile.x>=x and tile.y>=y and tile.x<x+w and tile.y<y+h:
                ret.append(tile)
        return ret
    
    def getTile(self,x,y):
        ret = self.getRect(x,y,1)
        if ret != []:
            ret = ret[0]
        else:
            ret = None
        return ret

    def loadTiles(self,tiles):
        for tile in tiles:
            self.addTile(Tile(*tile))
    
    def fill(self,tile):
        self.clear()
        self.addRect(tile,0,0,self.width,self.height)
        
    def clear(self):
        self.tiles = []


          
class Tile:
    
    def __init__(self,x,y,bgcol,char,fgcol,bgset,blocks,blocksLight=0):
        self.bgcol = bgcol
        self.char = char
        self.fgcol = fgcol
        self.blocks = blocks
        self.blocksLight = blocksLight
        self.bgset = bgset
        self.x = x
        self.y = y
    
    def copy(self):
        return Tile(self.x,self.y,self.bgcol,self.char,self.fgcol,self.bgset,self.blocks,self.blocksLight)
    
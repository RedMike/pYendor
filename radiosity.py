#! /usr/bin/python

import random, time
import data.libtcodpy as libtcod
import lib.graphics as gr


__author__="mike"
__date__ ="$Apr 30, 2011 05:45:11 PM$"

class Tile:

    def __init__(self,x,y,bgcol):
        self.bgcol = bgcol
        self.char = ' '
        self.fgcol = (255,255,255)
        self.blocks = 0
        self.blocksLight = 0
        self.bgset = 1
        self.x = x
        self.y = y
        self.tick = 0
        self.ticker = 0

class Map:

    def __init__(self):
        self.map = []
        for i in range(30):
            for j in range(30):
                self.map.append(Tile(i,j,(255,255,255)))

    def getTile(self,x,y):
        ret = 0
        for tile in self.map:
            if tile.x == x and tile.y == y:
                ret = tile
        return ret

    def tick(self):
        for tile in self.map:
            if tile.tick:
                tile.ticker += 1
                tile.tick = 0
    
def getX(q):
    r = 0
    if q == 0 or q == 4:
        r = 0
    if q == 1 or q == 2 or q == 3:
        r = 1
    if q == 5 or q == 6 or q == 7:
        r = -1
    return r

def getY(q):
    r = 0
    if q == 2 or q == 6:
        r = 0
    if q == 1 or q == 0 or q == 7:
        r = 1
    if q == 3 or q == 4 or q == 5:
        r = -1
    return r

def found(m,x,y):
    for i in range(8):
        if [x,y,i] in m:
            return 1
    return 0

max = 8
def init(map,px,py):
    global max
    map.getTile(px,py).bgcol = (255,0,0)
    map.getTile(px,py).char = '@'

    front = []
    #up = 0
    for i in range(8):
        front.append([px,py,i])

    for x in range(7):
        list = front
        front = []
        for fr in list:
            #tick the tile
            if map.getTile(fr[0],fr[1]) != 0:
                map.getTile(fr[0],fr[1]).ticker +=1

                #add 3 new ones
                for i in range(-1,2):
                    q = i
                    if fr[2] == 0 and i == -1:
                        q = 7
                    if fr[2] == 7 and i == 1:
                        q = -7
                    dx = getX(q+fr[2])
                    dy = getY(q+fr[2])
                    if not map.getTile(fr[0]+dx,fr[1]+dy) == 0:
                        if not map.getTile(fr[0]+dx,fr[1]+dy).blocks:
                            if not found(front,fr[0]+dx,fr[1]+dy):
                                front.append([fr[0]+dx,fr[1]+dy,fr[2]+q])
                                map.getTile(fr[0],fr[1]).ticker += 1
                if map.getTile(fr[0],fr[1]).ticker > max:
                    max = map.getTile(fr[0],fr[1]).ticker
                
            #if map.getTile(fr[0],fr[1]).ticker > 3:
            #    map.getTile(fr[0],fr[1]).ticker = 3
        map.tick()

def updateTiles(m):
    for i in range(30):
        for j in range(30):
            t = m.getTile(i,j)
            if t.blocks:
                t.char="#"
                t.bgcol=(0,0,255)
            else:
                c = 255/max
                t.bgcol = (0,0,0)
                t.bgcol = (c*t.ticker,c*t.ticker,c*t.ticker)
                #if t.ticker != 0: t.char = str(t.ticker)

if __name__ == "__main__":
    man = gr.RootWindow(30,30,'Radiosity','data/font.png')
    win = man.addWindow(gr.BorderedWindow,30,30,0,0)
    win.setBorder([(255,255,255),' ',(0,0,0),1])

    print 'start'

    m = Map()
    m.getTile(14,17).blocks = 1
    m.getTile(15,17).blocks = 1
    m.getTile(11,15).blocks = 1
    m.getTile(11,16).blocks = 1
    m.getTile(11,17).blocks = 1
    m.getTile(11,18).blocks = 1
    init(m,15,15)
    print 'init\'d'
    updateTiles(m)
    win.update(m.map)
    man.tick()
    man.draw()
    print 'tick'
    time.sleep(5)


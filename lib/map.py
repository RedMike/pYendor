

import random
import ConfigParser
import os
import data.libtcodpy as libtcod  # TODO: Modularise!

# Generator creates a map, then gen_map returns it.
#
# Map contains a basic 2D array of tuples of the form (blocks, blocks_light), for easy referencing.
#
# Tile is (blocks, blocks_light).
#
# Globals _WALL and _FLOOR to ease modification.

_WALL = (1,1)
_FLOOR = (0,0)

class Generator(object):
    
    def __init__(self,w,h):
        """Only initialises the map, doesn't generate immediately, until gen_map is called."""
        self.width = w
        self.height = h
        self.map = Map(w,h)
    
    def gen_map(self):
        """Returns generated map."""
        # basic generation algorithm
        self.map.clear()
        self.map.add_rect(2, 2, 10, 12, _FLOOR)
        self.map.add_rect(25, 4, 12, 15, _FLOOR)
        self.map.add_rect(10, 8, 20, 1, _FLOOR)
        self.map.add_rect(32, 9, 2, 4, _WALL)
        self.map.add_rect(5, 8, 2, 1, _WALL)
        return self.map

class BasicGenerator(Generator):
    """Generates a simple directional map, left to right."""

    def gen_map(self):
        """Returns simple left-to-right directional map."""
        self.map.clear()
        # initial options
        roughness = 50
        length = self.width-3
        wind = 100
        # starting points
        x = 1
        y = self.height/2-2
        height = 3
        for i in range(length):
            # iterate until we reach the right side of the screen
            self.map.add_rect(x, y, 1, height, _FLOOR)
            # every so often increase or decrease the width
            if random.randint(0,100)<roughness:
                height += random.randint(-2,2)
                if height < 3:
                    height = 3
                if y+height >= self.height:
                    height = self.height-y-1
            # every so often move the point we're at up or down
            if random.randint(0,100)<wind:
                y += random.randint(-2,2)
                if y < 1:
                    y = 1
                if y+height >= self.height:
                    y = self.height-height-1
            x += 1
        return self.map

class BlockGenerator(Generator):

    def __init__(self,w,h):
        super(BlockGenerator,self).__init__(150,150) # TODO: Fix me
        self.block_walls = { }
        self.block_dirs = { }
        self.block_widths = { }
        self.block_heights = { }
        self.parser = None
        self.accepted_sizes = set()
        self.rects = [ ]

    def add_rect(self,x,y,w,h):
        self.rects.append((x,y,w,h))

    def place_block(self,x,y,id):
        for i in range(len(self.block_walls[id])):
            for j in range(len(self.block_walls[id][i])):
                if self.block_walls[id][i][j] != '#':
                    self.map.add_tile(x+j,y+i,_FLOOR)

    def check_rect(self,x,y,w,h):
        if x<0 or y<0 or x+w>self.width or y+h>self.height:
            return True
        if (x,y,w,h) in self.rects:
            return True
        return False

    def check_col(self,rect):
        if self.check_rect(*rect):
            return True
        for rect2 in self.rects:
            if (rect[0] < rect2[0]+rect2[2] and rect[0]+rect[2] > rect2[0]
                  and rect[1] < rect2[1]+rect2[3] and rect[1]+rect2[3] > rect2[1]):
                return True
        return False

    def set_layout(self,name):
        self.parser = ConfigParser.RawConfigParser()
        # read in the layout
        self.parser.read('data/map/'+name+'.layout')
        self.accepted_sizes = set()
        for id in os.listdir('data/map/blocks/'):
            print 'Read a block in!'
            id = id.replace('.block','')
            # read in the blocks and add their data to the dicts
            self.parser.read('data/map/blocks/'+id+'.block')
            self.block_widths[id] = self.parser.getint(id,'width')
            self.block_heights[id] = self.parser.getint(id,'height')
            self.block_dirs[id] = { i : self.parser.getboolean(id,i) for i in ('top','bottom','left','right')}
            self.block_walls[id] = [ ]
            for i in range(self.block_heights[id]):
                line = self.parser.get(id, 'line' + str(i))
                line_new = ''
                for char in line:
                    if char != '#':
                        line_new += '.'
                    else:
                        line_new += '#'
                self.block_walls[id].append(line_new)
            self.accepted_sizes.add((self.block_widths[id],self.block_heights[id]))

    def choose_block(self,x,y,dir='top'):
        ret = []
        for id in self.block_heights.keys():
            if self.block_dirs[id][dir]:
                w = self.block_widths[id]
                h = self.block_heights[id]
                rect = (x, y, w, h)
                if not self.check_col(rect):
                    ret.append(id)
        if ret:
            return random.choice(ret)
        return None

    def _recurse_gen(self,x,y,dir):
        id = self.choose_block(x,y,dir)
        if id is None:
            return
        w = self.block_widths[id]
        h = self.block_heights[id]
        self.add_rect(x,y,w,h)
        self.place_block(x,y,id)
        for key in self.block_dirs[id].keys():
            if self.block_dirs[id][key]:
                new_dir = "top"
                if key == "top":
                    new_dir = "bottom"
                elif key == "left":
                    new_dir = "right"
                elif key == "right":
                    new_dir = "left"
                new_x = x+(key == "right")*w + (key=="left")*(-w)
                new_y = y+(key == "bottom")*h + (key=="top")*(-h)
                if 0 < new_x < self.width and 0 < new_y < self.height:
                    self._recurse_gen( new_x,new_y,new_dir)

    def gen_map(self):
        self.map.clear()
        #x, y = random.randint(0, self.width), random.randint(0, self.height)
        x, y = 10, 10
        #self.map.add_rect(0, y, self.width, 1, _FLOOR)
        #self.map.add_rect(x, 0, 1, self.height, _FLOOR)

        self._recurse_gen(x, y, "bottom")

        return self.map


class Map:
    """Contains 2D array of (blocks, blocks_light), and functions to ease modification."""
    
    def __init__(self,w,h):
        """Initialised with light-blocking walls."""
        self.width = w
        self.height = h
        self.clear()

    def add_tile(self, x, y, tile):
        """Replaces tile with given tuple."""
        if 0 < x < self.width and 0 < y < self.height:
            self.tiles[x][y] = tile
    
    def add_rect(self, x, y, w, h, tile):
        """Draws a rectangle of starting at (x,y), (w,h) size."""
        for i in range(w):
            for j in range(h):
                self.add_tile(x+i, y+j, tile)

    def add_circle(self, x, y, r, tile):
        """Draws a circle centered on (x,y), with the diameter r."""
        r /= 2
        for i in range(-r,r):
            for j in range(-r,r):
                if float((i*i+j*j)**(1/2.0)) < r:
                    self.add_tile(x+i, y+j, tile)
    
    def get_tiles(self):
        """Returns the whole map."""
        return self.tiles

    def get_rect(self, x, y, w, h):
        """Returns a 2D array section of the original map, starting at (x,y) with size (w,h)."""
        ret = [[_WALL for i in range(h)] for j in range(w)]
        for i in range(w):
            for j in range(h):
                ret[i][j] = self.get_tile(x+i, y+j)
        return ret
    
    def get_tile(self,x,y):
        """Returns wall if tile not in map."""
        if 0 < x < self.width and 0 < y < self.height:
            return self.tiles[x][y]
        return _WALL

    def clear(self):
        """Defaults everything to light-blocking walls."""
        self.tiles = [[_WALL for i in range(self.height)] for j in range(self.width)]

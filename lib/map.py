

import random

# Generator creates a map, then gen_map returns it.
#
# Map contains a basic 2D array of tuples of the form (blocks, blocks_light), for easy referencing.
#
# Tile is (blocks, blocks_light).
#
# Globals _WALL and _FLOOR to ease modification.

_WALL = (1,1)
_FLOOR = (0,0)

class Generator:
    
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

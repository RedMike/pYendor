

import random
import ConfigParser
import os

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
        super(BlockGenerator,self).__init__(w,h)
        self.block_walls = { }
        self.block_dirs = { }
        self.block_widths = { }
        self.block_heights = { }
        self.block_bias = { }
        self.parser = None
        self.accepted_sizes = set()
        self.rects = [ ]
        self.entities = [ ]
        self.finish_block = None
        self.finished = False

    def add_rect(self,x,y,w,h):
        self.rects.append((x,y,w,h))

    def add_ent(self,x,ox,y,oy,block_id,char):
        if self.parser.has_option(block_id,char) and self.parser.has_option(block_id,char+"_chance"):
            #it's an actual entity spawner definition
            lookup_name = self.parser.get(block_id,char)
            ret = [x+ox, y+oy, char+str(x)+str(y), lookup_name, self.parser.getfloat(block_id,char+'_chance')]
            ret2 = []
            for items in self.parser.items(block_id):
                name, val = items
                if name.startswith(char+'_') and name != char+"_chance":
                    att = name.replace(char+'_','')
                    ret2.append((att,val))
            ret.append(ret2)
            self.entities.append(tuple(ret))

    def place_block(self,x,y,id):
        for i in range(len(self.block_walls[id])):
            for j in range(len(self.block_walls[id][i])):
                char = self.block_walls[id][i][j]
                if char != '#':
                    self.map.add_tile(x+j,y+i,_FLOOR)
                    self.add_ent(x,j,y,i,id,char)


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
        if os.path.exists('data/map/'+name+'.layout'):
            self.parser = ConfigParser.RawConfigParser()
            self.block_walls = { }
            self.block_dirs = { }
            self.block_widths = { }
            self.block_heights = { }
            self.block_bias = { }
            self.rects = [ ]
            self.entities = [ ]
            # read in the layout
            self.parser.read('data/map/'+name+'.layout')
            self.accepted_sizes = set()
            for id in os.listdir('data/map/blocks/'):
                if '.block' in id:
                    id = id.replace('.block','')
                    # read in the blocks and add their data to the dicts
                    self.parser.read('data/map/blocks/'+id+'.block')
                    self.block_widths[id] = self.parser.getint(id,'width')
                    self.block_heights[id] = self.parser.getint(id,'height')
                    self.block_dirs[id] = { }
                    if self.parser.has_option('layout', id):
                        self.block_bias[id] = self.parser.getfloat('layout', id)
                    elif self.parser.has_option('layout', id[-2]):
                        self.block_bias[id] = self.parser.getfloat('layout', id)
                    else:
                        self.block_bias[id] = 0.5
                    for dir in ('top', 'bottom', 'left', 'right'):
                        s = self.parser.get(id,dir)
                        # s is a offset, length
                        self.block_dirs[id][dir] = tuple(map(int,s.split(',')))
                    self.block_walls[id] = [ ]
                    for i in range(self.block_heights[id]):
                        line = self.parser.get(id, 'line' + str(i))
                        self.block_walls[id].append(line)
                    self.accepted_sizes.add((self.block_widths[id],self.block_heights[id]))

    def choose_block(self, old_x, old_y, old_id, old_dir):
        new_dir = "bottom"
        if old_dir == "bottom":
            new_dir = "top"
        elif old_dir == "left":
            new_dir = "right"
        elif old_dir == "right":
            new_dir = "left"
        width = self.block_dirs[old_id][old_dir][1]
        valid_blocks = [ ]
        for block in self.block_dirs.keys():
            dir = self.block_dirs[block][new_dir]
            if dir[1] == width:
                #the exit fits, let's see if it has room from the other blocks
                x = old_x
                y = old_y
                w = self.block_widths[block]
                h = self.block_heights[block]
                x += self.block_widths[old_id] * (old_dir == "right") - w * (old_dir == "left")
                y += self.block_heights[old_id] * (old_dir == "bottom") - h * (old_dir == "top")
                off = self.block_dirs[old_id][old_dir][0]
                n_off = dir[0]
                #we offset the new block so that the two exits more or less line up
                if old_dir in ("left", "right"):
                    y -= (n_off - off) - (width - dir[1])/2
                elif old_dir in ("top", "bottom"):
                    x -= (n_off - off) - (width - dir[1])/2
                if not self.check_col((x,y,w,h)):
                    valid_blocks.append((x,y,block))
        if valid_blocks:
            choices = []
            for block in valid_blocks:
                x, y, id = block
                chance = int(self.block_bias[id]*100)
                choices += [block for i in range(chance)]
            if choices:
                return random.choice(choices)
            return None
        return None

    def _recurse_gen(self, x, y, block_id):
        self.add_rect(x, y, self.block_widths[block_id], self.block_heights[block_id])
        self.place_block(x, y, block_id)
        for dir in self.block_dirs[block_id].keys():
            dirs = self.block_dirs[block_id][dir]
            if dirs[1]:
                #it's a valid direction for the block, let's find if we've got a block that fits
                choice = self.choose_block(x, y, block_id, dir)
                if choice:
                    #we've got a block!
                    #recurse over it too
                    if choice[2].startswith(self.finish_block):
                        self.finished = True
                    self._recurse_gen(*choice)

    def gen_map(self):
        it = 0
        while not self.finished or len(self.rects) < 20:
            self.map.clear()
            self.entities = [ ]
            self.rects = [ ]
            x, y = random.randint(20, self.width-20), random.randint(20, self.height-20)
            block = self.parser.get('layout','start')
            self.finish_block = self.parser.get('layout','end')
            self.finished = False
            self._recurse_gen(x, y, block)
            it += 1
            if it > 1000:
                raise Exception
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

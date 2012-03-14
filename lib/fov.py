import data.libtcodpy as libtcod

class FovMap(object):

    def __init__(self):
        self.pad = 3
        self.map = None
        self.explored_map = None
        self.last_pos = (0, 0)

    def specific_init(self,w,h):
        self.map = libtcod.map_new(w + 2 * self.pad,h + 2 * self.pad)
        self.explored_map = [[False for i in range(h + 2 * self.pad)] for j in range(w + 2 * self.pad) ]
        libtcod.map_clear(self.map)

    def specific_set_properties(self,x,y,blocks_light,blocks):
        libtcod.map_set_properties(self.map,x+self.pad,y+self.pad,blocks_light,blocks)

    def specific_compute(self,x,y,radius=0,light_walls=True):
        libtcod.map_compute_fov(self.map,x+self.pad,y+self.pad,radius,light_walls,libtcod.FOV_PERMISSIVE_2)

    def specific_get_lit(self,x,y):
        return libtcod.map_is_in_fov(self.map,x+self.pad,y+self.pad)

    def specific_get_wall(self,x,y):
        return not libtcod.map_is_transparent(self.map,x+self.pad,y+self.pad)

    def get_wall(self,x,y):
        return self.specific_get_wall(x,y)

    def compute(self,pos_fct):
        pos = pos_fct()
        if not pos:
            return
        self.specific_compute(pos[0],pos[1])
        self.last_pos = pos

    def get_lit(self,x,y):
        #returns [lit or not, distance]
        d = (float(self.last_pos[0]-x)**2 + float(self.last_pos[1]-y)**2)**(1/2.0)
        if x in range(0, len(self.explored_map)-self.pad) and y in range(0, len(self.explored_map[0])-self.pad):
            return self.specific_get_lit(x,y),d
        else:
            return False, 5

    def set_explored(self,x,y):
        if 0 <= x+self.pad < len(self.explored_map) and 0 <= y+self.pad < len(self.explored_map[0]):
            self.explored_map[x+self.pad][y+self.pad] = True

    def get_explored(self,x,y):
        if 0 <= x+self.pad < len(self.explored_map) and 0 <= y+self.pad < len(self.explored_map[0]):
            return self.explored_map[x+self.pad][y+self.pad]
        return False

    def process_map(self,map):
        w, h = map.width, map.height
        self.specific_init(w,h)
        for x in range(w):
            for y in range(h):
                blocks, blocks_light = map.get_tile(x,y)
                self.specific_set_properties(x,y,not blocks_light, not blocks)




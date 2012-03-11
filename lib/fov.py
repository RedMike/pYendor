import data.libtcodpy as libtcod

class FovMap(object):

    def __init__(self):
        self.map = None
        self.explored_map = None
        self.last_pos = (0, 0)

    def specific_init(self,w,h):
        self.map = libtcod.map_new(w,h)
        self.explored_map = [[False for i in range(h)] for j in range(w)]
        libtcod.map_clear(self.map)

    def specific_set_properties(self,x,y,blocks_light,blocks):
        libtcod.map_set_properties(self.map,x,y,blocks_light,blocks)

    def specific_compute(self,x,y,radius=0,light_walls=True):
        libtcod.map_compute_fov(self.map,x,y,radius,light_walls,libtcod.FOV_PERMISSIVE_2)

    def specific_get_lit(self,x,y):
        return libtcod.map_is_in_fov(self.map,x,y)

    def specific_get_wall(self,x,y):
        return not libtcod.map_is_transparent(self.map,x,y)

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
        return self.specific_get_lit(x,y),d

    def set_explored(self,x,y):
        if 0 <= x < len(self.explored_map) and 0 <= y < len(self.explored_map[0]):
            self.explored_map[x][y] = True

    def get_explored(self,x,y):
        if 0 <= x < len(self.explored_map) and 0 <= y < len(self.explored_map[0]):
            return self.explored_map[x][y]
        return False

    def process_map(self,map):
        w, h = map.width, map.height
        self.specific_init(w,h)
        for x in range(w):
            for y in range(h):
                blocks, blocks_light = map.get_tile(x,y)
                self.specific_set_properties(x,y,not blocks_light, not blocks)




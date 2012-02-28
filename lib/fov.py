import data.libtcodpy as libtcod

class FovMap(object):

    def __init__(self):
        self.map = None
        self.last_pos = (0, 0)

    def specific_init(self,w,h):
        self.map = libtcod.map_new(w,h)
        libtcod.map_clear(self.map)

    def specific_set_properties(self,x,y,blocks_light,blocks):
        libtcod.map_set_properties(self.map,x,y,blocks_light,blocks)

    def specific_compute(self,x,y,radius=0,light_walls=True):
        libtcod.map_compute_fov(self.map,x,y,radius,light_walls,libtcod.FOV_SHADOW)

    def specific_get_lit(self,x,y):
        return libtcod.map_is_in_fov(self.map,x,y)

    def compute(self,pos):
        self.specific_compute(pos[0],pos[1])
        self.last_pos = pos

    def get_lit(self,x,y):
        #returns [lit or not, distance]
        d = ((self.last_pos[0]-x)**2 - (self.last_pos[1]-y)**2)**(1/2)
        return self.specific_get_lit(x,y),d

    def process_map(self,map):
        w, h = map.width, map.height
        self.specific_init(w,h)
        for x in range(w):
            for y in range(h):
                blocks, blocks_light = map.get_tile(x,y)
                self.specific_set_properties(x,y,not blocks_light, not blocks)




import pygame
from pygame.locals import *
import json, sys

black = (0,0,0)
white = (255,255,255)

pygame.init()


class OffWindow(object):
    """Offscreen window for storing pieces of graphical information, then blitting it all at once.

    Basically a convenient container for a big tile map.
    """

    def __init__(self, w, h, tile_set):
        self.size = (w, h)
        self.tile_set = tile_set
        self.tiles = [ [(black, tile_set[' '], white) for i in range(h)] for j in range(w)]


    def put_char(self, x, y, char, bg=None, fg=None):
        """Sets a tile to contain a certain char/string, and optionally, sets background/foreground color."""
        if 0 <= x < self.size[0] and 0 <= y < self.size[1]:
            tile = self.tiles[x][y]
            char = self.tile_set.get(char,self.tile_set[' '])
            tile = (tile[0], char, tile[2])
            if bg:
                tile = (self.tile_set.get(bg,bg), tile[1], tile[2])
            if fg:
                tile = (tile[0], tile[1], fg)
            self.tiles[x][y] = tile

    def set_col(self, x, y, bg=None, fg=None):
        """Sets a tile's colors to a certain pair; Leave as None what you don't want to change."""
        tile = self.tiles[x][y]
        if bg:
            tile = (bg, tile[1], tile[2])
        if fg:
            tile = (tile[0], tile[1], fg)
        self.tiles[x][y] = tile

    def get_col(self, x, y):
        """Gets a tile's colours as (bgcol, fgcol)."""
        return self.tiles[x][y][0], self.tiles[x][y][2]

    def put_string(self, x, y, w, h, msg, bg=None, fg=None):
        """Print a string inside a rectangle."""
        if not h:
            h = self.size[1]
        cur_x = x
        cur_y = y
        words = msg.split(" ")
        for word in words:
            if cur_x-x + len(word) > w:
                cur_y += 1
                cur_x = x
            for letter in word:
                self.put_char(cur_x, cur_y, letter, bg=bg, fg=fg)
                cur_x += 1
                if cur_x-x > w:
                    cur_y += 1
                    cur_x = x
            if cur_y - y > h:
                cur_y += 1
                break
            cur_x += 1

    def test_string_height(self, x, y, w, h, msg):
        """Get the height of the rectangle tightly fitting the string inside that rectangle."""
        h = self.size[1]
        cur_x = x
        cur_y = y
        words = msg.split(" ")
        for word in words:
            if cur_x-x + len(word) > w:
                cur_y += 1
                cur_x = x
            for letter in word:
                cur_x += 1
                if cur_x-x > w:
                    cur_y += 1
                    cur_x = x
            if cur_y - y > h:
                cur_y += 1
                break
            cur_x += 1
        return cur_y - y + 1

    def clear(self, bg=None, fg=None):
        """Clears everything to a set of colours and ' '."""
        if not bg:
            bg = black
        if not fg:
            fg = white
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                self.tiles[i][j] = (bg, self.tile_set[' '], fg)

    def put_h_line(self, x, y, w, bg=None, fg=None):
        """Draw a horizontal line."""
        for i in range(x, x+w):
            self.put_char(i, y, "hline", bg=bg, fg=fg)

    def put_v_line(self, x, y, h, bg=None, fg=None):
        """Draw a vertical line."""
        for j in range(y, y+h):
            self.put_char(x, j, "vline", bg=bg, fg=fg)

    def put_frame(self, x, y, w, h, bg=None, fg=None):
        """Draw a full line box."""
        for i in range(x+1, x+w):
            for j in range(y+1, y+h):
                self.put_char(x, j, "vline", bg=bg, fg=fg)
                self.put_char(x+w-1, j, "vline", bg=bg, fg=fg)
                self.put_char(i, y, "hline", bg=bg, fg=fg)
                self.put_char(i, y+h-1, "hline", bg=bg, fg=fg)
        self.put_char(x, y+h-1, "corner1", bg=bg, fg=fg)
        self.put_char(x, y, "corner2", bg=bg, fg=fg)
        self.put_char(x+w-1, y, "corner3", bg=bg, fg=fg)
        self.put_char(x+w-1, y+h-1, "corner4", bg=bg, fg=fg)


    def blit(self, src, src_x, src_y, src_w, src_h, x, y):
        """Blit another console onto this one."""
        for i in range(src_x, src_x+src_w):
            for j in range(src_y, src_y+src_h):
                self.tiles[i-src_x+x][j-src_y+y] = src.tiles[i][j]



class RootWindow(OffWindow):
    """Root window; holds a Pygame window and handles drawing to itself, while abstractising from proper
    graphics down to tile-based."""

    def __init__(self, name, w, h, font, zoom=2.0):
        self.size = (w,h)
        self.tiles = [ [(black, ' ', white) for i in range(h)] for j in range(w) ]

        self.tile_size = 8
        self.screen = pygame.display.set_mode((100,100)) # Initialise once, in order to be able to process font.
        self.load_font_set(font)
        self.real_size = (int(w*self.tile_size*zoom), int(h*self.tile_size*zoom))

        self.screen = pygame.display.set_mode(self.real_size)
        pygame.display.set_caption(name)
        self.root = pygame.Surface((w*self.tile_size, h*self.tile_size))
        self.clock = pygame.time.Clock()

    def new_window(self, w, h):
        win = OffWindow(w, h, self.tile_set)
        return win

    def load_image(self, file, ckey=None):
        image = pygame.image.load(file)
        image = image.convert()
        if not ckey:
            ckey = image.get_at((0,0))
        image.set_colorkey(ckey)
        return image

    def crop_tile_from_image(self, image, tile_size, x, y):
        """Crops a tile from an atlas, and returns a surface with it."""
        cropped = pygame.Surface((tile_size, tile_size)).convert()
        cropped.set_colorkey(image.get_colorkey())
        cropped.blit(image,(0,0),
            (x*tile_size,y*tile_size,(x+1)*tile_size,(y+1)*tile_size))
        return cropped

    def load_font_set(self, file):
        """Loads a JSON file specifying char/str bindings, and loads images/crops tiles from them."""
        self.tile_set = { }
        with open(file,'r') as f:
            font_set = json.load(f)
        self.tile_size = font_set["tile_size"]

        surf = pygame.Surface((self.tile_size, self.tile_size))
        surf.fill(black)
        self.tile_set[' '] = surf

        for font_key in font_set:
            set = font_set[font_key]
            if isinstance(set, dict):
                font_file = set["file_name"]
                c_key = set["color_key"]
                image = self.load_image(font_file,c_key)
                keys = { }
                for key in set["keys"]:
                    x, y = set["keys"][key]
                    keys[key] = self.crop_tile_from_image(image,self.tile_size,x,y)
                self.tile_set.update(keys)

    def render(self):
        """Internal method, don't call."""
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                set = self.tiles[i][j]
                im = set[1].copy()
                if set[2]:
                    im.fill(set[2],special_flags=pygame.BLEND_RGB_MIN)
                if isinstance(set[0], tuple):
                    self.root.fill(set[0], (i*self.tile_size, j*self.tile_size,self.tile_size, self.tile_size))
                elif isinstance(set[0], pygame.Surface):
                    self.root.blit(set[0], (i*self.tile_size, j*self.tile_size))
                self.root.blit(im, (i*self.tile_size, j*self.tile_size))
        pygame.transform.scale(self.root, self.screen.get_size() ,self.screen)

        pygame.display.flip()

    def update(self):
        """Call in main loop, handles drawing."""
        self.render()
        return 1

    def tick(self, fps=60):
        """Call in main loop for fps limiting."""
        self.clock.tick(fps)

def get_key():
    events = pygame.event.get(KEYDOWN)
    quit = []
    while not events and not quit:
        events = pygame.event.get(KEYDOWN)
        quit = pygame.event.get(QUIT)
    if quit:
        pygame.quit()
        sys.exit()
    pygame.event.clear()
    ret = [ ]
    for event in events:
        ret.append(event)
    return ret
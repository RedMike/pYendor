#! /usr/bin/python

import math
import data.libtcodpy as libtcod
import lib.graphics as gr


__author__="mike"
__date__ ="$Feb 1, 2011 6:35:52 PM$"

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

class Map:

    def __init__(self):
        self.map = []
        for i in range(300):
            for j in range(300):
                self.map.append(Tile(i,j,(255,255,255)))
        self.fact = 2
        self.colors = []
        self.max_it = 500
        c1 = libtcod.white
        c2 = libtcod.dark_red
        c3 = libtcod.light_red
        for i in range(35):
            coef = i/float(35)
            self.colors.append(libtcod.color_lerp(c1,c2,coef))
        for i in range(35):
            coef = i/float(35)
            self.colors.append(libtcod.color_lerp(c2,c3,coef))
        for i in range(30):
            coef = i/float(30)
            self.colors.append(libtcod.color_lerp(c3,c1,coef))

    def iterate(self):
        for tile in self.map:
            x0 = -0.74364500005892 - self.fact + tile.x/300.0*2.0*self.fact
            y0 = 0.13182700000109 - self.fact + tile.y/300.0*2.0*self.fact

            x = float(0)
            y = float(0)

            it = 0


            #init tests
            p = math.sqrt((x0-1/4.0)**2 + y0**2)
            if x0 >= p - 2*p*p + 1/4.0 and (x0+1)*(x0+1) + y0*y0 >= 1/16.0:
                while( x*x + y*y <= (2*2) and it<self.max_it):
                    xtemp = x*x - y*y + x0
                    y = 2.0*x*y + y0

                    x = xtemp

                    it = it+1
            else:
                    it = self.max_it

            if it==self.max_it:
                tile.bgcol = (0,0,0)
            else:
                tile.bgcol = self.colors[it%100]
        self.fact = self.fact/2.0
        
if __name__ == "__main__":
    man = gr.RootWindow(300,300,'Mandelbrot','data/font_pixel.png')
    win = man.add_window(gr.BorderedWindow,300,300,0,0)
    win.set_border([(255,255,255),' ',(0,0,0),1])

    m = Map()
    i = 0
    while 1:
        m.iterate()
        print 'tick'
        win.update(m.map)
        man.tick()
        man.draw()
        libtcod.sys_save_screenshot('./tmp/screenshot'+str(i)+'.png')
        i += 1
        if i == 50:
            break

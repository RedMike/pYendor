###################################
#                                 #
# Created by Mike Red             #
#   Version: 00.04.00g            #
#                                 #
#   http://remike.homelinux.org   #
#                                 #
###################################

import lib.base as base
import lib.graphics as graphics

WIDTH, HEIGHT = 100, 50
FLOORBGCOL = (92,204,204)
WALLBGCOL = (0,99,99)
BORDER1BG = (204,204,250)
BORDER1FG = (166,0,0)
BORDER2BG = (255,115,115)
BORDER2FG = (166,0,0)

#initialise application
app = base.Application("pYendor Test Game ",WIDTH,HEIGHT)
app.generate_map(WIDTH,HEIGHT,1)
app.place_player(1)
#create basic windows
gameW = app.add_window(0,graphics.LayeredGameWindow,100,30,0,0)
gameW = app.win_man.get_window(gameW)
gameW.set_border([BORDER1BG,' ',BORDER1FG,1])
gameW.bgcol = WALLBGCOL
gameW.clear()
app.setGameWindow(gameW)
while not app.exit:
    app.update()
    
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

#in tiles, borders are 1 tile wide.
WIDTH, HEIGHT = 100, 50
FLOORBGCOL = (92,204,204)
WALLBGCOL = (0,99,99)
BORDER1BG = (204,204,250)
BORDER1FG = (166,0,0)
BORDER2BG = (255,115,115)
BORDER2FG = (166,0,0)

#function defs, start menu
def startMenuCallback(ret):
    if ret == -1:
        app.quit()
    elif ret == 0:
        app.newLevel()
        app.win_man.window.show_window(gameW)
        app.transitState(1)
    elif ret == 2:
        app.saveMap('map')
    elif ret == 3:
        app.load_map('map')



#initialise application
app = base.Application("pYendor Test Game ",WIDTH,HEIGHT)
#define basic floor/wall types
app.floor = [0,0,FLOORBGCOL,' ',(0,0,0),1,0,0]
app.wall = [0,0,WALLBGCOL,' ',(0,0,0),1,1,1]
#create basic windows
gameW = app.add_window(0,graphics.LayeredGameWindow,100,30,0,0)
gameW = app.win_man.get_window(gameW)
#msgW = app.add_window(0,'bmw',50,20,0,30)
#statusW = app.add_window(0,'sw',50,10,50,30)
#debugW = app.add_window(0,'dbw',50,10,50,40)
#invW = app.add_window(1,'gw',30,25,1,1)
#define basic window options
gameW.set_border([BORDER1BG,' ',BORDER1FG,1])
#msgW.set_border([BORDER1BG,' ',BORDER1FG,1])
#statusW.set_border([BORDER1BG,' ',BORDER1FG,1])
#debugW.set_border([BORDER2BG,'!',BORDER2FG,1])
#invW.set_border([BORDER2BG,' ',BORDER2FG,1])
gameW.bgcol = WALLBGCOL
#msgW.bgcol = WALLBGCOL
#statusW.bgcol = WALLBGCOL
#debugW.bgcol = WALLBGCOL
#invW.bgcol = WALLBGCOL
gameW.clear()
#msgW.clear()
#statusW.clear()
#debugW.clear()
#invW.clear()
#create health bar on status window
#statusW.addBar('HP:',25,25,[(255,0,0),(0,0,0)])

#tell application to use windows
#app.setMessageWindow(msgW)
#app.setGameWindow(gameW)
#app.setInvWindow(invW)
#create start menu
#app.addMenu(-5,1,[["Enter.",0],["Save map.",2],["Load map.",3],
#       ["Quit",-1]],startMenuCallback)
#enter its state
#app.transitState(-5)
#main update loop
while not app.exit:
    #debug window
    tmp = app.get_map()
    if tmp == None:
        tmp = 0
    else:
        tmp = len(tmp.getTiles())
        #debugW.debugTick(app.sched.ticks,len(app.entityList),tmp)
    #hp bar update
    #pl = app.getPlayer()
    #if pl != None:
        #statusW.updateBar(0,'HP:',pl.hp,pl.maxhp,[(255,0,0),(0,0,0)])

    app.update()
    
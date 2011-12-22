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
COL1 = (15, 100, 175)
COL2 = (255, 150, 0)

app = base.Application("pYendor Test Game ",WIDTH,HEIGHT)
app.generate_map(WIDTH,HEIGHT,1)
app.place_player(1)
app.default_bindings()
game_win = app.add_window(0,graphics.LayeredGameWindow,WIDTH,HEIGHT-20,0,0)
game_win = app.win_man.get_window(game_win)
game_win.set_border([COL2,' ',(0,0,0),1])
game_win.bgcol = COL1
game_win.clear()

msg_win = app.add_window(0,graphics.BorderedMessageWindow,WIDTH,20,0,HEIGHT-20)
msg_win = app.win_man.get_window(msg_win)
msg_win.set_border([COL1,' ',(0,0,0),1])
msg_win.bgcol = (0,0,0)
msg_win.clear()

app.set_game_window(game_win)
app.set_message_window(msg_win)
app.add_messages(["Hello world.", "This is a test message which should be long enough to wrap, hopefully. However, that's not enough, so hey, there we go, another line, awesome."])
while not app.exit:
    app.update()
    
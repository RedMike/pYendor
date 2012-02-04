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
game_win = app.add_window(0,graphics.LayeredGameWindow,WIDTH-30,HEIGHT-20,0,0)
game_win = app.win_man.get_window(game_win)
game_win.set_border([COL2,' ',(0,0,0),1])
game_win.bgcol = COL1
game_win.clear()

msg_win = app.add_window(0,graphics.BorderedMessageWindow,WIDTH,20,0,HEIGHT-20)
msg_win = app.win_man.get_window(msg_win)
msg_win.set_border([COL1,' ',(0,0,0),1])
msg_win.bgcol = (0,0,0)
msg_win.clear()

inv_win = app.add_window(0,graphics.NodeWindow,30,HEIGHT-20,WIDTH-30,0)
inv_win = app.win_man.get_window(inv_win)
inv_win.set_border([COL1,' ',(0,0,0),1])
inv_win.bgcol = (0,0,0)
inv_win.clear()

app.set_game_window(game_win)
app.set_message_window(msg_win)
app.set_inventory_window(inv_win)
app.add_messages(["Hello world.",
                  "This is a test message which should be long enough to wrap, hopefully. "
                 +"However, that's not enough, so hey, there we go, another line, awesome."])

#dg_ids = {0:None, 1:0, 2:1, 3:1, 4:0, 5:4, 6:0}
#dg_txt = {0:"root", 1:"test", 2:"woohoo", 3:"This is a weird node window.", 4:"Hi.", 5:"Oh god why", 6:"Hello world."}
#dg_win = app.add_window(3,graphics.NodeWindow,20,30,WIDTH-20,0)
#dg_win = app.win_man.get_window(dg_win)
#dg_win.set_border([COL2,' ',(0,0,0),1])
#dg_win.bgcol = COL1
#dg_win.clear()
#dg_win.set_nodes(dg_ids,dg_txt)

def menu_callback(fct):
    choice = fct()
    if not choice:
        app.generate_map(WIDTH,HEIGHT,set=1)
        app.place_player(1)
        while app.menu_stack:
            app.remove_menu()
    elif choice == 1:
        app.quit()
    elif choice == 2:
        app.add_choice_menu(["Main menu: "], ("Start Game", "Quit", "Recursion.", "Anti-recursion."), menu_callback)
    elif choice == 3:
        app.remove_menu()

app.add_choice_menu(["Main menu: "], ("Start Game", "Quit", "Recursion"), menu_callback)
while not app.exit:
    app.update()
    #if app.get_player() is not None:
    #    if app.get_ent_pos(app.get_player())[0] > 50 and not app.menu_stack:
    #        app.add_choice_menu(["Your X position was over 50.", "This menu pops up when that happens:"],
    #                            ("Start Game", "Quit"), menu_callback)

    
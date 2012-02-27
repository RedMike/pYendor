#Copyright (c) 2011-2012, Roibu Theodor-Mihai
#All rights reserved.
#
#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are met:
#
#1. Redistributions of source code must retain the above copyright notice, this
#list of conditions and the following disclaimer.
#2. Redistributions in binary form must reproduce the above copyright notice,
#this list of conditions and the following disclaimer in the documentation
#and/or other materials provided with the distribution.
#
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
#ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#The views and conclusions contained in the software and documentation are those
#of the authors and should not be interpreted as representing official policies,
#either expressed or implied, of the FreeBSD Project.

import lib.base as base
import lib.graphics as graphics

WIDTH, HEIGHT = 100, 50
MAP_WIDTH, MAP_HEIGHT = 200, 200
COL1 = (15, 100, 175)
COL2 = (255, 150, 0)

app = base.Application("pYendor Test Game ",WIDTH,HEIGHT)
game_win = app.add_window(0,graphics.LayeredGameWindow,WIDTH-30,HEIGHT-20,0,0)
game_win = app.win_man.get_window(game_win)
game_win.set_border([COL2,' ',(0,0,0),1])
game_win.bgcol = COL1
game_win.clear()

msg_win = app.add_window(0,graphics.MessageWindow,WIDTH,20,0,HEIGHT-20)
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
app.add_messages(("Hello world.",
                  "This is a test message which should be long enough to wrap, hopefully. "
                 +"However, that's not enough, so hey, there we go, another line, awesome."))

def menu_callback(fct):
    choice = fct()
    if not choice:
        app.generate_map(MAP_WIDTH,MAP_HEIGHT,set=True)
        app.place_player(1)
        while app.menu_stack:
            app.remove_menu()
    elif choice == 1:
        app.quit()
    elif choice == 2:
        app.add_choice_menu(("Main menu: ",), ("Start Game", "Quit", "Recursion.", "Anti-recursion."), menu_callback)
    elif choice == 3:
        app.remove_menu()
app.add_choice_menu(("Main menu: ",), ("Start Game", "Quit", "Recursion"), menu_callback)
while not app.exit:
    app.update()


    
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

import struct
import lib.base as base
import lib.graphics as graphics

def debug(fct):
    switches, choices = fct() or (None, None)
    if switches:
        print zip(switches, choices)
        app.remove_menu()

class CustomApp(base.Application):

    def default_bindings(self):
        super(CustomApp,self).default_bindings()
        player = self.entity_manager[self.player]
        if player is not None:
            self.add_binding('o', [self.change_color_scheme,(COLBG, COLFG, COLGWALL, COLGFLOOR, COLGFOGFLOOR)])
            self.add_binding('p', [self.change_color_scheme,(COLBG, COLFG, COLGWALL2, COLGFLOOR, COLGFOGFLOOR)])
            self.add_binding('l', [self.add_switch_menu,(('Option 1', 'Longer Option 2', 'S O 3'),(False, True, False),debug),])

WIDTH, HEIGHT = 80, 50
MAP_WIDTH, MAP_HEIGHT = 100, 100

COLBG = "2C515D"
COLFG = "F2EFEC"

COLGBG = "C88E7C"
COLGBD = "E8DDB3"

COLGFLOOR = "957C74"
COLGFOGFLOOR = "ACA7A6"
COLGWALL = "E6E2DA"
COLGWALL2 = "333230"


app = CustomApp("Sam Pull RL",WIDTH,HEIGHT)

game_win = app.add_window(0,graphics.LayeredGameWindow,WIDTH-30,HEIGHT-20,0,0)
msg_win = app.add_window(0,graphics.MessageWindow,WIDTH,20,0,HEIGHT-20)
inv_win = app.add_window(0,graphics.InventoryWindow,30,HEIGHT-20,WIDTH-30,0)

app.set_game_window(game_win)
app.set_message_window(msg_win)
app.set_inventory_window(inv_win)

app.change_color_scheme(COLBG, COLFG, COLGWALL, COLGFLOOR, COLGFOGFLOOR)

def menu_callback(fct):
    choice = fct()
    if not choice:
        app.generate_map(MAP_WIDTH,MAP_HEIGHT,set=True)
        app.place_player(10)
        while app.menu_stack:
            app.remove_menu()
    elif choice == 1:
        app.quit()

app.add_choice_menu("Please report any bugs to mike@codingden.net.\n\nMain menu: ", ("Start Game", "Quit"), menu_callback, w=30, h=14)
while not app.exit:
    app.update()



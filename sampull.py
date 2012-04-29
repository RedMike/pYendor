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

class CustomApp(base.Application):

    def create_windows(self):
        self.game_win = self.add_window(0,graphics.LayeredGameWindow,30,35,25,0)
        self.msg_win = self.add_window(0,graphics.MessageWindow,25,35,WIDTH-25,0)
        self.inv_win = self.add_window(0,graphics.InventoryWindow,25,35,0,0)

        self.comm_win = self.add_window(0,graphics.ConsoleWindow,WIDTH,15,0,35)
        self.comm_win.set_label("> ")
        self.comm_win.set_length(WIDTH-2)

        self.change_color_scheme(COLBG, COLFG, COLGWALL2, COLGFLOOR, COLGFOGFLOOR)

    def console_callback(self,line):
        try:
            if line in ("quit", "n", "e", "s", "w", "north", "south", "east", "west", "get", "pickup"):
                player = self.entity_manager[self.player]
                if line == "quit":
                    self.quit()
                elif line == "n" or line == "north":
                    player.move(0,-1)
                elif line == "s" or line == "south":
                    player.move(0,1)
                elif line == "e" or line == "east":
                    player.move(1,0)
                elif line == "w" or line == "west":
                    player.move(-1,0)
                elif line == "get" or line == "pickup":
                    self.player_pickup()
            self.time_passing = True
        except Exception as e:
            self.add_messages((str(e),))

    def default_bindings(self):
        if self.comm_win:
            self.input_bindings(self.comm_win,self.console_callback,False)
        #self.add_binding('o', [self.change_color_scheme,(COLBG, COLFG, COLGWALL, COLGFLOOR, COLGFOGFLOOR)])
        #self.add_binding('p', [self.change_color_scheme,(COLBG, COLFG, COLGWALL2, COLGFLOOR, COLGFOGFLOOR)])

app = CustomApp("Sam Pull RL",WIDTH,HEIGHT)


def menu_callback(fct):
    choice = fct()
    if not choice:
        app.generate_map(MAP_WIDTH,MAP_HEIGHT,set=True)
        app.place_player(10)
        while app.menu_stack:
            app.remove_menu()
        app.scheduler.tick()
        app.update_game_window()
    elif choice == 1:
        app.quit()

app.add_choice_menu("Please report any bugs to mike@codingden.net.\n\nMain menu: ", ("Start Game", "Quit"), menu_callback, w=30, h=14)
while not app.exit:
    app.update()



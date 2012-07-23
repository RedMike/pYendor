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

WIDTH, HEIGHT = 50, 30
MAP_WIDTH, MAP_HEIGHT = 100, 100


class CustomApp(base.Application):

    def create_windows(self):
        self.game_win = self.add_window(0,graphics.LayeredGameWindow,WIDTH-25,HEIGHT,25,0)
        self.inv_win = self.add_window(0,graphics.InventoryWindow,25,HEIGHT,0,0)
        self.change_color_scheme("2C515D", "F2EFEC", "2C515D", "F2EFEC", "2C515D")

    def default_bindings(self):
        self.add_binding('escape', [self.quit, ()])
        self.add_binding('q', [self.quit, ()])
        pl = self.entity_manager[self.player]
        self.add_binding('arrow_left', [pl.move, (-1,0)])
        self.add_binding('arrow_right', [pl.move, (1,0)])
        self.add_binding('arrow_up', [pl.move, (0,-1)])
        self.add_binding('arrow_down', [pl.move, (0,1)])


app = CustomApp("Sam Pull RL",WIDTH,HEIGHT)

def menu_callback(fct):
    choice = fct()
    if not choice:
        app.generate_map(MAP_WIDTH,MAP_HEIGHT,set=True)
        app.place_player(10)
        #while app.menu_stack:
        #    app.remove_menu()
        app.update_game_window()
    elif choice == 1:
        app.save_state("testing.save")
    elif choice == 2:
        app.load_state("testing.save")
    elif choice == 3:
        while app.menu_stack:
            app.remove_menu()
        app.update_game_window()
    elif choice == 4:
        app.quit()

app.add_choice_menu("Please report any bugs to mike@codingden.net.\n\nMain menu: ", ("Generate Map", "Save Map", "Load Map", "Play", "Quit"),
        menu_callback, w=30, h=14)
while not app.exit:
    app.update()



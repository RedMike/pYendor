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
import random

import lib.base as base
import lib.graphics as graphics

WIDTH, HEIGHT = 80, 50
MAP_WIDTH, MAP_HEIGHT = 100, 100
COLBORD1 = (4, 58, 107)
COLBORD2 = (64, 141, 210)

COLWALL1 = (255, 149, 0)
COLWALL2 = (255, 176, 64)
COLWALL3 = (191, 168, 48)

COLFLOOR1 = (191, 55, 48)
COLFLOOR2 = (166, 8, 0)
COLWALLS = [COLWALL1, COLWALL1, COLWALL1, COLWALL1, COLWALL1, COLWALL1, COLWALL1,
            COLWALL1, COLWALL1, COLWALL1, COLWALL1, COLWALL1, COLWALL1, COLWALL1,
            COLWALL2, COLWALL2, COLWALL3]
COLFLOORS = [COLFLOOR1, COLFLOOR1, COLFLOOR1, COLFLOOR1, COLFLOOR1, COLFLOOR1, COLFLOOR1,
             COLFLOOR1, COLFLOOR1, COLFLOOR1, COLFLOOR1, COLFLOOR1, COLFLOOR1, COLFLOOR1,
             COLFLOOR2, COLFLOOR2]

class CustomApp(base.Application):

    def __init__(self, name, w, h):
        super(CustomApp,self).__init__(name, w, h)
        self.fov_map = None

    def add_choice_menu(self, labels, choices, callback):
        id = self.add_window(5, graphics.ChoiceWindow, self.win_man.width-30, self.win_man.height-20, 15, 10)
        win = self.win_man.get_window(id)
        win.set_border([COLBORD1,' ',(0,0,0),1])
        win.bgcol = COLBORD2
        win.clear()
        win.set_label(labels)
        win.set_choices(choices)
        self.menu_bindings(win,callback)
        self.menu_stack.append([id,callback])

    def get_wall_color(self, x, y):
        col = int((x**2 * 1023 + y*120)**1.9)%len(COLWALLS)
        return COLWALLS[col]

    def get_floor_color(self, x, y):
        col = int((x**2 * 1023 + y*120)**1.9)%len(COLFLOORS)
        return COLFLOORS[col]

    def update_game_window(self):
        cam = self.get_camera()
        map = self.get_map()
        win = self.game_win
        pos = self.get_ent_pos(cam)
        x, y = pos
        cx, cy = win.width/2, win.height/2
        ox, oy = x - cx, y - cy
        map = map.get_rect(ox, oy, win.width, win.height)
        tiles = [ ]
        for i in range(win.width):
            for j in range(win.height):
                wall = map[i][j][1]
                if wall:
                    col = self.get_wall_color(i + ox, j + oy)
                    tiles.append([i, j, col, ' ', (0,0,0), 1])
                if not wall:
                    col = self.get_floor_color(i + ox, j + oy)
                    tiles.append([i, j, col, ' ', (0,0,0), 1])


        win.update_layer(0,tiles)

        tiles = [ ]
        for id in self.entity_manager.get_ids():
            if self.entity_manager.get_attribute(id,'visible'):
                ret = self.get_ent_pos(id)
                if ret:
                    tx, ty = ret
                    ent = self.get_ent(id)
                    tiles.append([tx-ox, ty-oy, (0,0,0), ent.char, ent.fgcol, 0])
        win.update_layer(4,tiles)

        tiles = [ ]
        pl_pos = self.get_ent_pos(self.get_player())
        if pl_pos:
            tx, ty = pl_pos
            ent = self.get_ent(self.get_player())
            tiles.append([tx-ox, ty-oy, (0,0,0), ent.char, ent.fgcol, 0])
        win.update_layer(5,tiles)


app = CustomApp("Working Name",WIDTH,HEIGHT)
game_win = app.add_window(0,graphics.LayeredGameWindow,WIDTH-30,HEIGHT,30,0)
game_win = app.win_man.get_window(game_win)
game_win.set_border([COLBORD1,' ',(0,0,0),1])
game_win.bgcol = COLWALLS[0]
game_win.clear()

msg_win = app.add_window(0,graphics.MessageWindow,30,20,0,HEIGHT-20)
msg_win = app.win_man.get_window(msg_win)
msg_win.set_border([COLBORD1,' ',(0,0,0),1])
msg_win.bgcol = COLBORD2
msg_win.clear()

inv_win = app.add_window(0,graphics.NodeWindow,30,HEIGHT-20,0,0)
inv_win = app.win_man.get_window(inv_win)
inv_win.set_border([COLBORD1,' ',(0,0,0),1])
inv_win.bgcol = COLBORD2
inv_win.clear()

app.set_game_window(game_win)
app.set_message_window(msg_win)
app.set_inventory_window(inv_win)
#app.add_messages(("Hello world.",
#                  "This is a test message which should be long enough to wrap, hopefully. "
#                 +"However, that's not enough, so hey, there we go, another line, awesome."))

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
        pass

app.add_choice_menu(("Main menu: ",), ("Start Game", "Quit", "Debug."), menu_callback)
while not app.exit:
    app.update()


    
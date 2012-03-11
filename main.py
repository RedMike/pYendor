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
MAP_WIDTH, MAP_HEIGHT = 150, 150
COLBORD1 = (14, 83, 120)
COLBORD2 = (61, 157, 208)

COLWALL1 = (255, 149, 0)
COLWALL2 = (255, 176, 64)
COLWALL3 = (191, 168, 48)

COLFLOOR1 = (166, 8, 0)
COLFLOOR2 = (191, 55, 48)
COLWALLS = [COLWALL1, COLWALL1, COLWALL1, COLWALL1, COLWALL1, COLWALL1, COLWALL1,
            COLWALL1, COLWALL1, COLWALL1, COLWALL1, COLWALL1, COLWALL1, COLWALL1,
            COLWALL2, COLWALL2, COLWALL3]
COLFLOORS = [COLFLOOR1, COLFLOOR1, COLFLOOR1, COLFLOOR1, COLFLOOR1, COLFLOOR1, COLFLOOR1,
             COLFLOOR1, COLFLOOR1, COLFLOOR1, COLFLOOR1, COLFLOOR1, COLFLOOR1, COLFLOOR1,
             COLFLOOR2, COLFLOOR2]

class CustomApp(base.Application):

    def __init__(self, name, w, h):
        super(CustomApp,self).__init__(name, w, h)
#        self.fov_map = None
        self.craft_win = None

    def _craft_window_callback(self, mods, char, vk, window):
        if vk == self.keyboard.KEY_UP:
            if window.highlight > 0:
                window.highlight -= 1
        elif vk == self.keyboard.KEY_DOWN:
            if window.highlight < len(window.messages):
                window.highlight += 1
        elif char == 'q':
            window.highlight = None
            inv_win.highlight = None
            self.time_passing = 1
            self.close_craft_window()
            self.default_bindings()
        elif vk == self.keyboard.KEY_LEFT:
            self.close_craft_window()
        elif vk == self.keyboard.KEY_RIGHT or char == 'e':
            ent_id, usable = window.get_node_meta(window.highlight)
            orig_id, orig_usable = inv_win.get_node_meta(inv_win.highlight)
            if not usable:
                #it's either a node, the player, or a wound
                self.entity_manager.ent_equip(ent_id, orig_id)
                self.close_craft_window()
            else:
                #it's another item, we need to craft.
                self.close_craft_window()
        self.update_craft_window()
        self.update_inv_window()

    def _inventory_window_callback(self, mods, char, vk, window):
        """Callback for input when working with inventory windows.

        @type  mods: dict
        @param mods: State of modifiers in the form of {'lalt', 'ralt', 'lctrl', 'rctrl', 'shift'}
        @type  char: char
        @param char: If vk is KEY_CHAR, this is the printable character
        @type  vk: int
        @param vk: Keycode, check against L{interface.KeyboardListener}.KEY_*
        """
        if vk == self.keyboard.KEY_UP:
            if window.highlight > 0:
                window.highlight -= 1
        elif vk == self.keyboard.KEY_DOWN:
            if window.highlight < len(window.messages):
                window.highlight += 1
        elif char == 'q' or vk == self.keyboard.KEY_LEFT:
            window.highlight = None
            self.time_passing = 1
            self.default_bindings()
        elif char == 'r':
            ent_id, usable = window.get_node_meta(window.highlight)
            if usable:
                self.player_drop(ent_id)
        elif char == 'e' or vk == self.keyboard.KEY_RIGHT:
            ent_id, usable = window.get_node_meta(window.highlight)
            if usable:
                self.node_bindings(self.open_craft_window(),self._craft_window_callback)
                self.update_craft_window()
        self.update_inv_window()

    def update_inv_window(self):
        """Default implementation of inventory window updating.

        Subclass and replace to use a different format or a different window type.
        """
        if self.inv_win is None:
            return  #TODO: Error handling.
        player = self.get_player()
        name = self.entity_manager.get_name(player) + ' (' + str(self.get_ent(self.player).get_injuries()) + ')'
        names = {0:name}
        parents = {0:None}
        meta = {0:(player,False)}
        parents, names, meta, cur_id = self._inv_window_recurse(player,parents,names,meta)
        self.inv_win.set_nodes(parents,names,meta)

    def update_craft_window(self):
        """Default implementation of inventory window updating.

        Subclass and replace to use a different format or a different window type.
        """
        if self.craft_win is None:
            return  #TODO: Error handling.
        player = self.get_player()
        names = {0:self.entity_manager.get_name(player)}
        parents = {0:None}
        meta = {0:(player,False)}
        parents, names, meta, cur_id = self._inv_window_recurse(player,parents,names,meta)
        self.craft_win.set_nodes(parents,names,meta)

    def show_window(self,window):
        id = self.win_man.get_id(window)
        self.win_man.show_window(id)

    def hide_window(self,window):
        id = self.win_man.get_id(window)
        self.win_man.hide_window(id)

    def open_craft_window(self):
        if self.craft_win:
            self.show_window(self.craft_win)
            return self.craft_win
        else:
            raise Exception

    def close_craft_window(self):
        self.hide_window(self.craft_win)
        self.node_bindings(self.inv_win, self._inventory_window_callback)

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

    def add_input_menu(self, label, callback):
        id = self.add_window(6, graphics.InputWindow, 40, 5, 20, 20)
        win = self.win_man.get_window(id)
        win.set_border([COLBORD1,' ',(0,0,0),1])
        win.bgcol = COLBORD2
        win.clear()
        win.set_label(label)
        win.set_length(self.win_man.width-6)
        self.input_bindings(win, callback)
        self.menu_stack.append([id, callback])

    def get_wall_color(self, x, y):
        x, y = abs(x), abs(y)
        col = int((x**2 * 1023 + y*120)**1.9)%len(COLWALLS)
        return COLWALLS[col]

    def get_floor_color(self, x, y):
        x, y = abs(x), abs(y)
        col = int((x**2 * 1023 + y*120)**1.9)%len(COLFLOORS)
        return COLFLOORS[col]

    def set_craft_window(self,win):
        self.craft_win = win

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
                if self.fov_map:
                    lit = self.fov_map.get_lit(i + ox, j + oy)
                    wall = self.fov_map.get_wall(i + ox, j + oy)
                    explored = self.fov_map.get_explored(i + ox, j + oy)
                    if lit[0]:
                        if lit[1] <5 or explored:
                            if wall:
                                col = self.get_wall_color(i + ox, j + oy)
                                tiles.append([i, j, col, ' ', (0,0,0), 1])
                            if not wall:
                                col = self.get_floor_color(i + ox, j + oy)
                                tiles.append([i, j, col, ' ', (0,0,0), 1])
                            self.fov_map.set_explored(i+ox,j+oy)
                        else:
                            pass
                            #tiles.append([i, j, COLBORD2, ' ', (0,0,0), 1])
                    else:
                        if not explored:
                            pass
                            #tiles.append([i, j, COLBORD2, ' ', (0,0,0), 1])
                        else:
                            if wall:
                                col = self.get_wall_color(i + ox, j + oy)
                                tiles.append([i, j, col, ' ', (0,0,0), 1])
                            if not wall:
                                col = self.get_floor_color(i + ox, j + oy)
                                tiles.append([i, j, col, ' ', (0,0,0), 1])
                else:
                    wall = map[i][j][1]
                    if wall:
                        col = self.get_wall_color(i + ox, j + oy)
                        tiles.append([i, j, col, ' ', (0,0,0), 1])
                    if not wall:
                        col = self.get_floor_color(i + ox, j + oy)
                        tiles.append([i, j, col, ' ', (0,0,0), 1])


        win.update_layer(0,tiles)

        tiles = [ ]
#        for id in self.entity_manager.get_ids():
#            if self.entity_manager.get_attribute(id,'visible'):
#                ret = self.get_ent_pos(id)
#                if ret:
#                    tx, ty = ret
#                    ent = self.get_ent(id)
#                    tiles.append([tx-ox, ty-oy, (0,0,0), ent.char, ent.fgcol, 0])

        for i in range(-5, 5):
            for j in range(-5, 5):
                ret = self.get_ent_at(x+i, y+j)
                if ret is not None:
                    for id in ret:
                        if self.fov_map:
                            lit = self.fov_map.get_lit(i + x, j + y)
                            explored = self.fov_map.get_explored(i + x, j + y)
                            if lit[0] and explored and self.entity_manager.get_attribute(id,'visible'):
                                tx, ty = self.get_ent_pos(id)
                                ent = self.get_ent(id)
                                tiles.append([tx-ox, ty-oy, (0,0,0), ent.char, ent.fgcol, 0])
                        else:
                            if self.entity_manager.get_attribute(id,'visible'):
                                tx, ty = self.get_ent_pos(id)
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

    def update(self):
        if self.time_passing:
            self.scheduler.tick()
            if self.game_win is not None and self.get_camera() is not None and self.get_map() is not None:
                self.update_game_window()
                if self.player is not None:
                    self.update_inv_window()
        self.win_man.draw_all()

        #input
        self.keyboard.tick()


app = CustomApp("Working Name",WIDTH,HEIGHT)
game_win = app.add_window(0,graphics.LayeredGameWindow,WIDTH-30,HEIGHT,30,0)
game_win = app.win_man.get_window(game_win)
game_win.set_border([COLBORD1,' ',(0,0,0),1])
game_win.bgcol = COLBORD2
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

craft_win = app.add_window(5,graphics.NodeWindow,30,HEIGHT-20,30,0)
craft_win = app.win_man.get_window(craft_win)
craft_win.set_border([COLBORD1,' ',(0,0,0),1])
craft_win.bgcol = COLBORD2
craft_win.clear()
app.hide_window(craft_win)

app.set_game_window(game_win)
app.set_message_window(msg_win)
app.set_inventory_window(inv_win)
app.set_craft_window(craft_win)
#app.add_messages(("Hello world.",
#                  "This is a test message which should be long enough to wrap, hopefully. "
#                 +"However, that's not enough, so hey, there we go, another line, awesome."))

def main_menu_callback(fct):
    choice = fct()
    if not choice:
        app.generate_map("pre1",MAP_WIDTH,MAP_HEIGHT,set=True)
        app.place_player(1)
        while app.menu_stack:
            app.remove_menu()
        app.add_input_menu("What is your name?", name_menu_callback)
    elif choice == 1:
        app.quit()
    elif choice == 2:
        pass

def name_menu_callback(input):
    input = input.strip()
    if input != "":
        app.get_ent(app.get_player()).name = input
    while app.menu_stack:
        app.remove_menu()
    app.add_choice_menu(("Choose your difficulty: ",), ("Waa~ waaa~ I want my mommy~", "I AM a grownup, you big meanie!",
        "Not bad.", "Here we go."), difficulty_menu_callback)

def difficulty_menu_callback(fct):
    choice = fct()
    if not choice:
        items = 5
    elif choice == 1:
        items = 3
    elif choice == 2:
        items = 1
    else:
        while app.menu_stack:
            app.remove_menu()
        return
    pl = app.get_ent(app.get_player())
    inv = pl.inventory
    for i in range(items):
        it = app.add_entity(0,0,"salve")
        app.set_ent_parent(it,inv)
    while app.menu_stack:
        app.remove_menu()



app.add_choice_menu(("Main menu: ",), ("Start Game", "Quit", "Debug.", "Arrow keys to move;",
    "I, then arrow keys for inventory;", "R in inventory to drop;", "In inventory, right or E to use an item;",
    "In the use item window, right or E to use it on the selected object, Q to go back to the game directly;",
    "E to pick up an item, and F to try and jump, but there's a 15 tick cooldown.",
    "Q to quit the game.", "Report bugs to mike@codingden.net."), main_menu_callback)
while not app.exit:
    app.update()


    
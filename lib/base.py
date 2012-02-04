import random  # TODO: add libtcod RNG and customisable RNG system.
import lib.graphics as graphics
import lib.map as map
import lib.entity_manager as entity_man
import lib.interface as interface
import lib.time as time



class Application(object):
    """
    Main application class.

    After creating, set up the graphics options. Create the map or maps, then entities. Initialise any specifics.
    Then start calling Update every time you want to update.

    """
    
    version = (0, 5, 0, 'b')
    
    def __init__(self, name, w, h):
        self.exit = 0
        
        # One currently loaded map at any one time, referenced by the index it uses in self.maps.
        self.maps = []
        self.map = None
        
        # All entities are scheduled in one global scheduler.
        self.scheduler = time.Scheduler()

        # Entity management done by EntityManager.
        self.entity_manager = entity_man.EntityManager()

        # Player and camera entities are saved so that you could switch cameras
        # OR players quite easily.
        self.player = None
        self.camera = None
        
        # Initialise default windows with None.
        self.win_man = graphics.RootWindow(w,h,name)
        self.game_win = None
        self.msg_win = None
        self.inv_win = None
        
        # Initialise keyboard interface.
        self.keyboard = interface.KeyboardListener()

        # Initialise menus.
        self.menu_stack = [ ]

        self.time_passing = None

    def default_bindings(self):
        """Bind defaults for game."""
        self.time_passing = 1  # TODO: fix this.
        self.clear_bindings()
        player = self.get_ent(self.get_player())
        if player is not None:
            temp = [ ['w',[player.move,(0,-1)]],
                     ['s',[player.move,(0,1)]],
                     ['a',[player.move,(-1,0)]],
                     ['d',[player.move,(1,0)]],
                     ['i',[self.print_player_inventory,()]],
                     ['e',[self.player_pickup,()]],
                     ['q',[self.quit,()]] ]
            for set in temp:
                key = set[0]
                bind = set[1]
                self.add_binding(key,bind)

    def menu_bindings(self, window, callback):
        self.time_passing = 0  # TODO: Fix this.
        self.clear_bindings()
        temp = [ ['w', [window.move_up,()]],
               ['s', [window.move_down,()]],
               ['d', [callback,(window.enter,)]]
        ]
        for set in temp:
            key = set[0]
            bind = set[1]
            self.add_binding(key,bind)

    def generate_map(self,w,h,set):
        """Generates new map using BasicGenerator, then generates basic entities."""
        self.add_map(map=map.BasicGenerator(w,h).gen_map(),
                    set=set)

        # TODO: better entity generation
        m = self.get_map()
        m = m.get_rect(0,0,m.width,m.height)
        s = "#$*()[]"
        for i in range(len(m)):
            for j in range(len(m[i])):
                if not m[i][j][0]:
                    r = random.randint(0,500)
                    if r < 5:
                        id = self.add_entity(i, j)
                        if random.randint(0,100) < 220:
                            self.get_ent(id).set_attribute('solid',0)
                        ent = self.get_ent(id)
                        ent.char = s[random.randint(0,len(s)-1)]
                        ent.fgcol = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
                        if random.randint(0,100) < 50:
                            id2 = self.add_entity(i, j)
                            self.set_ent_pos(id2,id)
                            if random.randint(0,100) < 70:
                                id2 = self.add_entity(i, j)
                                self.set_ent_pos(id2,id)
                                id2 = self.add_entity(i, j)
                                self.set_ent_pos(id2,id)



    def add_map(self,file=0,map=0,set=0):
        """Add map to stack from file or object."""
        if map:
            self.maps += [map]
        elif file:
            pass
        if set:
            self.set_map(len(self.maps)-1)

    def set_map(self,id):
        """Set map as current one."""
        if id < len(self.maps):
            self.map = id
    
    def get_map(self):
        """Get current map."""
        if self.map is not None:
            return self.maps[self.map]
        return None

    def add_window(self,layer,type,w,h,x,y):
        """Add new window and return it."""
        win = self.win_man.add_window(layer,type,w,h,x,y)
        return win

    def clear_layer(self,layer):
        """Deletes all windows on a layer."""
        self.win_man.clear_layer(layer)

    def set_game_window(self,w):
        """Set current game window to use."""
        self.game_win = w

    def set_inventory_window(self,w):
        """Set current inventory window to use."""
        self.inv_win = w

    def set_message_window(self,w):
        """Set current message window to use."""
        self.msg_win = w

    def add_messages(self,msgs):
        """Post messages to current message window, takes a list of strings."""
        if self.msg_win is not None:
            self.msg_win.add_messages(msgs)

    def toggle_window(self,window):
        """Toggle whether a window is visible or not."""
        if self.win_man.get_visible(window):
            self.win_man.hide_window(window)
        else:
            self.win_man.show_window(window)

    def hide_window(self,window):
        """Hide a window."""
        self.win_man.hide_window(window)

    def show_window(self,window):
        """Unhide a window."""
        self.win_man.show_window(window)

    def add_choice_menu(self, labels, choices, callback):
        """Add a single choice menu to the stack and sets it as active.

        Callback is a function that takes one parameter. Parameter is a function called with no parameters of its own
        that returns the index of the highlighted choice, starting from 0.
        """
        id = self.win_man.add_window(5, graphics.ChoiceWindow, self.win_man.width, self.win_man.height, 0, 0)
        win = self.win_man.get_window(id)
        win.set_label(labels)
        win.set_choices(choices)
        self.menu_bindings(win,callback)
        self.menu_stack.append([id,callback])

    def remove_menu(self):
        """Removes the last menu on the stack, and rebinds to the new active menu.

        If no menus remain, rebinds the game.
        """
        self.win_man.remove_window(self.menu_stack[-1][0])
        del self.menu_stack[-1]
        if self.menu_stack:
            id,callback = self.menu_stack[-1]
            win = self.win_man.get_window(id)
            self.menu_bindings(win,callback)
        else:
            self.default_bindings()

    def add_binding(self,key,bind):
        """Add a key binding."""
        self.keyboard.add_binding(key,bind)
    
    def remove_binding(self,key):
        """Remove a key binding."""
        self.keyboard.remove_binding(key)

    def clear_bindings(self):
        """Clear all key bindings."""
        self.keyboard.clear_bindings()

    #entity work
    #[x,y,ent]
    def add_entity(self, x, y, type="entity", delay=1):
        """Create a new entity, gives it an ID, adds it to the entity list, schedules it, and returns its ID.

        Set delay to None for no scheduling.
        """
        id = self.entity_manager.add_entity(self, type)
        self.entity_manager.set_pos(id, (x, y))
        self.entity_manager.set_attribute(id, 'delay', delay)
        if delay is not None:
            self.entity_manager.schedule(self.scheduler, id)
        self.entity_manager.get_ent(id).id = id
        self.entity_manager.get_ent(id).name += ' #'+str(id)
        return id

    def place_player(self,delay):
        """Add a player entity and camera and set it as the current player."""
        map = self.get_map()
        if map is None:
            raise NoMapError
        tiles = map.get_rect(0,0,3,map.height)
        x, y = 0, 0
        for i in range(len(tiles)):
            for j in range(len(tiles[i])):
                if not tiles[i][j][0]:
                    x, y = i, j
        pid = self.add_entity(x, y, 'player', delay)
        cam = self.add_entity(x, y, 'camera', None)
        sch_id = self.scheduler.add_schedule( (self.get_ent(cam).sync_camera, [pid], 1) )
        self.entity_manager.set_sched(cam, sch_id)
        self.scheduler.set_dominant(self.entity_manager.get_sched(pid))
        self.player = pid
        self.camera = cam
        return pid

    def get_ent(self, id):
        """Raises IDNotFound if entity doesn't exist and NullID if passed None."""
        return self.entity_manager.get_ent(id)

    def get_ent_at(self, x, y):
        """Returns list of entities on tile or None."""
        return self.entity_manager.get_at(x, y)

    def get_ent_in(self, obj):
        """Returns list of entities contained by obj or None."""
        return self.entity_manager.get_in(obj)

    def get_player(self):
        """Returns current player ID or None."""
        return self.player

    def get_camera(self):
        """Returns current camera ID or None."""
        return self.camera

    def get_ent_pos(self, id):
        """Returns (x,y) or id of container for entity, can raise IDNotFound."""
        return self.entity_manager.get_pos(id)

    def set_ent_pos(self, id, pos):
        """Sets an entity's position as the object passed, tuple or int; pass the container id for contained ents."""
        self.entity_manager.set_pos(id, pos)

    def destroy_ents(self):
        """Destroy all entities."""
        pass

    def try_entity_move_relative(self, id, x, y):
        """Checks collisions and restrictions in place, then tries to move an entity; generally only called by Ents."""
        can_move = 1
        ex, ey = self.get_ent_pos(id)
        if self.get_map() is not None:
            # check for wall
            if self.get_map().get_tile(x + ex, y + ey)[0]:
                can_move = 0
            if self.get_ent(id).get_attribute('solid'):
                ents = self.get_ent_at(x + ex, y + ey)
                if ents is not None:
                    for ent in ents:
                        if self.get_ent(ent).get_attribute('solid'):
                            can_move = 0
            if can_move:
                self.entity_move(id, x + ex, y + ey)
        else:
            raise NoMapError

    def try_entity_move_to_entity(self, id, id2):
        """Tries moving entity id to entity id2."""
        x, y = self.get_ent_pos(id2)
        ex, ey = self.get_ent_pos(id)
        self.try_entity_move_relative(id, x-ex, y-ey)

    def entity_move(self, id, x, y):
        """Directly move an entity, no checks; generally called by try_entity_move_*."""
        self.entity_manager.set_pos(id, (x,y))
        if self.get_player() is id:
            self.examine_tile(x,y)

    def player_pickup(self):
        """Attempt to have the player pick up everything on the tile he's on."""
        pl = self.get_player()
        x, y = self.get_ent_pos(pl)
        ents = self.get_ent_at(x, y)
        msg = 'You pick up: '
        count = 0
        for id in ents:
            if id is not self.get_player():
                if self.get_ent(id).get_attribute('liftable'):
                    msg += self.get_ent(id).name + ', '
                    count += 1
                    self.set_ent_pos(id,pl)
        if count:
            msg = msg[:-2] + '.'
            self.add_messages([msg])

    def print_player_inventory(self):
        """Prints the player's inventory to the message window."""
        pl = self.get_player()
        ents = self.get_ent_in(pl)
        if ents is not None:
            msg = 'You currently have: '
            for id in ents:
                msg += self.get_ent(id).name + ', '
            msg = msg[:-2] + '.'
            self.add_messages([msg])
        else:
            msg = 'You have nothing on you.'
            self.add_messages([msg])


    def examine_tile(self, x, y):
        """Examines a tile and displays messages that list the entities on it, excluding the current player."""
        ents = self.get_ent_at(x, y)
        if ents == [self.get_player()]:
            return None
        else:
            msg = 'You see here: '
            for id in ents:
                if id is not self.get_player():
                    ent = self.get_ent(id)
                    msg += ent.name + ', '
            msg = msg[:-2] + '.'
        self.add_messages([msg])
        return ents

    def _inv_window_recurse(self,id,parents=None,names=None,cur_id=1,parent_id=0):
        """Internal recursion method for inventory listing."""
        if not names: names = {}
        if not parents: parents = {}
        ents = self.get_ent_in(id)
        if ents is not None:
            for child in ents:
                orig_id = cur_id
                names[cur_id] = self.get_ent(child).name
                parents[cur_id] = parent_id
                cur_id += 1
                parents, names, cur_id = self._inv_window_recurse(child,parents,names,cur_id,orig_id)
        return parents, names, cur_id

    def update_inv_window(self):
        """Default implementation of inventory window updating."""
        if self.inv_win is None:
            return  #TODO: Error handling.
        player = self.get_player()
        names = {0:self.get_ent(player).name}
        parents = {0:None}
        parents, names, tmp = self._inv_window_recurse(player,parents,names)
        self.inv_win.set_nodes(parents,names)

    def update_game_window(self):
        """Default implementation of graphics updating, updates map and entities; doesn't redraw walls."""
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
                if map[i][j] == (0,0):
                    tiles.append([i, j, (0,0,0), ' ', (0,0,0), 1])
        win.update_layer(0,tiles)

        tiles = [ ]
        for id in self.entity_manager.get_ids():
            if self.entity_manager.get_ent(id).drawn:
                tx, ty = self.get_ent_pos(id)
                ent = self.get_ent(id)
                tiles.append([tx-x+cx, ty-y+cy, (0,0,0), ent.char, ent.fgcol, 0])
        win.update_layer(4,tiles)

        tiles = [ ]
        pid = self.get_player()
        if pid is not None:
            tiles.append([cx, cy, (255,0,0), '@', (255,255,255), 0])
            win.update_layer(5,tiles)

    def update(self):
        """Update function, called every tick."""
        if self.time_passing:
            self.scheduler.tick()
            if self.game_win is not None and self.get_camera() is not None and self.get_map() is not None:
                self.update_game_window()
                if self.player is not None:
                    self.update_inv_window()
            #if self.msg_win is not None:
            #    ticks = self.scheduler.ticks
            #    self.add_messages(["Ticks: "+str(ticks)])
        self.win_man.draw_all()

        #input
        self.keyboard.tick()



    def quit(self):
        """Exit application."""
        self.exit = 1


class Error(Exception):
    """Base class for errors."""
    pass

class NoMapError(Error):
    """A function that needs a map has been called, with no map loaded."""
    pass

class IDNotFound(Error):
    """An ID has been requested and not found in the list."""
    pass

class NullID(Error):
    """An ID of None has been requested."""
    pass
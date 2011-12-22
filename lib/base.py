import lib.graphics as graphics
import lib.map as map
import lib.entity as entity
import lib.interface as interface
import lib.time as time



class Application:
    """
    Main application class.

    After creating, set up the graphics options. Create the map or maps, then entities. Initialise any specifics.
    Then start calling Update every time you want to update.

    """
    
    version = (0, 5, 0, 'a')
    
    def __init__(self, name, w, h):
        self.exit = 0
        
        # One currently loaded map at any one time, referenced by the index it uses in self.maps.
        self.maps = []
        self.map = None
        
        # All entities are scheduled in one global scheduler.
        self.scheduler = time.Scheduler()
                
        # Entities are kept in a dictionary as an id. Keys are a tuple of (x, y).
        # This allows for fast checking for entities in tiles, and raises
        # only a slight problem in keeping them in sync. Picking a class for
        # add_entity is done via the entity manager transparently. Send a string
        # like 'item'. ID lookup is in entity_list. Scheduling IDs are in entity_schedules
        self.entity_lookup = entity.EntityLookup()
        self.entity_list = { }
        self.entity_pos = { }
        self.entity_schedules = { }
        self.entity_cur_id = 0

        # Player and camera entities are saved so that you could switch cameras
        # OR players quite easily.
        self.player = None
        self.camera = None
        
        # Initialise default windows with None.
        self.win_man = graphics.RootWindow(w,h,name)
        self.game_win = None
        self.msg_win = None
        
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
        """Generates new map and adds it, using BasicGenerator from map."""
        self.add_map(map=map.BasicGenerator(w,h).gen_map(),
                    set=set)

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
        self.invWin = w

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
        ent = self.entity_lookup.get_class(type)(self)
        ent.set_attribute('delay',delay)
        id = self.entity_cur_id
        ent.id = id
        self.entity_list[id] = ent
        if delay is not None:
            self.entity_schedules[id] = self.scheduler.add_schedule((ent.update,(),delay))
        else:
            self.entity_schedules[id] = None
        self.entity_pos[id] = (x, y)
        return id

    def place_player(self,delay):
        """Add a player entity and camera and set it as the current player."""
        map = self.get_map()
        if map is None:
            raise Exception  # TODO exceptions
        tiles = map.get_rect(0,0,3,map.height)
        x, y = 0, 0
        for i in range(len(tiles)):
            for j in range(len(tiles[i])):
                if not tiles[i][j][0]:
                    x, y = i, j
        pid = self.add_entity(x, y, 'player', delay)
        cam = self.add_entity(x, y, 'camera', None)
        self.entity_schedules[cam] = self.scheduler.add_schedule( (self.get_ent(cam).sync_camera, [pid], 1) )
        self.scheduler.set_dominant(self.entity_schedules[pid])
        self.player = pid
        self.camera = cam
        return pid

    def get_ent(self, id):
        if id not in self.entity_list:
            raise Exception  # TODO add exceptions!
        return self.entity_list[id]

    def get_player(self):
        """Returns current player ID or None."""
        return self.player

    def get_camera(self):
        """Returns current camera ID or None."""
        return self.camera

    def get_ent_pos(self, id):
        """Returns (x,y) based on ID, or None."""
        if id not in self.entity_list:
            raise Exception  # TODO add exceptions!
        return self.entity_pos[id]

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
            if can_move:
                self.entity_move(id, x + ex, y + ey)
        else:
            raise Exception  # TODO: Add exceptions!

    def try_entity_move_to_entity(self, id, id2):
        """Tries moving entity id to entity id2."""
        x, y = self.get_ent_pos(id2)
        ex, ey = self.get_ent_pos(id)
        self.try_entity_move_relative(id, x-ex, y-ey)

    def entity_move(self, id, x, y):
        """Directly move an entity, no checks; generally called by try_entity_move_*."""
        self.entity_pos[id] = (x, y)

    def update_game_window(self):
        cam = self.get_camera()
        map = self.get_map()
        win = self.game_win
        pos = self.get_ent_pos(cam)
        if pos is None:
            raise Exception  # TODO Make exceptions for everything.
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
        pid = self.get_player()
        if pid is None:
            raise Exception # TODO No-one excepts the spanish inquisition.
        tiles.append([cx, cy, (255,0,0), '@', (255,255,255), 0])
        win.update_layer(5,tiles)

    def update(self):
        """Update function, called every tick."""
        if self.time_passing:
            if self.game_win is not None and self.get_camera() is not None and self.get_map() is not None:
                self.update_game_window()
            if self.msg_win is not None:
                ticks = self.scheduler.ticks
                self.add_messages(["Ticks: "+str(ticks)])
            self.scheduler.tick()
        self.win_man.draw_all()

        #input
        self.keyboard.tick()



    def quit(self):
        """Exit application."""
        self.exit = 1

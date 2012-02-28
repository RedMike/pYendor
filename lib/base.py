import random  # TODO: add libtcod RNG and customisable RNG system.
import lib.graphics as graphics
import lib.map as map
import lib.entity_manager as entity_man
import lib.interface as interface
import lib.time as time


class Application(object):
    """
    Main application class.

    Subclass this to modify basic functionality, or replace a module with one of your own.

    After creating the application object, create any windows using L{add_window}, set the default
    windows with L{set_game_window}, L{set_message_window}, L{set_inventory_window} if you do not wish
    to handle drawing and updating yourself, define your menu callbacks, then use L{add_choice_menu}
    to create a main menu, if you wish it. After this, loop while checking if L{exit} is false, and
    run L{self.update} every iteration.

    """
    
    version = (0, 5, 0, 'b')
    
    def __init__(self, name, w, h):
        """Initialise the application with basic default values.

        @type  name: string
        @param name: Main window name.
        @type  w: number
        @param w: Main window width.
        @type  h: number
        @param h: Main window height.
        """
        self.exit = 0
        
        # One currently loaded map at any one time, referenced by the index it uses in self.maps.
        self.maps = []
        self.map = None
        
        # All entities are scheduled in one global scheduler.
        self.scheduler = time.Scheduler()

        # Entity management done by EntityManager.
        self.entity_manager = entity_man.EntityManager(self)

        # Player and camera entities are saved so that you could switch cameras
        # OR players quite easily.
        self.player = None
        self.camera = None
        
        # Initialise default windows with None.
        self.win_man = graphics.WindowManager(w,h,name)
        self.game_win = None
        self.msg_win = None
        self.inv_win = None
        
        # Initialise keyboard interface.
        self.keyboard = interface.KeyboardListener()

        # Initialise menus.
        self.menu_stack = [ ]

        self.time_passing = None

        self.debug = 1

    def default_bindings(self):
        """Bind default game keys.

        Any custom bindings are cleared, and keys are only bound if L{get_player} returns non-None.
        Basic keys are:
            - B{Movement}: W, A, S, D
            - B{Inventory}: I
            - B{Actions}: E, R
            - B{Application}: Q
        Where E and R are pick up and drop, respectively, and Q sets L{exit} to I{true}.
        """
        self.time_passing = 1  # TODO: fix this.
        self.clear_bindings()
        player = self.get_ent(self.get_player())
        if player is not None:
            temp = [ [self.keyboard.KEY_UP,[player.move,(0,-1)]],
                     [self.keyboard.KEY_DOWN,[player.move,(0,1)]],
                     [self.keyboard.KEY_LEFT,[player.move,(-1,0)]],
                     [self.keyboard.KEY_RIGHT,[player.move,(1,0)]],
                     ['i',[self.node_bindings,(self.inv_win, self._inventory_window_callback)]],
                     ['e',[self.player_pickup,()]],
                     ['r',[self.player_drop,()]],
                     ['q',[self.quit,()]],
                     [self.keyboard.KEY_ESCAPE, [self.quit, ()]],
                     ['t',[self.add_input_menu,(">>> ",)]]]
            for set in temp:
                key = set[0]
                bind = set[1]
                self.add_binding(key,bind)

    def node_bindings(self, window, callback):
        """Bind default node window keys.

        Any custom bindings are cleared, and keys are bound for the window and callback you pass.

        @type  window: L{graphics.Window}
        @param window: Window to bind to as menu.
        """
        self.time_passing = 0  # TODO: Fix this.
        self.clear_bindings()
        if window.highlight is None:
            window.highlight = 0
        self.keyboard.set_default_binding(callback, (window,))

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
        elif char == 'q':
            window.highlight = None
            self.time_passing = 1
            self.default_bindings()
        elif char == 'r':
            ent_id, usable = window.get_node_meta(window.highlight)
            if usable:
                self.player_drop(ent_id)
        elif char == 'e':
            pl = self.get_player()
            pl_ent = self.get_ent(pl)
            ent_id, usable = window.get_node_meta(window.highlight)
            if usable and not self.get_ent_in(pl_ent.nodes['r_hand']):
                self.set_ent_parent(ent_id, pl_ent.nodes['r_hand'])
            elif not usable and self.get_ent_in(pl_ent.nodes['r_hand']) is not None:
                for ent in self.get_ent_in(pl_ent.nodes['r_hand']):
                    if self.get_ent(ent).get_attribute('usable'):
                        self.set_ent_parent(ent, ent_id)
        self.update_inv_window()

    def input_bindings(self, window):
        """Bind default input keys.

        Any custom bindings are cleared, and keys are bound for the window and callback you pass.

        @type  window: L{graphics.Window}
        @param window: Window to bind to as menu.
        """
        self.time_passing = 0  # TODO: Fix this.
        self.clear_bindings()
        self.keyboard.set_default_binding(self._input_window_callback, (window,))

    def _input_window_callback(self, mods, char, vk, window):
        """Default input window callback.
        Gets called while an input window is on the screen and a key is pressed.

        @type  mods: dict
        @param mods: Modifier state in the form of {'lalt', 'ralt', 'lctrl', 'rctrl', 'shift'}
        @type  char: char
        @param char: If vk is KEY_CHAR, this is the printable character
        @type  vk: int
        @param vk: Keycode, check against L{interface.KeyboardListener}.KEY_*
        """
        if vk == interface.KeyboardListener.KEY_BACKSPACE:
            window.backspace()
        elif vk == interface.KeyboardListener.KEY_ENTER:
            #DEBUG ONLY!
            try:
                s = window.enter()
                exec s
            except Exception as e:
                self.add_messages((str(e),))
            self.remove_menu()
        elif vk == interface.KeyboardListener.KEY_SPACE:
            window.add_char(' ')
        elif interface.KeyboardListener.KEY_0 <= vk <= interface.KeyboardListener.KEY_9:
            window.add_char(char)
        elif vk == interface.KeyboardListener.KEY_CHAR:
            if mods['shift']:
                window.add_char(char.upper())
            else:
                window.add_char(char)

    def menu_bindings(self, window, callback):
        """Bind default menu keys.

        Any custom bindings are cleared, and keys are bound for the window and callback you pass.

        @type  window: L{graphics.Window}
        @param window: Window to bind to as menu.
        @type  callback: Function.
        @param callback: Function that gets called on accept.
        """
        self.time_passing = 0  # TODO: Fix this.
        self.clear_bindings()
        temp = [ [self.keyboard.KEY_UP, [window.move_up,()]],
               [self.keyboard.KEY_DOWN, [window.move_down,()]],
               [self.keyboard.KEY_ENTER, [callback,(window.enter,)]]
        ]
        for set in temp:
            key = set[0]
            bind = set[1]
            self.add_binding(key,bind)

    def generate_map(self,w,h,set):
        """Generates new map using BasicGenerator, then generates basic entities.

        @type  w: number
        @param w: Width of map.
        @type  h: height
        @param h: Height of map.
        @type  set: bool
        @param set: If true, sets map as active.
        """
        gen = map.BlockGenerator(w,h)
        gen.set_layout('test')
        m = gen.gen_map()
        ents = gen.entities
        self.generate_ents(ents)
        self.add_map(map=m,
                    set=set)

    def generate_ents(self,list):
        """Populates map with entities, takes a list of (x, y, entity_lookup_name, chance),
            where chance is a float in [0,1]."""
        for set in list:
            x, y, ent_string, chance = set
            r = random.random()
            if r < chance:
                self.add_entity(x, y, ent_string)

    def add_map(self,file=0,map=0,set=0):
        """Add map to stack from file or object.

        @type  file: string
        @param file: Path to file.
        @type  map: L{map.Map}
        @param map: Map object to add to stack.
        @type  set: bool
        @param set: If true, set as active.
        """
        if map:
            self.maps += [map]
        elif file:
            pass
        if set:
            self.set_map(len(self.maps)-1)

    def set_map(self,id):
        """Set map as I{id}."""
        if id < len(self.maps):
            self.map = id
    
    def get_map(self):
        """Returns current map, or I{None}."""
        if self.map is not None:
            return self.maps[self.map]
        return None

    def add_window(self,layer,type,w,h,x,y):
        """Create a new window and return its ID.

        @type  layer: number
        @param layer: Layer to place window on. Higher means drawn on top.
        @type  type: subclass of graphics.Window or compatible substitute
        @param type: Window type that gets created.
        @type  w: number
        @param w: Width of window.
        @type  h: number
        @param h: Height of window.
        @type  x: number
        @param x: X coordinate of top-left corner.
        @type  y: number
        @param y: Y coordinate of top-left corner.
        @rtype: number
        @return: Window ID of created window; Use L{graphics.WindowManager.get_window} to get the object.
        """
        win = self.win_man.add_window(layer,type,w,h,x,y)
        return win

    def clear_layer(self,layer):
        """Deletes all windows on a layer."""
        self.win_man.clear_layer(layer)

    def set_game_window(self,w):
        """Set game window to draw_tiles by default.

        In order to draw_tiles several windows or use a different updating algorithm, leave this as
        I{None} and roll your own updating algorithm following L{update_game_window}.
        """
        self.game_win = w

    def set_inventory_window(self,w):
        """Set inventory window to use by default.

        In order to draw_tiles several windows or use a different updating algorithm, leave this as
        I{None} and roll your own updating algorithm following L{update_inv_window}.
        """
        self.inv_win = w

    def set_message_window(self,w):
        """Set message window to use by default.

        In order to draw_tiles several windows or use a different updating algorithm, leave this as
        I{None} and roll your own updating algorithm following L{add_messages}.
        """
        self.msg_win = w

    def add_messages(self,msgs):
        """Post messages to current message window, takes a list of strings.

        For using a different updating algorithm, you could, for example, prepend each string
        with a specific character, and subclass and replace this method to separate into several
        windows by the prepended character, and ommiting it from display.

        @type  msgs: tuple
        @param msgs: A list of messages to display.
        """
        if self.msg_win is not None:
            self.msg_win.add_messages(msgs)

    def toggle_window(self,window):
        """Toggle whether a window is visible or not.

        Convenience function, calls L{window manager <graphics.WindowManager>} functions.

        @type  window: number
        @param window: ID of window to toggle.
        """
        if self.win_man.get_visible(window):
            self.win_man.hide_window(window)
        else:
            self.win_man.show_window(window)

    def hide_window(self,window):
        """Hide a window.

        Convenience function, calls L{window manager <graphics.WindowManager>} functions.
        """
        self.win_man.hide_window(window)

    def show_window(self,window):
        """Unhides a window.

        Convenience function, calls L{window manager <graphics.WindowManager>} functions.
        """
        self.win_man.show_window(window)

    def get_menu_window(self):
        """Returns current menu window or None."""
        if len(self.menu_stack) > 0:
            return self.win_man.get_window(self.menu_stack[-1][0])

    def add_input_menu(self, label):
        """Adds an input menu to the stack and sets it as active.

        Callback gets called with a method that returns the string that was in the list.

        @type  label: string
        @param label: Text to display before input bar.
        """
        id = self.add_window(6, graphics.InputWindow, self.win_man.width, 6, 0, self.win_man.height-6)
        win = self.win_man.get_window(id)
        win.set_label(label)
        win.set_length(self.win_man.width-6)
        self.input_bindings(win)
        self.menu_stack.append([id])

    def add_choice_menu(self, labels, choices, callback):
        """Adds a single choice menu to the stack and sets it as active.

        ID of choice in choices is the ID that gets used in callback, starting from 0.

        @type  labels: tuple
        @param labels: List of strings that are displayed before choices.
        @type  choices: tuple
        @param choices: List of valid choices in the menu.
        @type  callback: method
        @param callback: Function that gets called with a function as a parameter, that returns the ID
                        of the choice selected, when called.
        """
        id = self.add_window(5, graphics.ChoiceWindow, self.win_man.width, self.win_man.height, 0, 0)
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
            if win == graphics.ChoiceWindow:
                self.menu_bindings(win,callback)
            elif win == graphics.InputWindow:
                self.input_bindings(win)
        else:
            self.default_bindings()

    def add_binding(self,key,bind):
        """Add a key binding.

        Convenience function, passes to L{interface module <interface.KeyboardListener>}.
        """
        self.keyboard.add_char_binding(key,bind)
    
    def remove_binding(self,key):
        """Remove a key binding.

        Convenience function, passes to L{interface module <interface.KeyboardListener>}.
        """
        self.keyboard.remove_binding(key)

    def clear_bindings(self):
        """Clear all key bindings.

        Convenience function, passes to L{interface module <interface.KeyboardListener>}.
        """
        self.keyboard.clear_bindings()

    def add_entity(self, x, y, type="entity", delay=1):
        """Create a new entity at a position and return the ID.

        Set delay to I{None} for no calls to the draw_tiles method.

        @type  x: number
        @param x: X coordinate of entity position
        @type  y: number
        @param y: Y coordinate of entity position
        @type  type: string
        @param type: Type of object to be created, from L{entity.EntityLookup}.
        @type  delay: number
        @param delay: Number of ticks inbetween calls of the entity's draw_tiles method.
        """
        id = self.entity_manager.add_entity(type,delay)
        self.entity_manager.set_pos(id, (x, y))
        #self.entity_manager.get_ent(id).name += '#'+str(id)  # TODO: remove debug ids
        return id

    def place_player(self,delay):
        """Convenience method that adds a player entity, a camera entity, and returns the player ID.

        Player is placed in the first available tile on the first 3 columns of the map.
        """
        map = self.get_map()
        if map is None:
            raise NoMapError
        tiles = map.get_rect(0,0,map.width,map.height)
        x, y = 0, 0
        for i in range(len(tiles)):
            for j in range(len(tiles[i])):
                if not tiles[i][j][0]:
                    x, y = i, j
                    break
        pid = self.add_entity(x, y, 'player', delay)
        cam = self.add_entity(x, y, 'camera', None)
        sch_id = self.scheduler.add_schedule( (self.get_ent(cam).sync_camera, [pid], 1) )
        self.entity_manager.set_sched(cam, sch_id)
        self.scheduler.set_dominant(self.entity_manager.get_sched(pid))
        self.player = pid
        self.camera = cam
        return pid

    def get_ent(self, id):
        """Convenience method, passes call to {entity manager<entity_manager.EntityManager>}.

        Raises IDNotFound if entity doesn't exist and NullID if passed None.
        """
        return self.entity_manager.get_ent(id)

    def get_ent_at(self, x, y):
        """Convenience method, passes call to {entity manager<entity_manager.EntityManager>}.

        Returns list of entities on tile or None.
        """
        return self.entity_manager.get_at(x, y)

    def get_ent_in(self, obj):
        """Convenience method, passes call to {entity manager<entity_manager.EntityManager>}.

        Returns list of entities contained by obj or None.
        """
        return self.entity_manager.get_in(obj)

    def get_player(self):
        """Returns current player ID or None."""
        return self.player

    def get_camera(self):
        """Returns current camera ID or None."""
        return self.camera

    def get_ent_pos(self, id):
        """Convenience method, passes call to {entity manager<entity_manager.EntityManager>}.

        Returns (x,y) or None, can raise IDNotFound.
        """
        return self.entity_manager.get_pos(id)

    def set_ent_pos(self, id, pos):
        """Convenience method, passes call to {entity manager<entity_manager.EntityManager>}.

        @type  id: number
        @param id: ID of entity to be placed.
        @type  pos: tuple
        @param pos: Position of entity, (x,y) tuple.

        Sets an entity's position as the object passed, tuple of shape (x,y).
        Unsets parenting, so the entity is placed directly onto the map, if called.
        """
        self.entity_manager.set_pos(id, pos)

    def set_ent_parent(self, id, parent_id):
        """Convenience method, passes call to {entity manager<entity_manager.EntityManager>}.

        @type  id: number
        @param id: ID of entity to be contained.
        @type  parent_id: ID of container.
        @param parent_id: Container object to place entity in.

        Unsets position.
        """
        self.entity_manager.set_parent(id, parent_id)

    def destroy_ents(self):
        """Destroy all entities.

        Not yet implemented.
        """
        pass

    def collision_check(self, id, x, y):
        """Checks collisions and restrictions in place, returns I{True} for able to move.

        Raises NoMapError when map is not initialised yet.
        """
        can_move = True
        ex, ey = self.get_ent_pos(id)
        if self.get_map() is not None:
            # check for wall
            if self.get_map().get_tile(x + ex, y + ey)[0]:
                can_move = False
            # check if we're blocking or not
            if self.entity_manager.get_attribute(id,'blocking'):
                # we are, let's check for entities on that spot, if they're blocking
                ents = self.get_ent_at(x + ex, y + ey)
                if ents is not None:
                    for ent in ents:
                        if self.entity_manager.get_attribute(ent,'blocking'):
                            can_move = False
            return can_move
        else:
            raise NoMapError

    def player_drop(self, id=None):
        """Attempt to have the player drop whatever is in his hand."""
        pl = self.get_player()
        pl_ent = self.get_ent(pl)
        pos = self.get_ent_pos(pl)
        if id is None:
            if self.get_ent_in(pl_ent.nodes['r_hand']):
                for id in self.get_ent_in(pl_ent.nodes['r_hand']):
                    self.set_ent_pos(id,pos)
            if self.get_ent_in(pl_ent.nodes['l_hand']):
                for id in self.get_ent_in(pl_ent.nodes['l_hand']):
                    self.set_ent_pos(id,pos)
        else:
            self.set_ent_pos(id,pos)

    def player_pickup(self):
        """Attempt to have the player pick up everything on the tile he's on.

        Places items into r_hand or l_hand by default.
        """
        pl = self.get_player()
        pl_ent = self.get_ent(pl)
        x, y = self.get_ent_pos(pl)
        ents = self.get_ent_at(x, y)
        for id in ents: # TODO: pickup menu
            if id is not self.get_player():
                if self.entity_manager.get_attribute(id,'liftable'):
                    if not self.get_ent_in(pl_ent.nodes['r_hand']):
                        self.set_ent_parent(id,pl_ent.nodes['r_hand'])
                        break
                    elif not self.get_ent_in(pl_ent.nodes['l_hand']):
                        self.set_ent_parent(id,pl_ent.nodes['l_hand'])
                        break


    def _inv_window_recurse(self,id,parents=None,names=None,meta=None,cur_id=1,parent_id=0):
        """Internal recursion method for inventory listing with default node window."""
        if not names: names = {}
        if not parents: parents = {}
        if not meta: meta = {}
        ents = self.get_ent_in(id)
        if ents is not None:
            for child in ents:
                orig_id = cur_id
                names[cur_id] = self.entity_manager.get_name(child)
                parents[cur_id] = parent_id
                meta[cur_id] = (child,self.entity_manager.get_ent(child).get_attribute('usable'))
                cur_id += 1
                parents, names, meta, cur_id = self._inv_window_recurse(child,parents,names,meta,cur_id,orig_id)
        return parents, names, meta, cur_id

    def update_inv_window(self):
        """Default implementation of inventory window updating.

        Subclass and replace to use a different format or a different window type.
        """
        if self.inv_win is None:
            return  #TODO: Error handling.
        player = self.get_player()
        names = {0:self.entity_manager.get_name(player)}
        parents = {0:None}
        meta = {0:(player,False)}
        parents, names, meta, cur_id = self._inv_window_recurse(player,parents,names,meta)
        self.inv_win.set_nodes(parents,names,meta)

    def update_game_window(self):
        """Default implementation of graphics updating, updates map and entities; doesn't redraw walls.

        Subclass and replace to use a different format.
        """
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
            if self.entity_manager.get_attribute(id,'visible'):
                ret = self.get_ent_pos(id)
                if ret is not None:
                    tx, ty = ret
                    ent = self.get_ent(id)
                    tiles.append([tx-x+cx, ty-y+cy, (0,0,0), ent.char, ent.fgcol, 0])
        win.update_layer(4,tiles)

        #tiles = [ ]
        #pid = self.get_player()
        #if pid is not None:
        #    tiles.append([cx, cy, (255,0,0), '@', (255,255,255), 0])
        #    win.update_layer(5,tiles)

    def update(self):
        """Update function, called every update.

        Subclass and replace to add code to run every working update, or drawing calls.
        """
        if self.time_passing:
            self.scheduler.tick()
            if self.game_win is not None and self.get_camera() is not None and self.get_map() is not None:
                self.update_game_window()
                if self.player is not None:
                    self.update_inv_window()
        self.win_man.draw_all()

        #input
        self.keyboard.tick()

    def quit(self):
        """Exit application."""
        self.exit = 1


class Error(Exception):
    """Base class for errors."""

class NoMapError(Error):
    """A function that needs a map has been called, with no map loaded."""

class IDNotFound(Error):
    """An ID has been requested and not found in the list."""

class NullID(Error):
    """An ID of None has been requested."""

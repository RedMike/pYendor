import random  # TODO: add libtcod RNG and customisable RNG system.
import lib.graphics as graphics
import lib.map as map
import lib.entity_manager as entity_man
import lib.interface as interface
import lib.time as time
import lib.fov as fov


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
        self.inv_win = None
        self.msg_win = None
        self.create_windows()

        self.fov_map = True
        
        # Initialise keyboard interface.
        self.keyboard = interface.KeyboardListener()

        # Initialise menus.
        self.menu_stack = [ ]

        self.time_passing = True

    def change_color_scheme(self, bgcol, fgcol, game_wall_col, game_floor_col, game_fog_floor_col):
        self.bgcol = bgcol
        self.fgcol = fgcol
        self.floor_col = game_floor_col
        self.fog_floor_col = game_fog_floor_col
        self.wall_col = game_wall_col
        for window in self.win_man:
            window.bgcol = self.bgcol
            window.fgcol = self.fgcol
            window.clear()
        if self.game_win:
            self.game_win.bgcol = self.wall_col
            self.game_win.clear()

    def create_windows(self):
        """Create default windows; Subclass to easily set a different layout."""
        bgcol = (0,0,0)
        fgcol = (255,255,255)
        wall_col = None
        floor_col = None
        fog_floor_col = None

        #create windows here

        self.change_color_scheme(bgcol,fgcol,wall_col,floor_col,fog_floor_col)

    def default_bindings(self):
        """Bind default game keys.

        Any custom bindings are cleared, and keys are only bound if L{get_player} returns non-None.
        Basic keys are:
            - B{Movement}: W, A, S, D
            - B{Inventory}: I
            - B{Actions}: E
            - B{Application}: Q, Escape
        Where E is pick up.
        """
        self.clear_bindings()
        player = self.entity_manager[self.player]
        if player is not None:
            temp = [ ['arrow_up',[player.move,(0,-1)]],
                     ['arrow_down',[player.move,(0,1)]],
                     ['arrow_left',[player.move,(-1,0)]],
                     ['arrow_right',[player.move,(1,0)]],
                     ['i',[self.node_bindings,(self.inv_win, self._inventory_window_callback)]],
                     ['e',[self.player_pickup,()]],
                     ['q',[self.quit,()]],
                     ['escape', [self.quit, ()]]]
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
        @param vk: Keycode, check against L{interface.KeyboardListener}.char_codes
        """
        if vk == self.keyboard.char_codes['arrow_up']:
            if window.highlight > 0:
                window.highlight -= 1
        elif vk == self.keyboard.char_codes['arrow_down']:
            if window.highlight < len(window.messages):
                window.highlight += 1
        elif char == 'q':
            window.highlight = None
            self.default_bindings()
        elif char == 'd':
            node = window.highlight
            ent_id, usable = window.get_node_meta(node)
            self.entity_manager.ent_drop(ent_id)
            if window.activated_node == node:
                window.activated_node = None
        elif char == 'r':
            if window.activated_node:
                window.activated_node = None
        elif char == 'e':
            if not window.activated_node:
                node = window.highlight
                window.activated_node = node
            else:
                active, active_usable = window.get_node_meta(window.activated_node)
                node, node_usable = window.get_node_meta(window.highlight)
                self.entity_manager.ent_use(node, active)
                self.update_inv_window()
                window.highlight_node_by_meta(active)
        elif char == 'f':
            ent_id, usable = window.get_node_meta(window.highlight)
            self.entity_manager.ent_activate(ent_id)
        self.update_inv_window()

    def input_bindings(self, window, return_callback, remove=True):
        """Bind default input keys.

        Any custom bindings are cleared, and keys are bound for the window and callback you pass.

        @type  window: L{graphics.Window}
        @param window: Window to bind to as menu.
        """
        self.clear_bindings()
        self.keyboard.set_default_binding(self._input_window_callback, (window,return_callback,remove))

    def _pickup_window_callback(self, ret):
        options, switches, meta = ret() or (None, None, None)
        if switches:
            for i in range(len(options)):
                if switches[i]:
                    self.entity_manager.ent_lift(self.entity_manager[self.player].inventory, meta[i])
            self.remove_menu()

    def _input_window_callback(self, mods, char, vk, window, enter_callback, remove=True):
        """Default input window callback.
        Gets called while an input window is on the screen and a key is pressed.

        @type  mods: dict
        @param mods: Modifier state in the form of {'lalt', 'ralt', 'lctrl', 'rctrl', 'shift'}
        @type  char: char
        @param char: If vk is KEY_CHAR, this is the printable character
        @type  vk: int
        @param vk: Keycode, check against L{interface.KeyboardListener}.KEY_*
        """
        if char != '':
            if mods['shift']:
                window.add_char(char.upper())
            else:
                window.add_char(char)
        else:
            if vk == interface.KeyboardListener.char_codes['backspace']:
                window.backspace()
            elif vk == interface.KeyboardListener.char_codes['enter']:
                s = window.enter()
                if s:
                    enter_callback(s)
                if remove:
                    self.remove_menu()

    def _input_window_return_callback(self, line):
        try:
            exec line
        except Exception as e:
            self.add_messages((str(e),))
        self.remove_menu()

    def menu_bindings(self, window, callback):
        """Bind default menu keys.

        Any custom bindings are cleared, and keys are bound for the window and callback you pass.

        @type  window: L{graphics.Window}
        @param window: Window to bind to as menu.
        @type  callback: Function.
        @param callback: Function that gets called on accept.
        """
        self.clear_bindings()
        temp = [ ['arrow_up', [window.move_up,()]],
            ['w', [window.move_up,()]],
            ['arrow_down', [window.move_down,()]],
            ['s', [window.move_down,()]],
            ['enter', [callback,(window.enter,)]],
            ['e', [callback,(window.enter,)]]]
        for set in temp:
            key = set[0]
            bind = set[1]
            self.add_binding(key,bind)

    def generate_map(self,w,h,set,layout='test'):
        """Generates new map using BasicGenerator, then generates basic entities.

        @type  w: number
        @param w: Width of map.
        @type  h: height
        @param h: Height of map.
        @type  set: bool
        @param set: If true, sets map as active.
        @type  layout: str
        @param layout: Filename of layout file to use.
        """
        gen = map.BlockGenerator(w,h)
        gen.set_layout(layout)
        m = gen.gen_map()
        ents = gen.entities
        self.generate_ents(m,ents)
        self.add_map(map=m,set=set)

    def generate_ents(self,map,list):
        """Populates map with entities, takes a list of (x, y, entity_lookup_name, chance),
            where chance is a float in [0,1]."""
        chances = { }
        for set in list:
            x, y, char, ent_string, chance, meta = set
            if char not in chances:
                chances[char] = random.random()
            if chances[char] < chance:
                ent = self.add_entity(x, y, ent_string)
                ent_obj = self.entity_manager[ent]
                for set in meta:
                    att, val = set
                    ent_obj.set_meta_attribute(att,val)
                ent_obj.update()

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
            self.fov_map = fov.FovMap(map.width,map.height)
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
        """Create a new window and return it.

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
        @rtype: X{graphics.Window} subclass
        @return: Created window.
        """
        win = self.win_man.add_window(layer,type,w,h,x,y)
        return win

    def clear_layer(self,layer):
        """Deletes all windows on a layer."""
        self.win_man.clear_layer(layer)

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

    def get_menu_window(self):
        """Returns current menu window or None."""
        if len(self.menu_stack) > 0:
            return self.win_man[self.menu_stack[-1][0]]

    def add_input_menu(self, label, callback, remove=True):
        """Adds an input menu to the stack and sets it as active.

        Callback gets called with a method that returns the string that was in the list.

        @type  label: string
        @param label: Text to display before input bar.
        """
        announce_layer = max(self.win_man.get_layers())+1
        win = self.add_window(announce_layer, graphics.InputWindow, self.win_man.width, 6, 0, self.win_man.height-6)
        win.set_label(label)
        win.set_length(self.win_man.width-6)
        self.input_bindings(win, callback, remove)
        self.menu_stack.append([win.id])

    def add_choice_menu(self, label, choices, callback, bgcol=None, fgcol=None, w=None, h=None, x=None, y=None):
        """Adds a single choice menu to the stack and sets it as active.

        ID of choice in choices is the ID that gets used in callback, starting from 0.

        @type  label: str
        @param label: String that contains entire labels for the menu, use \n for separating lines.
        @type  choices: tuple
        @param choices: List of valid choices in the menu.
        @type  callback: method
        @param callback: Function that gets called with a function as a parameter, that returns the ID
                        of the choice selected, when called.
        """
        if not bgcol:
            bgcol = self.bgcol
        if not fgcol:
            fgcol = self.fgcol
        if not w:
            w = 10
        if not h:
            h = 10
        if not x:
            x = self.win_man.width/2 - w/2
        if not y:
            y = self.win_man.height/2 - h/2
        announce_layer = max(self.win_man.get_layers())+1
        win = self.add_window(announce_layer, graphics.ChoiceWindow, w, h, x, y)
        win.bgcol = bgcol
        win.fgcol = fgcol
        win.set_label(label)
        win.set_choices(choices)
        self.menu_bindings(win,callback)
        self.menu_stack.append([win.id,callback])

    def add_switch_menu(self, switches, choices, meta, callback, bgcol=None, fgcol=None, w=None, h=None, x=None, y=None):
        """Adds a single switches menu to the stack and sets it as active.

        @type  switches: tuple
        @param switches: Tuple of choices to list.
        @type  choices: tuple
        @param choices: Tuple of starting choice states.
        @type  meta: tuple
        @param meta: Tuple of information attached to each switch.
        @type  callback: method
        @param callback: Function that gets called with a function as a parameter, that returns the ID
                        of the choice selected, when called.
        """
        if not bgcol:
            bgcol = self.bgcol
        if not fgcol:
            fgcol = self.fgcol
        if not w:
            w = 40
        if not h:
            h = 20
        if not x:
            x = self.win_man.width/2 - w/2
        if not y:
            y = self.win_man.height/2 - h/2
        announce_layer = max(self.win_man.get_layers())+1
        win = self.add_window(announce_layer, graphics.SwitchWindow, w, h, x, y)
        win.highlight = 1
        win.bgcol = bgcol
        win.fgcol = fgcol
        win.set_switches(switches,choices,meta)
        self.menu_bindings(win,callback)
        self.menu_stack.append([win.id,callback])

    def remove_menu(self):
        """Removes the last menu on the stack, and rebinds to the new active menu.

        If no menus remain, rebinds the game.
        """
        self.win_man.remove_window(self.menu_stack.pop()[0])
        if self.menu_stack:
            id,callback = self.menu_stack[-1]
            win = self.win_man[id]
            if win == graphics.ChoiceWindow:
                self.menu_bindings(win,callback)
            elif win == graphics.InputWindow:
                self.input_bindings(win,self._input_window_return_callback)
        else:
            self.default_bindings()

    def add_binding(self,key,bind):
        """Add a key binding.

        If key is a string of length 1, it's treated as a direct key binding. If longer than length 1, it's treated
        as a non-char binding. List of such bindings is in the keyboard module.
        """
        self.keyboard.add_binding(key,bind)
    
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

    def add_entity(self, x, y, type="entity", delay=10):
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
        for id in self.entity_manager:
            if self.entity_manager.get_name(id) == "player_spawn":
                x, y = self.entity_manager.get_abs_pos(id)
        pid = self.add_entity(x, y, 'player', delay)
        cam = self.add_entity(x, y, 'camera', None)
        self.entity_manager.set_parent(cam, pid)
        self.scheduler.set_dominant(self.entity_manager.get_sched(pid))
        self.player = pid
        self.camera = cam
        return pid

    def get_player_pos(self):
        if not self.player:
            return 0,0
        else:
            return self.get_ent_pos(self.player)

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
        if self.get_map() is not None:
            pos = self.get_ent_pos(id)
            if not pos:
                return False
            ex, ey = pos
            # check for wall
            if self.get_map().get_tile(x + ex, y + ey)[0]:
                can_move = False
            # check if we're blocking or not
            if self.entity_manager.get_attribute(id,'blocking'):
                # we are, let's check for entities on that spot, if they're blocking
                for ent in self.entity_manager[(x+ex, y+ey)]:
                    if self.entity_manager.get_attribute(ent,'blocking'):
                        can_move = False
            return can_move
        else:
            return False

    def player_pickup(self):
        """Attempt to have the player pick up everything on the tile he's on.

        Creates a switch menu listing everything on the tile.
        """
        pl = self.player
        x, y = self.get_ent_pos(pl)
        ents = self.entity_manager[(x,y)]
        opts, switches, meta = [], [], []
        valid_ents = [ ]
        for ent in ents:
            if ent is not pl and self.entity_manager[ent].listed:
                valid_ents += [ent]
        if len(valid_ents) > 1:
            for ent in valid_ents:
                if ent is not pl:
                    opts.append(self.entity_manager[ent].get_name())
                    switches.append(False)
                    meta.append(ent)
            opts, switches, meta = tuple(opts), tuple(switches), tuple(meta)
            self.add_switch_menu(opts, switches, meta, self._pickup_window_callback)
        elif len(valid_ents) == 1:
            self.entity_manager.ent_lift(self.entity_manager[pl].inventory, valid_ents[0])

    def _inv_window_recurse(self,id,parents=None,names=None,meta=None,cur_id=1,parent_id=0):
        """Internal recursion method for inventory listing with default node window."""
        if not names: names = {}
        if not parents: parents = {}
        if not meta: meta = {}
        for child in self.entity_manager[id]:
            child_ent = self.entity_manager[child]
            if child_ent.listed:
                orig_id = cur_id
                names[cur_id] = child_ent.name
                parents[cur_id] = parent_id
                meta[cur_id] = (child,child_ent.get_attribute('usable'))
                cur_id += 1
                parents, names, meta, cur_id = self._inv_window_recurse(child,parents,names,meta,cur_id,orig_id)
        return parents, names, meta, cur_id

    def update_inv_window(self):
        """Default implementation of inventory window updating.

        Subclass and replace to use a different format or a different window type.
        """
        if self.inv_win is None:
            return
        player = self.player
        if player is None:
            return
        names = {0:self.entity_manager.get_name(player)}
        parents = {0:None}
        meta = {0:(player,False)}
        parents, names, meta, cur_id = self._inv_window_recurse(player,parents,names,meta)
        self.inv_win.set_nodes(parents,names,meta)

    def update_game_window(self, fov_radius=10):
        """Default implementation of graphics updating, updates map and entities.

        Subclass and replace to use a different format.
        """

        if self.camera:
            camera_x, camera_y = self.entity_manager.get_abs_pos(self.camera)
            map = self.get_map()
            win = self.game_win
            center_x, center_y = win.width/2, win.height/2
            offset_x, offset_y = camera_x - center_x, camera_y - center_y

            # set up FOV map and compute FOV
            if self.fov_map:
                self.fov_map.clear_light()
                fov.fieldOfView(camera_x, camera_y, map.width, map.height, fov_radius, self.fov_map.set_lit, map.get_blocking)

            # make a list of the tiles to draw
            # tiles of the form [x, y, fgcol, string, bgcol, set_background]
            bg_tiles = [ ]
            ent_tiles = [ ]

            for i in range(win.width):
                for j in range(win.height):
                    x, y = i + offset_x, j + offset_y

                    lit = False
                    explored = False
                    if self.fov_map:
                        lit = self.fov_map.get_lit(x, y)
                        explored = self.fov_map.get_explored(x, y)
                    blocks = map.get_blocking(x, y)

                    if lit:
                        if not blocks:
                            bg_tiles.append([i, j, self.floor_col, 'floor', None, 1])
                        else:
                            bg_tiles.append([i, j, self.wall_col, 'wall', None, 1])
                    else:
                        if not blocks and explored:
                            bg_tiles.append([i, j, self.floor_col, 'dark_floor', None, 1])
                        else:
                            bg_tiles.append([i, j, self.wall_col, 'dark_wall', None, 1])

                    ents = self.entity_manager[(x, y)]
                    for ent in ents:
                        if lit and self.entity_manager.get_attribute(ent, 'visible'):
                            bg = 'floor'
                            if blocks:
                                bg = 'wall'
                            ent_tiles.append([i, j, bg, self.entity_manager[ent].char, None, 1])
            win.update_layer(0,bg_tiles)
            win.update_layer(1,ent_tiles)


    def update(self):
        """Update function, called every update.

        Subclass and replace to add code to run every working update, or drawing calls.
        """

        if self.time_passing:
            self.scheduler.tick()
        self.time_passing = False
        self.update_game_window()
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

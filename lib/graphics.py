import data.libtcodpy as libtcod

#    Window
#    |
#    +-LayeredGameWindow
#    |
#    +-MessageWindow
#       |
#       +-ChoiceWindow
#       |
#       +-InputWindow
#       |
#       +-NodeWindow


def convert(color):
    """Convert (r, g, b) color to libtcod.Color.

    Has to be replaced to change graphical back-end library.

    @type  color: tuple
    @param color: (r,g,b) formatted tuple describing a colour.
    @rtype: libtcod.Color
    @return: Converted library-specific color.
    """
    if not isinstance(color,libtcod.Color):
        color = libtcod.Color(*color)
    return color

class WindowManager(object):
    """Contains all windows and handles positioning, drawing and layering.

    Windows are referred to by ID.
    Window position is in I{positions}, object in I{window_list}, layer in I{layers}
    and visibility flag in I{visibilities}.
    """

    def __init__(self,w,h,name,font='data/font.png'):
        """Initialisation method.

        @type  w: number
        @param w: Main window width.
        @type  h: number
        @param h: Main window height.
        @type  name: string
        @param name: Main window title.
        @type  font: string
        @param font: Path to font file.
        """
        self.width = w
        self.height = h
        self.name = name
        self.font = font
        self.specific_init()
        self.current_id = 0
        self.window_list = { }
        self.positions = { }
        self.layers = { }
        self.visibilities = { }

    def specific_init(self):
        """Library-specific initialisation.

        Subclass and replace to change graphical backend.
        """
        libtcod.console_set_custom_font(self.font,
                libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
        libtcod.console_init_root(self.width, self.height, self.name)

    def add_window(self, layer, type, w, h, x, y):
        """Adds a new window.

        Higher layers are drawn last, thus show up on top.

        @type  layer: number
        @param layer: Layer to add the window to.
        @type  type: subclass of L{Window}.
        @param type: Type of new window.
        @type  w: number
        @param w: Width of new window.
        @type  h: number
        @param h: Height of new window.
        @type  x: number
        @param x: X coordinate of new window's top-left corner.
        @type  y: number
        @param y: Y coordinate of new window's top-left corner.
        @rtype:  number
        @return: Created window's ID.
        """
        win = type(w,h)
        id = self.current_id
        self.window_list[id] = win
        self.positions[id] = (x,y)
        self.layers[id] = layer
        self.visibilities[id] = 1
        self.current_id += 1
        return id

    def get_window(self, id):
        """Looks up and returns a window object by ID.

        @type  id: number
        @param id: Window ID.
        @rtype:  instance of L{Window} subclass.
        @return: Window object.
        """
        return self.window_list[id]

    def get_visible(self, id):
        """Returns a window's visibility flag.

        @type  id: number
        @param id: Window ID.
        @rtype:  bool
        @return: Window's visibility flag.
        """
        return self.visibilities[id]

    def hide_window(self,id):
        """Set a window's visibility flag to I{False}.

        @type  id: number
        @param id: Window ID.
        """
        self.visibilities[id] = False

    def show_window(self,id):
        """Set a window's visibility flag to I{True}.

        @type  id: number
        @param id: Window ID.
        """
        self.visibilities[id] = True

    def clear_layer(self,layer):
        """Clear a layer of windows.

        @type  layer: number
        @param layer: ID of layer to clear.
        """
        for id in self.layers.iterkeys():
            if self.layers[id] == layer:
                self.window_list[id].clear()
                del self.window_list[id]
                del self.positions[id]
                del self.layers[id]
                del self.visibilities[id]
    
    def remove_window(self,id):
        """Remove a window.

        @type  id: number
        @param id: Window ID.
        """
        if id in self.window_list:
            del self.window_list[id]
            del self.positions[id]
            del self.layers[id]
            del self.visibilities[id]

    def specific_flush(self):
        """Libtcod-specific flushing of console."""
        libtcod.console_flush()

    def specific_draw_window(self, id):
        """Libtcod-specific drawing.

        @type  id: number
        @param id: Window ID.
        """
        x, y = self.positions[id]
        win = self.window_list[id]
        libtcod.console_blit(win.con, 0, 0, win.width, win.height, 0, x, y)

    def draw_all(self):
        """Draw all the layers, in order.

        Lower layers are drawn first, so higher layers can cover them up.
        """
        l = list(self.layers.itervalues())
        l = list(set(l)) #remove duplicates and sort.
        l.sort()
        for layer in l:
            for id in self.layers:
                if self.layers[id] == layer:
                    self.specific_draw_window(id)
        self.specific_flush()


class Window(object):
    """Basic window object with basic drawing methods.

    It takes care of drawing to its own off-screen console, the window manager handles blitting that to the main
    console.
    """
    
    def __init__(self,w,h):
        """Initialisation method.

        @type  w: number
        @param w: Width of window.
        @type  h: number
        @param h: Height of window.
        """
        self.width = w
        self.height = h
        self.bgcol = (255,0,0)
        self.fgcol = (255,255,255)
        self.border_tile = None
        self.specific_init()

    def specific_init(self):
        """Library-specific console initialisation."""
        self.con = libtcod.console_new(self.width,self.height)

    def specific_draw_char(self,x,y,char,bgcol,fgcol,bgset):
        """Library-specific drawing a character at a position with a specific color.

        @type  x: number
        @param x: X coordinate.
        @type  y: number
        @param y: Y coordinate.
        @type  char: char
        @param char: Character to draw.
        @type  bgcol: libtcod.Color
        @param bgcol: libtcod-specific color to draw background of character.
        @type  fgcol: libtcod.Color
        @param fgcol: libtcod-specific color to draw character foreground in.
        @type  bgset: bool
        @param bgset: If I{True}, fills background in, else, only the character itself is drawn.
        """
        libtcod.console_set_background_color(self.con,bgcol)
        libtcod.console_set_foreground_color(self.con,fgcol)
        libtcod.console_put_char(self.con, x, y, char, bgset)

    def specific_print_line_rect(self,bgcol,fgcol,x,y,w,h,msg):
        """Library-specific drawing a string inside a filled rectangle.

        @type  bgcol: libtcod.Color
        @param bgcol: Background libtcod-specific color to draw the rectangle.
        @type  fgcol: libtcod.Color
        @param fgcol: Foreground libtcod-specific color to draw the text in.
        @type  x: number
        @param x: X coordinate of top-left corner of rectangle.
        @type  y: number
        @param y: Y coordinate of top-left corner of rectangle.
        @type  w: number
        @param w: Width of rectangle.
        @type  h: number
        @param h: Height of rectangle.
        @type  msg: string
        @param msg: String to draw inside the rectangle.
        """
        libtcod.console_set_background_color(self.con,bgcol)
        libtcod.console_set_foreground_color(self.con,fgcol)
        libtcod.console_print_left_rect(self.con,x,y,w,h,1,msg)

    def specific_get_line_height(self,x,y,w,h,msg):
        """Library-specific predicting height of a string inside a rect without drawing.

        Returns the height of the string wrapped around into the rectangle.

        @type  x: number
        @param x: X coordinate of top-left corner of rectangle.
        @type  y: number
        @param y: Y coordinate of top-left corner of rectangle.
        @type  w: number
        @param w: Width of rectangle.
        @type  h: number
        @param h: Height of rectangle.
        @type  msg: string
        @param msg: String to fit inside the rectangle.
        @rtype: number
        @return: Number of lines the string would end up being..
        """
        return libtcod.console_height_left_rect(self.con,x,y,w,h,msg)

    def specific_console_clear(self,bgcol,fgcol):
        """Library-specific clearing of console to a color.

        @type  bgcol: libtcod.Color
        @param bgcol: Background libtcod-specific color to clear to.
        @type  fgcol: libtcod.Color
        @param fgcol: Foreground libtcod-specific color to clear to.
        """
        libtcod.console_set_background_color(self.con,bgcol)
        libtcod.console_set_foreground_color(self.con,fgcol)
        libtcod.console_clear(self.con)

    def set_border(self,tile):
        """Set the border type, (bgcol, char, fgcol, bgset) or None for no border.

        Draws the border immediately afterwards.

        @type  tile: tuple
        @param tile: Tuple of the form (bgcol, char, fgcol, bgset) that describes the window's border tile.
        """
        self.border_tile = tile
        self.restore_border()

    def restore_border(self):
        """Restore border, automatically called after clearing or border draw_tiles.

        Does nothing if I{border_tile} is None.
        """
        if self.border_tile is not None:
            tiles = [ ]
            for i in range(self.width):
                tiles += [[i,0]+self.border_tile]
                tiles += [[i,self.height-1]+self.border_tile]
            for i in range(self.height):
                tiles += [[0,i]+self.border_tile]
                tiles += [[self.width-1,i]+self.border_tile]
            self.draw_tiles(tiles)

    def draw_tiles(self,tiles):
        """Draw tiles onto the window.

        Does not clear window.

        @type  tiles: list
        @param tiles: List of tuples of the form (x, y, bgcol, char, fgcol, bgset).
        """
        for tile in tiles:
            x, y, bgcol, char, fgcol, bgset = tile
            if 0 <= x < self.width:
                if 0 <= y < self.height:
                    bgcol = convert(bgcol)
                    fgcol = convert(fgcol)
                    self.specific_draw_char(x,y,char,bgcol,fgcol,bgset)

    def draw_messages(self,msgs):
        """Draw messages onto the window.

        Does not clear window.

        @type  msgs: list
        @param msgs: List of tuples of the form (x, y, msg).
        """
        for msg in msgs:
            x, y, line = msg
            self.specific_print_line_rect(convert(self.bgcol), convert(self.fgcol), x, y, self.width-3, 0, line)

    def clear(self,bgcol = None, fgcol = None):
        """Clear window.

        Defaults to clearing to the instance variables L{bgcol} and L{fgcol}.
        Restores the border afterwards.

        @type  bgcol: tuple or libtcod.Color or None
        @param bgcol: Background color to clear the window to.
        @type  fgcol: tuple or libtcod.Color or None
        @param fgcol: Foreground color to clear the window to.
        """
        if bgcol is None:
            bgcol = self.bgcol
        if fgcol is None:
            fgcol = self.fgcol
        bgcol = convert(bgcol)
        fgcol = convert(fgcol)
        self.specific_console_clear(bgcol,fgcol)
        self.restore_border()


class LayeredGameWindow(Window):
    """Main game window, supports layers."""
    
    def __init__(self,w,h):
        """Initialisation method."""
        super(LayeredGameWindow,self).__init__(w,h)
        self.layers = { }
    
    def update_layer(self,layer,tiles):
        """Update a layer with a list of (x, y, bgcol, char, fgcol, bgset)."""
        map = [ ]
        for tile in tiles:
            map += [tile]
        self.layers[layer] = map
        self.draw_layers()

    def draw_layers(self):
        """Draw all layers, then restore border."""
        self.clear()
        s = list(self.layers.iterkeys())
        s.sort()
        for layer in s:
            tiles = self.layers[layer]
            self.draw_tiles(tiles)
        self.restore_border()


class MessageWindow(Window):
    """Main messaging window type.

    Scrolls down when too many messages have been added, but dumps old messages.
    """
    
    def __init__(self,w,h):
        """Initialisation method.

        @type  w: number
        @param w: Width of window.
        @type  h: number
        @param h: Height of window.
        """
        super(MessageWindow,self).__init__(w,h)
        self.messages = [ ]
        
    def get_current_height(self):
        """Returns current height of messages in window.

        @rtype: number
        @return: Current height of messages in queue.
        """
        y = 2  # padding for border
        for msg in self.messages:
            y += self.specific_get_line_height(2, y, self.width-4, 0, msg[2])
        return y

    def add_messages(self,msgs):
        """Add messages to queue.

        @type  msgs: list
        @param msgs: List of strings to add to the queue.
        """
        for msg in msgs:
            y = self.get_current_height()
            h = self.specific_get_line_height(2, y, self.width-4, 0, msg)
            while y + h > self.height - 2:
                del self.messages[0]
                y = 2
                for tmp_msg in self.messages:
                    tmp_msg[1] = y
                    y += self.specific_get_line_height(2, y, self.width-4, 0, tmp_msg[2])
                y = self.get_current_height()
            self.messages.append([2, y, msg])
        self.clear()
        self.draw_messages(self.messages)


class ChoiceWindow(MessageWindow):
    """Main menu type, single choice from multiple ones."""
    
    def __init__(self,w,h):
        """Initialisation method."""
        super(ChoiceWindow,self).__init__(w, h)
        self.labels = [ ]
        self.choices = [ ]
        self.highlight = None
    
    def set_label(self,labels):
        """Set choice displayed label."""
        self.labels = labels
    
    def set_choices(self,choices):
        """Set available choices."""
        self.choices = choices
        if self.highlight is None or self.highlight>=len(self.choices):
            self.highlight = 0
        self.tick()
        
    def add_choice(self,choice):
        """Add new choice."""
        self.choices.append(choice)
        if self.highlight is None:
            self.highlight = 0
        self.tick()
    
    def set_highlight(self,id):
        """Set currently highlighted choice."""
        if len(self.choices) > id >= 0:
            self.highlight = id
        self.tick()
    
    def move_up(self):
        """Move currently selected choice up."""
        self.set_highlight(self.highlight-1)
    
    def move_down(self):
        """Move currently selected choice down."""
        self.set_highlight(self.highlight+1)
    
    def enter(self):
        """Returns currently selected choice."""
        return self.highlight

    def tick(self):
        """Internally-called updater method."""
        self.messages = [ ]
        self.draw_messages(self.messages)
        msgs = [ ]
        msgs += self.labels
        msgs += [' ']
        for id in range(len(self.choices)):
            choice = self.choices[id]
            if id != self.highlight:
                line = '  ' + str(id) + '.  ' + choice
            else:
                line = '  X.  ' + choice
            msgs.append(line)
        self.add_messages(msgs)


class InputWindow(MessageWindow):
    """One line input window.

    Used to obtain one line of text from the player.
    """
    
    def __init__(self,w,h):
        """Initialisation method.

        @type  w: number
        @param w: Width of window.
        @type  h: number
        @param h: Height of window.
        """
        super(InputWindow,self).__init__(w, h)
        self.label = ""
        self.length = 5
        self.input = ""
    
    def set_label(self,label):
        """Sets label to display before text.

        @type  label: string
        @param label: Text to display before text.
        """
        self.label = label
        self.update()
    
    def set_length(self,length):
        """Sets max length of input.

        @type  length: number
        @param length: Maximum number of characters that can be input.
        """
        self.length = length
    
    def add_char(self,char):
        """Adds character to input.

        Does nothing if maximum length is already reached.

        @type  char: char
        @param char: Character to add.
        """
        if len(self.input)<self.length:
            self.input += char
        self.update()
    
    def remove_char(self,id):
        """Removes character from input.

        @type  id: number
        @param id: Index of character to remove.
        """
        self.input = self.input[:id] + self.input[id+1:]
        self.update()
    
    def backspace(self):
        """Convenience method to remove last character."""
        self.remove_char(len(self.input)-1)
    
    def enter(self):
        """Returns current input and clears input.

        @rtype: string
        @return: Currently input string.
        """
        inp = self.input
        self.input = ""
        self.update()
        return inp
    
    def update(self):
        """Internally-called updater method."""
        self.clear()
        msgs = [self.label, ">>> " + self.input, '']
        self.messages = []
        self.add_messages(msgs)
        self.restore_border()

class NodeWindow(MessageWindow):
    """Node-list window, like a tree view."""

    def __init__(self,w,h):
        """Initialisation method."""
        super(NodeWindow,self).__init__(w,h)
        self.node_list = { }
        self.node_parents = { }
        self.add_node(0,None,"root")

    def set_nodes(self, parents, texts):
        self.node_list = { }
        self.node_parents = { }
        for id in texts.keys():
            self.add_node(id, parents[id], texts[id])
        self.tick()

    def add_node(self, id, parent, text):
        if id in self.node_list:
            del self.node_list[id]
            del self.node_parents[id]
        if parent not in self.node_list and parent is not None:
            parent = 0
        self.node_list[id] = text
        self.node_parents[id] = parent

    def get_node_text(self, id):
        if id not in self.node_list:
            return "Error"
        return self.node_list[id]

    def rename_node(self, id, text):
        if id not in self.node_list:
            return  #TODO: error handling.
        self.node_list[id] = text

    def get_children(self, id):
        ret = [ ]
        for node in self.node_parents.keys():
            if self.node_parents[node] == id:
                ret.append(node)
        return ret

    def _recurse_children(self, id=0, ret=None, depth=0):
        """Internal recursion function that goes through all the children of root and returns a list of them."""
        if not ret: ret = []
        for child in self.get_children(id):
            ret.append("  "*depth + "|-<" +self.get_node_text(child)+">")
            ret = self._recurse_children(child, ret, depth+1)
        return ret

    def tick(self):
        self.clear()
        msgs = ["<" + self.get_node_text(0) + ">"]
        self._depth = 0
        msgs += self._recurse_children()
        self.messages = [ ]
        self.add_messages(msgs)
        self.restore_border()


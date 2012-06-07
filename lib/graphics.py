import struct
import data.libtctrout as libtctrout

#    Window
#    |
#    +-LayeredGameWindow
#    |
#    +-MessageWindow
#       |
#       +-ChoiceWindow
#       |
#       +-InputWindow
#       | |
#       | +-ConsoleWindow
#       |
#       +-NodeWindow
#          +
#          |
#          +-InventoryWindow


def convert(color):
    """Convert hex to tuple.

    Has to be replaced to change graphical back-end library.
    """
    if isinstance(color, str):
        color = tuple(struct.unpack('BBB', color.decode('hex')))
    return color

class WindowManager(object):
    """Contains all windows and handles positioning, drawing and layering.

    Windows are referred to by ID.
    Window position is in I{positions}, object in I{window_list}, layer in I{layers}
    and visibility flag in I{visibilities}.
    """

    def __init__(self,w,h,name,font='data/main.font'):
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

    def __len__(self):
        return len(self.window_list)

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.window_list[item]
        else:
            return NotImplemented

    def __iter__(self):
        return self.window_list.itervalues()

    def __contains__(self, item):
        return item in self.window_list

    def specific_init(self):
        """Library-specific initialisation.

        Subclass and replace to change graphical backend.
        """
        self.root = libtctrout.RootWindow(self.name, self.width,
                        self.height, self.font)
        self.root.clear()

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
        @return: Created window.
        """
        win = type(w,h,self)
        id = self.current_id
        self.window_list[id] = win
        self.window_list[id].id = id
        self.positions[id] = (x,y)
        self.layers[id] = layer
        self.visibilities[id] = 1
        self.current_id += 1
        return win

    def get_layers(self):
        """Returns a list of the layers in the manager."""
        return self.layers.values()

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
                self.remove_window(id)
    
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
        self.root.update()
        self.root.tick()

    def specific_draw_window(self, id):
        """Libtcod-specific drawing.

        @type  id: number
        @param id: Window ID.
        """
        x, y = self.positions[id]
        win = self.window_list[id]
        self.root.blit(win.con, 0, 0, win.width, win.height, x, y)

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
                    self[id].update()
                    self.specific_draw_window(id)
        self.specific_flush()


class Window(object):
    """Basic window object with basic drawing methods.

    It takes care of drawing to its own off-screen console, the window manager handles blitting that to the main
    console.
    """
    
    def __init__(self,w,h,parent):
        """Initialisation method.

        @type  w: number
        @param w: Width of window.
        @type  h: number
        @param h: Height of window.
        """
        self.width = w
        self.height = h
        self.parent = parent
        self.bgcol = (255,0,0)
        self.fgcol = (255,0,0)
        self.border_tile = None
        self.specific_init()

    def specific_init(self):
        """Library-specific console initialisation."""
        self.con = self.parent.root.new_window(self.width,self.height)

    def specific_set_bg_col(self,x,y,bgcol):
        """Library-specific setting a position's background color.

        @type  x: number
        @param x: X coordinate.
        @type  y: number
        @param y: Y coordinate.
        @type  bgcol: libtcod.Color
        @param bgcol: Color to set the cell's background color to.
        """
        self.con.set_col(x, y, bg=bgcol)

    def specific_set_fg_col(self,x,y,bgcol):
        """Library-specific setting a position's foreground color.

        @type  x: number
        @param x: X coordinate.
        @type  y: number
        @param y: Y coordinate.
        @type  bgcol: libtcod.Color
        @param bgcol: Color to set the cell's foreground color to.
        """
        self.con.set_col(x, y, fg=bgcol)

    def specific_get_bg_col(self,x,y):
        """Library-specific getting a position's background color.

        @type  x: number
        @param x: X coordinate.
        @type  y: number
        @param y: Y coordinate.
        """
        return self.con.get_col(x,y)[0]

    def specific_get_fg_col(self,x,y):
        """Library-specific getting a position's foreground color.

        @type  x: number
        @param x: X coordinate.
        @type  y: number
        @param y: Y coordinate.
        """
        return self.con.get_col(x,y)[1]

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
        if not bgset:
            bgcol = None
        self.con.put_char(x, y, char, bg=bgcol, fg=fgcol)

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
        self.con.put_string(x,y,w,h,msg,bg=bgcol,fg=fgcol)

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
        return self.con.test_string_height(x,y,w,h,msg)

    def specific_console_clear(self,bgcol,fgcol):
        """Library-specific clearing of console to a color.

        @type  bgcol: libtcod.Color
        @param bgcol: Background libtcod-specific color to clear to.
        @type  fgcol: libtcod.Color
        @param fgcol: Foreground libtcod-specific color to clear to.
        """
        self.con.clear(bg=bgcol,fg=fgcol)

    def specific_h_line(self, x, y, w):
        """Library-specific drawing of a horizontal line onto the console."""
        bgcol = convert(self.bgcol)
        fgcol = convert(self.fgcol)
        self.con.put_h_line(x,y,w,bg=bgcol,fg=fgcol)

    def specific_v_line(self, x, y, h):
        """Library-specific drawing of a vertical line onto the console."""
        bgcol = convert(self.bgcol)
        fgcol = convert(self.fgcol)
        self.con.put_v_line(x,y,h,bg=bgcol,fg=fgcol)

    def specific_frame(self, x, y, w, h):
        """Library-specific drawing of a frame onto the console."""
        bgcol = convert(self.bgcol)
        fgcol = convert(self.fgcol)
        self.con.put_frame(x,y,w,h,bg=bgcol,fg=fgcol)

    def reverse_at(self,x,y):
        """Reverse the colors in a cell.
        
        @type  x: number
        @param x: X coordinate.
        @type  y: number
        @param y: Y coordinate.
        """
        colb = self.specific_get_bg_col(x,y)
        colf = self.specific_get_fg_col(x,y)
        self.specific_set_bg_col(x,y,colf)
        self.specific_set_fg_col(x,y,colb)

    def reverse_rect(self,x,y,w,h):
        for i in range(x, x+w):
            for j in range(y, y+h):
                self.reverse_at(i,j)

    def reverse_line(self,y):
        self.reverse_rect(2,y,self.width-4,1)

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
        else:
            self.specific_frame(0, 0, self.width, self.height)

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
                    self.specific_draw_char(x,y,char,bgcol,fgcol,bgset)

    def draw_messages(self,msgs):
        """Draw messages onto the window.

        Does not clear window.

        @type  msgs: list
        @param msgs: List of tuples of the form (x, y, msg).
        """
        for msg in msgs:
            x, y, line = msg
            self.specific_print_line_rect(convert(self.bgcol), convert(self.fgcol), x, y, self.width-4, 0, line)

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

    def update(self):
        """Internally-called updater method."""
        pass


class LayeredGameWindow(Window):
    """Main game window, supports layers."""
    
    def __init__(self,w,h,parent):
        """Initialisation method."""
        super(LayeredGameWindow,self).__init__(w,h,parent)
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
    
    def __init__(self,w,h,parent):
        """Initialisation method.

        @type  w: number
        @param w: Width of window.
        @type  h: number
        @param h: Height of window.
        """
        super(MessageWindow,self).__init__(w,h,parent)
        self.messages = [ ]

    def get_msg_y(self,id):
        """Returns y coordinate of message."""
        return self.messages[id][1]
        
    def get_current_height(self):
        """Returns current height of messages in window.

        @rtype: number
        @return: Current height of messages in queue.
        """
        y = 2  # padding for border
        for msg in self.messages:
            y += self.get_msg_height(y, msg[2])
        return y

    def get_msg_height(self, y, msg):
        """Convenience method."""
        return self.specific_get_line_height(2, y, self.width-4, 0, msg)

    def add_messages(self,msgs):
        """Add messages to queue.

        @type  msgs: list
        @param msgs: List of strings to add to the queue.
        """
        for msg in msgs:
            y = self.get_current_height()
            h = self.get_msg_height(y, msg)
            while y + h > self.height - 2:
                del self.messages[0]
                y = 2
                for tmp_msg in self.messages:
                    tmp_msg[1] = y
                    y += self.get_msg_height(y, tmp_msg[2])
                y = self.get_current_height()
            self.messages.append([2, y, msg])
        self.clear()
        self.draw_messages(self.messages)

    def update(self):
        super(MessageWindow,self).update()
        self.clear()
        self.draw_messages(self.messages)


class ChoiceWindow(MessageWindow):
    """Main menu type, single choice from multiple ones."""
    
    def __init__(self,w,h,parent):
        """Initialisation method."""
        super(ChoiceWindow,self).__init__(w, h,parent)
        self.labels = [ ]
        self.choices = [ ]
        self.highlight = None
    
    def set_label(self,label):
        """Set choice displayed label."""
        self.labels = [ ]
        for line in label.split("\n"):
            self.labels.append(line)
    
    def set_choices(self,choices):
        """Set available choices."""
        self.choices = choices
        if self.highlight is None or self.highlight>=len(self.choices):
            self.highlight = 0
        self.update()
        
    def add_choice(self,choice):
        """Add new choice."""
        self.choices.append(choice)
        if self.highlight is None:
            self.highlight = 0
        self.update()
    
    def set_highlight(self,id):
        """Set currently highlighted choice."""
        if len(self.choices) > id >= 0:
            self.highlight = id
        self.update()
    
    def move_up(self):
        """Move currently selected choice up."""
        self.set_highlight(self.highlight-1)
    
    def move_down(self):
        """Move currently selected choice down."""
        self.set_highlight(self.highlight+1)
    
    def enter(self):
        """Returns currently selected choice."""
        return self.highlight

    def update(self):
        """Internally-called updater method."""
        self.messages = [ ]
        self.draw_messages(self.messages)
        msgs = [ ]
        msgs += self.labels
        msgs += [' ']
        for id in range(len(self.choices)):
            choice = self.choices[id]
            line = "  " +  choice
            msgs.append(line)
        self.add_messages(msgs)
        y = self.get_msg_y(self.highlight+len(self.labels)+1)
        h = self.get_msg_height(0,self.choices[self.highlight]+'  ' + str(self.highlight) +'.  ')
        for i in range(h):
            self.reverse_line(y+i)


class InputWindow(MessageWindow):
    """One line input window.

    Used to obtain one line of text from the player.
    """
    
    def __init__(self,w,h,parent):
        """Initialisation method.

        @type  w: number
        @param w: Width of window.
        @type  h: number
        @param h: Height of window.
        """
        super(InputWindow,self).__init__(w, h,parent)
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
        msgs = [self.label + self.input]
        self.messages = []
        self.add_messages(msgs)
        self.restore_border()


class ConsoleWindow(InputWindow):
    """Console-type window, basically an input window with a history."""

    def __init__(self,w,h,parent):
        super(ConsoleWindow,self).__init__(w,h,parent)
        self.history = [ ]

    def enter(self):
        """Returns current input, adds command to history and clears input."""
        if self.input:
            self.history.append(self.input)
        return super(ConsoleWindow,self).enter()

    def update(self):
        self.clear()
        self.messages = []
        self.add_messages([" "])
        if self.history:
            self.history.reverse()
            self.add_messages(self.history[:self.height-6])
            self.history.reverse()
        msgs = [(1,1,self.label + self.input)]
        self.draw_messages(msgs)
        self.reverse_rect(1,1,self.width-2,1)
        self.specific_h_line(1,2,self.width-2)
        self.restore_border()

class NodeWindow(MessageWindow):
    """Node-list window, like a tree view."""

    def __init__(self,w,h,parent):
        """Initialisation method."""
        super(NodeWindow,self).__init__(w,h,parent)
        self.node_list = { }
        self.node_parents = { }
        self.node_meta = { }
        self.add_node(0,None,"root",(0,))
        self.highlight = None

    def set_nodes(self, parents, texts, meta=None):
        if meta is None:
            meta = { }
        self.node_list = { }
        self.node_parents = { }
        self.node_meta = { }
        for id in texts.keys():
            if id not in meta:
                meta[id] = ()
            self.add_node(id, parents[id], texts[id], meta[id])
        self.update()

    def add_node(self, id, parent, text, meta=()):
        if id in self.node_list:
            del self.node_list[id]
            del self.node_parents[id]
            del self.node_meta[id]
        if parent not in self.node_list and parent is not None:
            parent = 0
        self.node_list[id] = text
        self.node_parents[id] = parent
        self.node_meta[id] = meta

    def get_node_meta(self, id):
        if id not in self.node_list:
            return
        return self.node_meta[id]

    def highlight_node_by_meta(self, meta):
        for id in range(len(self.node_meta)):
            node = self.node_meta[id]
            if node[0] == meta:
                self.activated_node = id
                break


    def get_node_text(self, id):
        if id not in self.node_list:
            return "Error"
        return self.node_list[id]

    def rename_node(self, id, text):
        if id not in self.node_list:
            return
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

    def update(self):
        self.clear()
        msgs = ["<" + self.get_node_text(0) + ">"]
        self._depth = 0
        msgs += self._recurse_children()
        self.messages = [ ]
        self.add_messages(msgs)
        self.restore_border()
        if self.highlight is not None:
            self.reverse_line(self.get_msg_y(self.highlight))

class InventoryWindow(NodeWindow):

    def __init__(self,w,h,parent):
        super(InventoryWindow,self).__init__(w,h,parent)
        self.activated_node = None

    def update(self):
        super(InventoryWindow,self).update()
        self.specific_h_line(1, self.height-3, self.width-2)
        msg = "Active: "
        if self.activated_node:
            msg += "<" + self.node_list[self.activated_node] + ">"
        self.draw_messages([(3, self.height-2, msg)])

class SwitchWindow(MessageWindow):

    def __init__(self,w,h,parent):
        super(SwitchWindow,self).__init__(w,h,parent)
        self.switches = [ ]
        self.choices = [ ]
        self.meta = [ ]
        self.highlight = 0

    def set_switches(self, switches, choices, meta):
        self.choices = list(choices)
        self.switches = list(switches)
        self.meta = list(meta)

    def move_up(self):
        if self.highlight:
            self.highlight -= 1
            if not self.highlight:
                self.highlight += 1

    def move_down(self):
        if self.highlight:
            self.highlight += 1
            if self.highlight > len(self.switches) + 1:
                self.highlight -= 1

    def enter(self):
        if self.highlight != len(self.switches) + 1:
            self.choices[self.highlight-1] = not self.choices[self.highlight-1]
            return None
        else:
            ret = (self.switches, self.choices, self.meta)
            self.highlight = 0
            return ret

    def update(self):
        self.clear()
        msgs = [ ]
        for id in range(len(self.switches)):
            msg = '  '
            msg += self.switches[id]
            msg += ' ' * (self.width - 16 - len(self.switches[id]))
            msg += '    ['
            if self.choices[id]:
                msg += 'X]'
            else:
                msg += ' ]'
            msgs.append(msg)
        while len(msgs) < self.height - 5:
            msgs.append(" ")
        msgs.append("< Close >")
        self.messages = [ ]
        self.add_messages(msgs)
        if self.highlight <= len(self.switches):
            self.reverse_line(self.highlight+1)
        else:
            self.reverse_line(self.height-3)
        self.restore_border()

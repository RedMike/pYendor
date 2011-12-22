import data.libtcodpy as libtcod

# Window
# |
# +-BorderedWindow
#    |
#    +-GameWindow
#    |  |
#    |  +-LayeredGameWindow
#    |
#    +-BorderedMessageWindow
#    |  |
#    |  +-ChoiceWindow
#    |  |
#    |  +-InputWindow
#    |  |
#    |  +-MultiChoiceWindow
#    |
#    +-StatusWindow
#


def convert(color):
    """Convert (r, g, b) color to libtcod.Color."""
    if not isinstance(color,libtcod.Color):
        color = libtcod.Color(*color)
    return color

class RootWindow(object):
    """Root window object that contains all other windows.

    Each window has an ID, layers and visibility are dicts.
    """

    def __init__(self,w,h,name,font='data/font.png'):
        """Initialisation method, name shows up as the title."""
        # TODO: font things.
        self.width = w
        self.height = h
        self.name = name
        self.font = font
        self.specific_init()
        self.current_id = 0
        self.window_list = { }
        self.positions = { }
        self.layers = { }
        self.visibility = { }

    def specific_init(self):
        """Library-specific initialisation; Overwrite for non-libtcod."""
        libtcod.console_set_custom_font(self.font,
                libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
        libtcod.console_init_root(self.width, self.height, self.name)
        # libtcod.console_credits()

    def add_window(self, layer, type, w, h, x, y):
        """Adds a new window, returns id."""
        win = type(w,h)
        self.window_list[self.current_id] = win
        self.positions[self.current_id] = (x,y)
        self.layers[self.current_id] = layer
        self.visibility[self.current_id] = 1
        self.current_id += 1
        return self.current_id-1

    def get_window(self, id):
        """Returns window object."""
        return self.window_list[id]

    def get_visible(self, id):
        """Returns a window's visibility flag."""
        return self.visibility[id]

    def hide_window(self,id):
        """Set a window's visibility flag to 0."""
        self.visibility[id] = 0

    def show_window(self,id):
        """Set a window's visibility flag to 1."""
        self.visibility[id] = 1

    def clear_layer(self,layer):
        for id in self.layers.iterkeys():
            if self.layers[id] == layer:
                self.window_list[id].clear()
                del self.window_list[id]
                del self.positions[id]
                del self.layers[id]
                del self.visibility[id]
    
    def remove_window(self,id):
        """Remove a window, by id."""
        if id in self.window_list:
            del self.window_list[id]
            del self.positions[id]
            del self.layers[id]
            del self.visibility[id]

    def draw_window(self, id):
        """Libtcod-specific drawing of window."""
        x, y = self.positions[id]
        win = self.window_list[id]
        libtcod.console_blit(win.con, 0, 0, win.width, win.height, 0, x, y)

    def draw_all(self):
        """Draw all the layers, in order, lowest to highest."""
        l = list(self.layers.itervalues())
        l.sort()
        for layer in l:
            for id in self.layers:
                if self.layers[id] == layer:
                    self.draw_window(id)
        libtcod.console_flush()

class Window(object):
    """Basic window from which any kind of window is derived from.

    It takes care of drawing to its own off-screen console, the root window does the rest.
    """
    
    def __init__(self,w,h):
        """Set the background color afterwards if needed."""
        self.width = w
        self.height = h
        self.bgcol = (255,0,0)
        self.fgcol = (255,255,255)
        self.specific_init()

    def specific_init(self):
        """Library-specific console initialisation."""
        self.con = libtcod.console_new(self.width,self.height)

    def draw_char(self,x,y,char,bgcol,fgcol,bgset):
        """Library-specific drawing a character at a position with a specific color."""
        libtcod.console_set_background_color(self.con,bgcol)
        libtcod.console_set_foreground_color(self.con,fgcol)
        libtcod.console_put_char(self.con, x, y, char, bgset)

    def print_line_rect(self,bgcol,fgcol,x,y,w,h,msg):
        """Library-specific drawing a string inside a rect."""
        libtcod.console_set_background_color(self.con,bgcol)
        libtcod.console_set_foreground_color(self.con,fgcol)
        libtcod.console_print_left_rect(self.con,x,y,w,h,1,msg)

    def get_line_height(self,x,y,w,h,msg):
        """Library-specific predicting height of a string inside a rect."""
        return libtcod.console_height_left_rect(self.con,x,y,w,h,msg)

    def console_clear(self,bgcol,fgcol):
        """Library-specific clearing of console to a color."""
        libtcod.console_set_background_color(self.con,bgcol)
        libtcod.console_set_foreground_color(self.con,fgcol)
        libtcod.console_clear(self.con)

    def update(self,tiles):
        """Update window with tiles of the form (x,y,bgcol,char,fgcol,bgset)."""
        for tile in tiles:
            x, y, bgcol, char, fgcol, bgset = tile
            if 0 <= x < self.width:
                if 0 <= y < self.height:
                    bgcol = convert(bgcol)
                    fgcol = convert(fgcol)
                    self.draw_char(x,y,char,bgcol,fgcol,bgset)

    def update_message(self,msgs):
        """Update window with a list of messages in format (x, y, msg)."""
        for msg in msgs:
            x, y, line = msg
            self.print_line_rect(convert(self.bgcol), convert(self.fgcol), x, y, self.width-3, 0, line)

    def clear(self,bgcol = None, fgcol = None):
        """Clear window to a color."""
        if bgcol is None:
            bgcol = self.bgcol
        if fgcol is None:
            fgcol = self.fgcol
        bgcol = convert(bgcol)
        fgcol = convert(fgcol)
        self.console_clear(bgcol,fgcol)


class BorderedWindow(Window):
    """Window with a set tile border."""

    def __init__(self,w,h):
        """Call setBorder after for the border to show up."""
        super(BorderedWindow,self).__init__(w,h)
        self.borderTile = None
    
    def set_border(self,tile):
        """Set the border type, (bgcol, char, fgcol, bgset) or None for no border."""
        self.borderTile = tile
        self.restore_border()
    
    def restore_border(self):
        """Restore border, automatically called after clearing."""
        if self.borderTile is not None:
            tiles = [ ]
            for i in range(self.width):
                tiles += [[i,0]+self.borderTile]
                tiles += [[i,self.height-1]+self.borderTile]
            for i in range(self.height):
                tiles += [[0,i]+self.borderTile]
                tiles += [[self.width-1,i]+self.borderTile]
            self.update(tiles)
    
    def clear(self,bgcol = None, fgcol = None):
        """Clear window to a color, then restore border."""
        super(BorderedWindow,self).clear(bgcol,fgcol)
        self.restore_border()


class LayeredGameWindow(BorderedWindow):
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
            self.update(tiles)
        self.restore_border()


class BorderedMessageWindow(BorderedWindow):
    """Main messaging window type."""
    
    def __init__(self,w,h):
        """Initialisation method."""
        super(BorderedMessageWindow,self).__init__(w,h)
        self.messages = [ ]
        
    def get_current_height(self):
        """Returns current height of messages in window."""
        y = 2  # padding for border
        for msg in self.messages:
            y += self.get_line_height(2, y, self.width-4, 0, msg[2])
        return y

    def add_messages(self,msgs):
        """Add messages, as a list."""
        for msg in msgs:
            y = self.get_current_height()
            h = self.get_line_height(2, y, self.width-4, 0, msg)
            while y + h > self.height - 2:
                del self.messages[0]
                y = 2
                for tmp_msg in self.messages:
                    tmp_msg[1] = y
                    y += self.get_line_height(2, y, self.width-4, 0, tmp_msg[2])
                y = self.get_current_height()
            self.messages.append([2, y, msg])
        self.clear()
        self.update_message(self.messages)


class ChoiceWindow(BorderedMessageWindow):
    """Main menu type, single choice from multiple ones."""
    
    def __init__(self,w,h):
        """Initialisation method."""
        super(ChoiceWindow,self).__init__(w, h)
        self.labels = [ ]
        self.choices = [ ]
        self.highlight = None
    
    def set_label(self,labels):
        """Set choice displayed labels."""
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
        self.update_message(self.messages)
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


class InputWindow(BorderedMessageWindow):
    """One line input window."""
    
    def __init__(self,w,h):
        """Initialisation method."""
        super(InputWindow,self).__init__(w, h)
        self.labels = []
        self.length = 5
        self.input = ""
    
    def setLabel(self,labels):
        """Set label before text input."""
        self.labels = labels
        self.tick()
    
    def setLength(self,length):
        """Set max length of input."""
        self.length = length
    
    def addChar(self,c):
        """Add character to input."""
        if len(self.input)<self.length:
            self.input += c
        self.tick()
    
    def removeChar(self,id):
        """Remove character from input."""
        self.input = self.input[:id] + self.input[id+1:]
        self.tick()
    
    def backspace(self):
        """Backspace method."""
        self.removeChar(len(self.input)-1)
    
    def enter(self):
        """Return current input."""
        inp = self.input
        self.input = ""
        self.tick()
        return inp
    
    def tick(self):
        """Internally-called updater method."""
        self.clear()
        msgs = []
        for label in self.labels:
            msgs.append(label)
        msgs.append([self.bgcol, '', (255,255,255), 1])
        msgs.append([(255,255,255), self.input, (80,80,80), 1])
        msgs.append([self.bgcol, '', (255,255,255), 1])
        self.update_message(msgs)
        self.restore_border()

class MultiChoiceWindow(BorderedMessageWindow):
    """Multi-choice window."""

    def __init__(self,w,h):
        """Initialisation method."""
        super(MultiChoiceWindow,self).__init__(w, h)
        self.labels = []
        self.choices = []
        self.chosen = []

    def setLabels(self,labels):
        """Set choice labels."""
        self.labels = labels

    def setChoices(self,choices):
        """Set choices."""
        self.choices = choices
        self.tick()

    def addChoice(self,choice):
        """Add new choice."""
        self.choices.append(choice)
        self.tick()

    def choose(self,choice):
        """Toggle choice."""
        if choice in self.chosen:
            self.chosen.remove(choice)
        else:
            self.chosen += [self.choices[choice][1]]

    def enter(self):
        """Return currently selected choices."""
        return self.chosen

    def tick(self):
        """Internally-called updater method."""
        self.clear()
        msgs = []
        for label in self.labels:
            msgs += [label]
        msgs += [[self.bgcol, '', (255,255,255), 1]]
        msgs += [[self.bgcol, '', (255,255,255), 1]]
        for id in range(len(self.choices)):
            choice = self.choices[id]
            line = ' '
            if id in self.chosen:
                line += '+'
            else:
                line += '-'
            line += ' ' + str(id) + ')  ' + choice[0]
            msgs += [[self.bgcol, line, (255,255,255), 1]]
            msgs += [[self.bgcol, '', (255,255,255), 1]]
        self.update_message(msgs)

class StatusWindow(BorderedWindow):
    """Variable bar-number bar window."""

    def __init__(self,w,h):
        """Initialisation method."""
        super(StatusWindow,self).__init__(w,h)
        self.bars = []

    # [current, maximum, (bgcol,fgcol)]
    def addBar(self,label,cur,max,col):
        """Add new bar in format [current, max, (bgcol, fgcol)], returns id."""
        self.bars += [[label,cur,max,col]]
        return len(self.bars)-1

    def updateBar(self,id,label,cur,max,col):
        """Update bar."""
        self.bars[id] = [label,cur,max,col]
        self.tick()

    def tick(self):
        """Internally-called updater method."""
        self.clear()
        y = 2
        #bar = [label,current,maximum,(bgcol,fgcol)]
        for bar in self.bars:
            label,cur,max,col = bar
            bcol = col[0]
            fcol = col[1]
            l = len(label)
            maxw = self.width-4-l

            r = int(float(cur)/max*maxw)

            # tile = (x, y, bgcol, char, fgcol, bgset)
            tiles = []
            for x in range(l):
                bgcol = (0,0,0)
                char = label[x]
                fgcol = (255,255,255)
                bgset = 1
                tiles += [[x+2,y,bgcol,char,fgcol,bgset]]
            for x in range(r):
                bgcol = bcol
                char = "="
                fgcol = fcol
                bgset = 1
                tiles += [[x+2+l,y,bgcol,char,fgcol,bgset]]
            if r != self.width-4-l:
                for x in range(self.width-4-l-r):
                    bgcol = (0,0,255)
                    char = " "
                    fgcol = (0,0,0)
                    bgset = 1
                    tiles += [[self.width-x-3,y,bgcol,
                        char,fgcol,bgset]]
            y+=1
            # label: bar
            # cur/max
            # [space]
            cur = str(cur)
            max = str(max)
            for x in range(len(cur)):
                bgcol = (0,0,0)
                char = cur[x]
                fgcol = (255,255,255)
                bgset = 1
                tiles += [[x+2,y,bgcol,char,fgcol,bgset]]
            tiles += [[len(cur)+2,y,(0,0,0),'/',(255,255,255),1]]
            for x in range(len(max)):
                bgcol = (0,0,0)
                char = max[x]
                fgcol = (255,255,255)
                bgset = 1
                tiles += [[x+len(cur)+3,y,bgcol,char,fgcol,bgset]]
            self.update(tiles)
            y += 2
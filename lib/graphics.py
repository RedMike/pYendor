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
#
# tile = (x, y, bgcol, char, fgcol, bgset)
# msg = (bgcol, msg, fgcol, bgset)
# choice = (text, ret)


def convert(color):
    """Convert color to libtcod.Color."""
    if not isinstance(color,libtcod.Color):
        color = libtcod.Color(*color)
    return color

def listTile(tile):
    """Turn tuple, list or Tile object into tuple."""
    if not isinstance(tile,list) and not isinstance(tile,tuple):
        x = tile.x
        y = tile.y
        bgcol = tile.bgcol
        char = tile.char
        fgcol = tile.fgcol
        bgset = tile.bgset
    else:
        x = tile[0]
        y = tile[1]
        bgcol = tile[2]
        char = tile[3]
        fgcol = tile[4]
        bgset = tile[5]
    return (x, y, bgcol, char, fgcol, bgset)

class WindowManager(object):
    """Window manager class that handles Application <-> Window actions.

    Ideally, only import WindowManager from graphics. Any colors passed should
    be tuples like (r,g,b), with values between 0 and 255. Modify associations
    for custom window types."""
    
    def __init__(self,w,h,name):
        """Initialisation method, also creates root window."""
        self.window = RootWindow(w,h,name)
        self.layers = {}
        self.assoc = {}
        ass1 = ['lgw','bmw','cw','iw','dbw','mcw','sw','gw']
        ass2 = [LayeredGameWindow, BorderedMessageWindow, ChoiceWindow,
                InputWindow, DebugWindow, MultiChoiceWindow,
                StatusWindow, GridWindow]
        for id in range(len(ass1)):
            self.addAssoc(ass1[id],ass2[id])
        
    def addAssoc(self,key,obj):
        """Add new association between window class and string."""
        self.assoc[key] = obj

    def removeWindow(self,win):
        """Remove window from drawing list."""
        for i in self.layers.keys():
            v = self.layers[i]
            for j, w in enumerate(v):
                if win == w[0]:
                    del v[j]

    def clearLayer(self,layer):
        """Delete a whole layer."""
        for window in self.layers[layer]:
            self.window.removeWindow(window)
        del self.layers[layer]

    
    def draw(self):
        """Draw whole drawing list."""
        for i in self.layers.keys():
            v = self.layers[i]
            for j, w in enumerate(v):
                win = w[0]
                x = w[1]
                y = w[2]
                if self.window.visibility[win]:
                    self.window.draw(win,x,y)
    
    
    def addWindow(self,layer,type,w,h,x,y):
        """Add new window to a layer, type passed as str according to assoc."""
        if type in self.assoc:
            type = self.assoc[type]
            if layer not in self.layers:
                self.layers[layer] = []
            win = self.window.addWindow(type,w,h,x,y)
            self.layers[layer].append([win,x,y])
            return win

    def toggleVisible(self,window):
        """Toggle whether a window is visible, helper function."""
        if self.window.visibility[window]:
            self.window.hideWindow(window)
        else:
            self.window.showWindow(window)
        
class RootWindow(object):
    """Root window object that contains all other windows.

    Contains a console onto which everything is blitted, should only be created
    by WindowManager. Has no idea about layering windows, WinMan's job."""

    def __init__(self,w,h,name,font='data/font.png'):
        """Initialisation method, name shows up as the title, with version."""
        self.width = w
        self.height = h
        self.name = name
        self.font = font

        self.specificInit()
        
        self.windows = []
        self.visibility = {}

    def specificInit(self):
        """Library-specific initialisation overwritten for non-libtcod."""
        libtcod.console_set_custom_font(self.font,
                libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
        libtcod.console_init_root(self.width, self.height, self.name, False)
        libtcod.console_credits()
    
    def addWindow(self,type,w,h,x,y):
        """Add a new window, only called by WindowManager."""
        win = type(w,h)
        self.windows += [win]
        self.visibility[win] = 1
        return win

    def hideWindow(self,window):
        """Set a window's visibility flag to 0."""
        self.visibility[window] = 0

    def showWindow(self,window):
        """Set a window's visibility flag to 1."""
        self.visibility[window] = 1
    
    def removeWindow(self,window):
        """Remove a window, called by WindowManager."""
        if window in self.windows:
            self.windows.remove(window)
            del self.visibility[window]
        
    def draw(self, win, x, y):
        """Draw a window at a position, called by WindowManager."""
        libtcod.console_blit(win.con, 0, 0,
                win.width, win.height, 0, x, y)
        libtcod.console_flush()

class Window(object):
    """Basic window from which all are derived from."""
    
    def __init__(self,w,h):
        """Initialisation, after which you should set bgcol is non-standard."""
        self.width = w
        self.height = h
        self.bgcol = (0,0,0)
        self.specificInit()

    def specificInit(self):
        """Library-specific console initialisation, called in __init__."""
        self.con = libtcod.console_new(self.width,self.height)
    
    def update(self,tiles):
        """Update window with tiles of the form [x,y,bgcol,char,fgcol,bgset]."""
        for tile in tiles:
            x, y, bgcol, char, fgcol, bgset = listTile(tile)
            if x>=0 and x<self.width and y>=0 and y<self.height:
                bgcol = convert(bgcol)
                fgcol = convert(fgcol)
                self.drawChar(x,y,char,bgcol,fgcol,bgset)


    def drawChar(self,x,y,char,bgcol,fgcol,bgset):
        """Library-specific drawing a character at a position with a specific
        color."""
        libtcod.console_set_background_color(self.con,bgcol)
        libtcod.console_set_foreground_color(self.con,fgcol)
        libtcod.console_put_char(self.con, x, y, char, bgset)
    
    # msgs
    # msg = (bgcol, msg, fgcol, bgset)
    def updateMessage(self,msgs):
        """Update window with a list of messages, in the format
        [bgcol, msg, fgcol, bgset]."""
        y = 2
        for msg in msgs:
            bgcol, line, fgcol, bgset = msg
            bgcol = convert(bgcol)
            fgcol = convert(fgcol)
            h = self.getLineHeight(2, y, self.width-4, 0, line)
            if y<self.height-2-h:
                self.printLineRect(bgcol, fgcol, 2,y,self.width-4,0,bgset,line)
            y += h

    def printLineRect(self,bgcol,fgcol,x,y,w,h,bgset,msg):
        """Library-specific drawing a string inside a rect."""
        libtcod.console_set_background_color(self.con,bgcol)
        libtcod.console_set_foreground_color(self.con,fgcol)
        libtcod.console_print_left_rect(self.con,x,y,w,h,bgset,msg)

    def getLineHeight(self,x,y,w,h,msg):
        """Library-specific predicting height of a string inside a rect."""
        return libtcod.console_height_left_rect(self.con,x,y,w,h,msg)
    
    def clear(self,bgcol = -1, fgcol = (255,255,255)):
        """Clear window to a color."""
        if not isinstance(bgcol, tuple):
            bgcol = self.bgcol
        bgcol = convert(bgcol)
        fgcol = convert(fgcol)
        self.consoleClear(bgcol,fgcol)

    def consoleClear(self,bgcol,fgcol):
        """Library-specific clearing of console to a color."""
        libtcod.console_set_background_color(self.con,bgcol)
        libtcod.console_set_foreground_color(self.con,fgcol)
        libtcod.console_clear(self.con)

class BorderedWindow(Window):
    """Window with a set tile border."""
    
    def __init__(self,w,h):
        """Initialisation method, call setBorder after."""
        super(BorderedWindow,self).__init__(w,h)
        self.borderTile = False
    
    def setBorder(self,tile):
        """Set the border type, like a regular tile."""
        self.borderTile = tile
        self.restoreBorder()
    
    def restoreBorder(self):
        """Restore border, called after clearing."""
        if self.borderTile:
            tiles = []
            for i in range(self.width):
                tiles += [[i,0]+self.borderTile]
                tiles += [[i,self.height-1]+self.borderTile]
            for i in range(self.height):
                tiles += [[0,i]+self.borderTile]
                tiles += [[self.width-1,i]+self.borderTile]
            self.update(tiles)
    
    def clear(self,bgcol = -1, fgcol = (255,255,255)):
        """Clear window to a color, then restore border."""
        super(BorderedWindow,self).clear(bgcol,fgcol)
        self.restoreBorder()

class LayeredGameWindow(BorderedWindow):
    """Main game window, supports layers."""
    
    def __init__(self,w,h):
        """Initialisation method."""
        super(LayeredGameWindow,self).__init__(w,h)
        self.layers = {}
    
    def updateLayer(self,layer,tiles):
        """Update a layer with a list of tiles."""
        map = []
        for tile in tiles:
            tile = listTile(tile)
            map += [tile]
        self.layers[layer] = map
        self.updateLayers()

    def updateLayerWEnts(self,layer,ents):
        """Update a layer with a list of entities."""
        self.clear()
        tiles = []
        for ent in ents:
            if ent.getAttribute('visible'):
                tiles.append(ent.getTile())
        self.updateLayer(layer,tiles)
        self.updateLayers()

    def updateLayers(self):
        """Update all layers, then restore border."""
        for layer in self.layers.itervalues():
            self.update(layer)
        self.restoreBorder()
    
class BorderedMessageWindow(BorderedWindow):
    """Main messaging window type."""
    
    def __init__(self,w,h):
        """Initialisation method."""
        super(BorderedMessageWindow,self).__init__(w,h)
        self.messages = []
        
    def getCurrentHeight(self):
        """Returns current height of messages in window."""
        y = 2
        for msg in self.messages:
            y += self.getLineHeight(2, y, self.width-4, 0, msg[1])
        return y
                
    # msg = (bgcol, msg, fgcol, bgset)
    def addMessages(self,msgs):
        """Add messages in format (bgcol, msg, fgcol, bgset)."""
        y = self.getCurrentHeight()
        for msg in msgs:
            h = self.getLineHeight(2, y, self.width-4, 0, msg[1])
            while y+h>self.height-2-h:
                del self.messages[0]
                y = self.getCurrentHeight()
            self.messages.append(msg)
        self.clear()
        self.updateMessage(self.messages)
    
class ChoiceWindow(BorderedMessageWindow):
    """Main menu type, single choice from multiple ones."""
    
    def __init__(self,w,h):
        """Initialisation method."""
        super(ChoiceWindow,self).__init__(w, h)
        self.labels = []
        self.choices = []
        self.highlight = -1
    
    def setLabel(self,labels):
        """Set choice displayed labels."""
        self.labels = labels
    
    def setChoices(self,choices):
        """Set available choices."""
        self.choices = choices
        if self.highlight == -1 or self.highlight>=len(self.choices):
            self.highlight = 0
        self.tick()
        
    def addChoice(self,choice):
        """Add new choice."""
        self.choices.append(choice)
        if self.highlight == -1:
            self.highlight = 0
        self.tick()
    
    def setHighlight(self,id):
        """Set currently highlighted choice."""
        if id<len(self.choices) and id>=0:
            self.highlight = id
        self.tick()
    
    def moveUp(self):
        """Move currently selected choice up."""
        self.setHighlight(self.highlight-1)
    
    def moveDown(self):
        """Move currently selected choice down."""
        self.setHighlight(self.highlight+1)
    
    def enter(self):
        """Returns currently selected choice or None."""
        if self.highlight != -1:
            return self.choices[self.highlight][1]
    
    # msg = (bgcol, msg, fgcol, bgset)
    # choice = (text, ret)
    def tick(self):
        """Internally-called updater method."""
        self.clear()
        msgs = []
        for label in self.labels:
            msgs += label
        msgs += [[self.bgcol, '', (255,255,255), 1]]
        msgs += [[self.bgcol, '', (255,255,255), 1]]
        for id in range(len(self.choices)):
            choice = self.choices[id]
            line = '  ' + str(id) + '.  ' + choice[0]
            if self.highlight != id:
                msgs += [[self.bgcol, line, (255,255,255), 1]]
            else:
                msgs += [[(255,255,255), line, (0,0,0), 1]]
            msgs += [[self.bgcol, '', (255,255,255), 1]]
        self.updateMessage(msgs)

class GridWindow(BorderedMessageWindow):
    """Main inventory window type."""

    def __init__(self,w,h):
        """Initialisation method."""
        super(GridWindow,self).__init__(w, h+3)
        self.items = []
        self.names = []
        self.tiles = []
        self.choice = 1

    def setItems(self,items):
        """Set contained items in format (id,tile,name) and tile in format
        (x,y,bgcol,char,fgcol,bgset); x and y are ignored."""
        self.items = items
        self.updateItems()

    def setNames(self,names):
        """Set display names."""
        self.names = names

    def updateItems(self):
        """Internally-called updater for items."""
        self.tiles = []
        self.names = ['debug' for i in range(len(self.items))]
        i = 3
        j = 3
        for item in self.items:
            #(x, y, bgcol, char, fgcol, bgset)
            tile = item[1]
            c = (0,0,0)
            if item[0] == self.choice:
                c = (120,55,10)
            r = [i, j, c, tile[0], tile[1], 1 ]
            self.names[item[0]-1] = tile[2]
            self.tiles += [r]

            i += 2
            if i>self.width-4:
                i = 3
                j += 2
        #finish checkerboard
        if len(self.tiles) != 0:
            i = self.tiles[-1][0]
            j = self.tiles[-1][1]
        else:
            i = 1
            j = 3
        k = len(self.items)
        while j < self.height - 7:
            i += 2
            k += 1
            if i>self.width-4:
                j += 2
                i = 3
            if j >= self.height -7:
                break
            c = (0,0,0)
            if self.choice == k:
                c = (120,55,10)
            t = [i,j,c,' ',(0,0,0),1]
            self.tiles += [t]

        for j in range(self.height-5,self.height):
            for i in range(0,self.width):
                r = [i, j, (0,0,0), ' ', (255,255,255), 1 ]
                self.tiles += [r]
        self.update(self.tiles)

    def moveLeft(self):
        """Move choice left."""
        if self.choice>1:
            self.choice -= 1
        self.updateItems()

    def moveRight(self):
        """Move choice right."""
        self.choice += 1
        self.updateItems()

    def moveUp(self):
        """Move choice up."""
        self.choice -= (self.width-6)/2
        if self.choice<1:
            self.choice = 1
        self.updateItems()

    def moveDown(self):
        """Move choice down."""
        self.choice += (self.width-6)/2
        self.updateItems()

    def enter(self):
        """Return currently selected item or -1."""
        #might not make sense, but self.choice can be on a
        # nonexistent item
        for it in self.items:
            if it[0] == self.choice:
                return it[0]
        return -1

    def update(self,tiles):
        """Overridden update method, also draws currently selected item name."""
        super(GridWindow,self).update(tiles)
        if self.choice-1 < len(self.names):
            bgcol = convert((0,0,0))
            fgcol = convert((255,255,255))
            self.printLineRect(bgcol,fgcol,3,self.height-3, self.width,
                    self.height,1,self.names[self.choice-1])

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
        self.input = self.input [:-1]
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
        self.updateMessage(msgs)
        self.restoreBorder()

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
        self.updateMessage(msgs)

class DebugWindow(BorderedWindow):
    """Simple debug window."""

    def debugTick(self,ticks,nrEnts,nrTiles):
        """Update method not internally-called."""
        msgs = []
        # msg = (bgcol, msg, fgcol, bgset)
        msgs.append([(255,0,0),'Current tick: '+
            str(ticks),(255,255,255),1])
        msgs.append([(  0,0,0),'Nmbr of ents: '+
            str(nrEnts),(255,255,255),1])
        msgs.append([(  0,0,0),'Nmr of tiles: '+
            str(nrTiles),(255,255,255),1])
        self.updateMessage(msgs)

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
        msgs = []
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
import data.libtcodpy as libtcod

class KeyboardListener:
    """Libtcod-based keyboard listener.

    List of key-codes copy-pasted from libtcod.
    """

    KEY_NONE = 0
    KEY_ESCAPE = 1
    KEY_BACKSPACE = 2
    KEY_TAB = 3
    KEY_ENTER = 4
    KEY_SHIFT = 5
    KEY_CONTROL = 6
    KEY_ALT = 7
    KEY_PAUSE = 8
    KEY_CAPSLOCK = 9
    KEY_PAGEUP = 10
    KEY_PAGEDOWN = 11
    KEY_END = 12
    KEY_HOME = 13
    KEY_UP = 14
    KEY_LEFT = 15
    KEY_RIGHT = 16
    KEY_DOWN = 17
    KEY_PRINTSCREEN = 18
    KEY_INSERT = 19
    KEY_DELETE = 20
    KEY_LWIN = 21
    KEY_RWIN = 22
    KEY_APPS = 23
    KEY_0 = 24
    KEY_1 = 25
    KEY_2 = 26
    KEY_3 = 27
    KEY_4 = 28
    KEY_5 = 29
    KEY_6 = 30
    KEY_7 = 31
    KEY_8 = 32
    KEY_9 = 33
    KEY_KP0 = 34
    KEY_KP1 = 35
    KEY_KP2 = 36
    KEY_KP3 = 37
    KEY_KP4 = 38
    KEY_KP5 = 39
    KEY_KP6 = 40
    KEY_KP7 = 41
    KEY_KP8 = 42
    KEY_KP9 = 43
    KEY_KPADD = 44
    KEY_KPSUB = 45
    KEY_KPDIV = 46
    KEY_KPMUL = 47
    KEY_KPDEC = 48
    KEY_KPENTER = 49
    KEY_F1 = 50
    KEY_F2 = 51
    KEY_F3 = 52
    KEY_F4 = 53
    KEY_F5 = 54
    KEY_F6 = 55
    KEY_F7 = 56
    KEY_F8 = 57
    KEY_F9 = 58
    KEY_F10 = 59
    KEY_F11 = 60
    KEY_F12 = 61
    KEY_NUMLOCK = 62
    KEY_SCROLLLOCK = 63
    KEY_SPACE = 64
    KEY_CHAR = 65

    def __init__(self):
        self.bindings = { }
        self.default = None
        self.default_params = ()

    def set_default_binding(self,fct,params=()):
        """Sets the default callback for keys, use None to disable.

        Callback's function takes three arguments: mods, char, vk. Where mods is a dict of the following shape:
        {'lalt' : bool, 'ralt' : bool, 'lctrl' : bool, 'rctrl' : bool, 'shift' : bool}, char is the printable char if
        any are available, and vk is one of the KEY_* elements in this class.

        @type  fct: method
        @param fct: Function to be called for any unhandled keys.
        @type  params: tuple
        @param params: Parameters to call the function with as last arguments.
        """
        self.default = fct
        self.default_params = params

    def add_bindings(self,vk,bind):
        """Adds a keycode binding to the listener.

        Does nothing for CHAR or numbers.

        @type  vk: int
        @param vk: KEY_* keycode.
        @type  bind: tuple
        @param bind: Tuple of the form (fct, (param1, param2, ..)).
        """
        if (vk < self.KEY_0 or vk > self.KEY_9) and vk != self.KEY_CHAR:
            self.bindings[vk] = bind


    
    def add_char_binding(self,key,bind):
        """Adds a character binding to the listener.

        @type  key: char
        @param key: Character to which to add a binding.
        @type  bind: tuple
        @param bind: Tuple of the form (fct, (param1, param2, ..)).
        """
        self.bindings[key] = bind
    
    def remove_binding(self,key):
        """Removes a binding.

        @type  key: char
        @param key: Binding to remove.
        """
        del self.bindings[key]

    def clear_bindings(self):
        """Removes all bindings."""
        self.bindings = dict()
        self.default = None

    def tick(self):
        """Tick and run the bindings for the next keypress event.

        For the binding (fct, (p1, p2, p3, ...)), fct gets called with p1, p2, p3, ... as parameters.
        """
        key = libtcod.console_wait_for_keypress(False)
        k = chr(key.c)
        vk = key.vk
        if vk in self.bindings:
            f = self.bindings[vk][0]
            vars = self.bindings[vk][1]
            f(*vars)
        elif k in self.bindings:
            f = self.bindings[k][0]
            vars = self.bindings[k][1]
            f(*vars)
        elif self.default is not None:
            mods = {'lalt' : key.lalt, 'ralt' : key.ralt, 'lctrl' : key.lctrl, 'rctrl' : key.rctrl, 'shift' : key.shift}
            k = chr(key.c)
            vk = key.vk
            t = (mods,k,vk) + self.default_params
            self.default(*t)

    

            
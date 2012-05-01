import data.libtcodpy as libtcod

class KeyboardListener:
    """Libtcod-based keyboard listener.

    List of key-codes copy-pasted from libtcod.
    """

    char_codes = {
        'none' : 0,
        'escape' : 1,
        'backspace' : 2,
        'tab' : 3,
        'enter' : 4,
        'shift' : 5,
        'control' : 6,
        'alt' : 7,
        'pause' : 8,
        'caps_lock' : 9,
        'page_up' : 10,
        'page_down' : 11,
        'end' : 12,
        'home' : 13,
        'arrow_up' : 14,
        'arrow_left' : 15,
        'arrow_right' : 16,
        'arrow_down' : 17,
        'print_screen' : 18,
        'insert' : 19,
        'delete' : 20,
        'left_win' : 21,
        'right_win' : 22,
        'apps' : 23,
        'zero' : 24,
        'one' : 25,
        'two' : 26,
        'three' : 27,
        'four' : 28,
        'five' : 29,
        'six' : 30,
        'seven' : 31,
        'eight' : 32,
        'nine' : 33,
        'keypad_zero' : 34,
        'keypad_one' : 35,
        'keypad_two' : 36,
        'keypad_three' : 37,
        'keypad_four' : 38,
        'keypad_five' : 39,
        'keypad_six' : 40,
        'keypad_seven' : 41,
        'keypad_eight' : 42,
        'keypad_nine' : 43,
        'keypad_add' : 44,
        'keypad_sub' : 45,
        'keypad_div' : 46,
        'keypad_mul' : 47,
        'keypad_dec' : 48,
        'keypad_enter' : 49,
        'F1' : 50,
        'F2' : 51,
        'F3' : 52,
        'F4' : 53,
        'F5' : 54,
        'F6' : 55,
        'F7' : 56,
        'F8' : 57,
        'F9' : 58,
        'F10' : 59,
        'F11' : 60,
        'F12' : 61,
        'numlock' : 62,
        'scroll_lock' : 63,
        'space' : 64,
        'char' : 65
    }

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

    def add_keycode_binding(self,key,bind):
        """Adds a keycode binding to the listener.

        Does nothing for CHAR or numbers.

        @type  key: str
        @param key: key from X{self.non_char_binds}.
        @type  bind: tuple
        @param bind: Tuple of the form (fct, (param1, param2, ..)).
        """
        if key not in ('zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'char'):
            self.bindings[self.char_codes[key]] = bind
    
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

    

            
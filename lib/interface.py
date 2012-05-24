import data.libtctrout as libtctrout

class KeyboardListener:
    """Libtcod-based keyboard listener.
    """

    char_codes = {
        'none' : 0,
        'escape' : libtctrout.K_ESCAPE,
        'backspace' : libtctrout.K_BACKSPACE,
        'tab' : libtctrout.K_TAB,
        'enter' : libtctrout.K_RETURN,
        'shift' : libtctrout.KMOD_SHIFT,
        'control' : libtctrout.KMOD_CTRL,
        'alt' : libtctrout.KMOD_ALT,
        'pause' : libtctrout.K_PAUSE,
        'caps_lock' : libtctrout.K_CAPSLOCK,
        'page_up' : libtctrout.K_PAGEUP,
        'page_down' : libtctrout.K_PAGEDOWN,
        'end' : libtctrout.K_END,
        'home' : libtctrout.K_HOME,
        'arrow_up' : libtctrout.K_UP,
        'arrow_left' : libtctrout.K_LEFT,
        'arrow_right' : libtctrout.K_RIGHT,
        'arrow_down' : libtctrout.K_DOWN,
        'print_screen' : libtctrout.K_PRINT,
        'insert' : libtctrout.K_INSERT,
        'delete' : libtctrout.K_DELETE,
        'left_win' : libtctrout.K_LSUPER,
        'right_win' : libtctrout.K_RSUPER,
        'apps' : libtctrout.K_LMETA,
        '0' : libtctrout.K_0,
        '1' : libtctrout.K_1,
        '2' : libtctrout.K_2,
        '3' : libtctrout.K_3,
        '4' : libtctrout.K_4,
        '5' : libtctrout.K_5,
        '6' : libtctrout.K_6,
        '7' : libtctrout.K_7,
        '8' : libtctrout.K_8,
        '9' : libtctrout.K_9,
        'keypad_zero' : libtctrout.K_KP0,
        'keypad_one' : libtctrout.K_KP1,
        'keypad_two' : libtctrout.K_KP2,
        'keypad_three' : libtctrout.K_KP3,
        'keypad_four' : libtctrout.K_KP4,
        'keypad_five' : libtctrout.K_KP5,
        'keypad_six' : libtctrout.K_KP6,
        'keypad_seven' : libtctrout.K_KP7,
        'keypad_eight' : libtctrout.K_KP8,
        'keypad_nine' : libtctrout.K_KP9,
        'keypad_add' : libtctrout.K_KP_PLUS,
        'keypad_sub' : libtctrout.K_KP_MINUS,
        'keypad_div' : libtctrout.K_KP_DIVIDE,
        'keypad_mul' : libtctrout.K_KP_MULTIPLY,
        'keypad_dec' : libtctrout.K_KP_PERIOD,
        'keypad_enter' : libtctrout.K_KP_ENTER,
        'F1' : libtctrout.K_F1,
        'F2' : libtctrout.K_F2,
        'F3' : libtctrout.K_F3,
        'F4' : libtctrout.K_F4,
        'F5' : libtctrout.K_F5,
        'F6' : libtctrout.K_F6,
        'F7' : libtctrout.K_F7,
        'F8' : libtctrout.K_F8,
        'F9' : libtctrout.K_F9,
        'F10' : libtctrout.K_F10,
        'F11' : libtctrout.K_F11,
        'F12' : libtctrout.K_F12,
        'numlock' : libtctrout.K_NUMLOCK,
        'scroll_lock' : libtctrout.K_SCROLLOCK,
        ' ' : libtctrout.K_SPACE,
        'a' : libtctrout.K_a,
        'b' : libtctrout.K_b,
        'c' : libtctrout.K_c,
        'd' : libtctrout.K_d,
        'e' : libtctrout.K_e,
        'f' : libtctrout.K_f,
        'g' : libtctrout.K_g,
        'h' : libtctrout.K_h,
        'i' : libtctrout.K_i,
        'j' : libtctrout.K_j,
        'k' : libtctrout.K_k,
        'l' : libtctrout.K_l,
        'm' : libtctrout.K_m,
        'n' : libtctrout.K_n,
        'o' : libtctrout.K_o,
        'p' : libtctrout.K_p,
        'q' : libtctrout.K_q,
        'r' : libtctrout.K_r,
        's' : libtctrout.K_s,
        't' : libtctrout.K_t,
        'u' : libtctrout.K_u,
        'v' : libtctrout.K_v,
        'w' : libtctrout.K_w,
        'x' : libtctrout.K_x,
        'y' : libtctrout.K_y,
        'z' : libtctrout.K_z,
        '!' : libtctrout.K_EXCLAIM,
        '"' : libtctrout.K_QUOTEDBL,
        '#' : libtctrout.K_HASH,
        '$' : libtctrout.K_DOLLAR,
        '&' : libtctrout.K_AMPERSAND,
        '\'': libtctrout.K_QUOTE,
        '(' : libtctrout.K_LEFTPAREN,
        ')' : libtctrout.K_RIGHTPAREN,
        '*' : libtctrout.K_ASTERISK,
        '+' : libtctrout.K_PLUS,
        '-' : libtctrout.K_MINUS,
        ',' : libtctrout.K_COMMA,
        '.' : libtctrout.K_PERIOD,
        ':' : libtctrout.K_COLON,
        ';' : libtctrout.K_SEMICOLON,
        '<' : libtctrout.K_LESS,
        '=' : libtctrout.K_EQUALS,
        '>' : libtctrout.K_GREATER,
        '?' : libtctrout.K_QUESTION,
        '@' : libtctrout.K_AT,
        '[' : libtctrout.K_LEFTBRACKET,
        ']' : libtctrout.K_RIGHTBRACKET,
        '\\': libtctrout.K_BACKSLASH,
        '^' : libtctrout.K_CARET,
        '_' : libtctrout.K_UNDERSCORE,
        '`' : libtctrout.K_BACKQUOTE
    }
    mods_codes = {
        'shift' : libtctrout.KMOD_SHIFT,
        'lctrl' : libtctrout.KMOD_LCTRL,
        'rctrl' : libtctrout.KMOD_RCTRL,
        'lalt' : libtctrout.KMOD_LALT,
        'ralt' : libtctrout.KMOD_RALT,
    }

    key_codes = dict((v,k) for k, v in char_codes.iteritems())

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

    def add_binding(self,key,bind):
        """Adds a keycode binding to the listener.

        @type  key: str
        @param key: key from X{self.non_char_binds}.
        @type  bind: tuple
        @param bind: Tuple of the form (fct, (param1, param2, ..)).
        """
        self.bindings[self.char_codes[key]] = bind

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

        keys = libtctrout.get_key()
        for key in keys:
            vk = key.key
            if vk in self.bindings:
                f = self.bindings[vk][0]
                vars = self.bindings[vk][1]
                f(*vars)
            elif self.default:
                mods = {'lalt' : 0, 'ralt' : 0, 'lctrl' : 0,
                        'rctrl' : 0, 'shift' : 0}
                for mod in mods:
                    mods[mod] = key.mod & self.mods_codes[mod]
                ch = key.unicode
                if ch:
                    if ord(ch) <= 31 and ord(ch) != 9:
                        ch = ''
                t = (mods,ch,vk) + self.default_params
                self.default(*t)

    

            
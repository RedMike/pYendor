import data.libtcodpy as libtcod


#  Interface system
#  Currently, only libtcod.
#
#    Binding format:
#        {char:[function,[var1,var2,...]]}

class KeyboardListener:
    """Libtcod-based keyboard listener."""
    
    def __init__(self, bindings=None):
        if not bindings: bindings = dict()
        self.bindings = bindings
    
    def add_binding(self,key,bind):
        self.bindings[key] = bind
    
    def remove_binding(self,key):
        del self.bindings[key]

    def clear_bindings(self):
        self.bindings = dict()

    def tick(self):
        key = libtcod.console_wait_for_keypress(False)
        k = chr(key.c)
        if k in self.bindings:
            f = self.bindings[k][0]
            vars = self.bindings[k][1]
            f(*vars)
    

            
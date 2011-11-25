import data.libtcodpy as libtcod


#  Interface system
#  Mainly keyboard-based.
#
#    Binding format:
#        {char:[function,vars]}
#            where vars is a LIST of them.

class KeyboardListener:
    
    def __init__(self,bindings={}):
        self.bindings = bindings
    
    def addBinding(self,key,bind):
        self.bindings[key] = bind
    
    def removeBinding(self,key):
        del self.bindings[key]

    def tick(self):
        key = libtcod.console_wait_for_keypress(False)
        k = chr(key.c)
        ret = { }
        if k in self.bindings:
            f = self.bindings[k][0]
            vars = self.bindings[k][1]
            ret[k] = f(*vars)
        return ret
    

            
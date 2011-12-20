import random
import lib.graphics as graphics
import lib.map as map
import lib.entity as entity
import lib.interface as interface
import lib.time as time
import lib.object as object



class Application:
    """
    Main application class.

    After creating, set up the graphics options. Create the map or maps, then entities. Initialise any specifics.
    Then start calling Update every time you want to update.

    """
    
    version = (0, 5, 0, 'a')
    
    def __init__(self, name, w, h):
        self.exit = 0
        
        # One currently loaded map at any one time, referenced by the index it uses in self.maps. Changing maps is
        # done using change_map to deinitialise everything needed, then reinitialise.
        self.maps = []
        self.map = None
        
        # All entities are scheduled in one global scheduler.
        self.scheduler = time.Scheduler()
                
        # Entities are kept in a dictionary as an id. Keys are a tuple of (x, y).
        # This allows for fast checking for entities in tiles, and raises
        # only a slight problem in keeping them in sync. Picking a class for
        # addEntity is done via the entity manager transparently. Send a string
        # like 'item'. ID lookup is in entityList.
        self.entity_lookup = entity.EntityLookup()
        self.entity_list = { }
        self.entity_pos = { }
        self.entity_cur_id = 0

        # Player and camera entities are saved so that you could switch cameras
        # OR players quite easily.
        self.player = None
        self.camera = None
        
        # Initialise default windows with None.
        self.win_man = graphics.WindowManager(w,h,name+' '+'.'.join(self.version))
        self.game_win = None
        self.menu_win = None
        self.msg_win = None
        self.announcement_win = None
        
        # Initialise keyboard interface.
        self.keyboard = interface.KeyboardListener()


    def default_bindings(self,tmp=0):
        """Bind defaults, generally coupled with a prior clearBindings."""
        player = self.getPlayer()
        if player != None:
            temp = [ ['w',[player.move,(0,-1)]],
                     ['s',[player.move,(0,1)]],
                     ['a',[player.move,(-1,0)]],
                     ['d',[player.move,(1,0)]],
                     ['e',[self.player_pickup,()]],
                     ['q',[self.quit,()]] ]
            for set in temp:
                key = set[0]
                bind = set[1]
                self.add_binding(key,bind)

    def new_level(self):
        """Generates new map and places/transfers player to it."""
        width, height, set = 100, 30, 1
        self.generate_map(width, height, set)
        if len(self.maps) == 1:
            self.populate_ents()
            self.place_player()
        else:
            self.destroyEnts()
            self.populate_ents()
            self.place_player()

    def generate_map(self,w,h,set):
        """Generates new map and adds it, using BasicGenerator from map."""
        self.add_map(file=0,map=map.BasicGenerator(w,h).gen_map(),
                    set=set)

    def add_map(self,file=0,map=0,set=0):
        """Add map to stack from file or object."""
        if map:
            self.maps += [map]
        elif file:
            pass
        if set:
            self.set_map(len(self.maps)-1)

    def set_map(self,id):
        """Set map as current one."""
        if id < len(self.maps):
            self.map = id
    
    def get_map(self):
        """Get current map."""
        if self.map != -1:
            return self.maps[self.map]

    def add_window(self,layer,type,w,h,x,y):
        """Add new window and return it."""
        win = self.win_man.addWindow(layer,type,w,h,x,y)
        return win

    def clearLayer(self,layer):
        """Ask window manager to clear a layer."""
        self.win_man.clearLayer(layer)

    def setGameWindow(self,w):
        """Set current game window to use."""
        self.game_win = w

    def setInvWindow(self,w):
        """Set current inventory window to use and hide it."""
        self.invWin = w
        self.win_man.window.hideWindow(w)

    def setMessageWindow(self,w):
        """Set current message window to use."""
        self.msg_win = w

    def addMessages(self,msgs):
        """Post messages to current message window, takes a list of strings."""
        if self.msg_win != 0:
            for msg in msgs:
                set = [self.msg_win.bgcol,msg,(255,255,255),1]
                self.msg_win.addMessages([set])

    def addAnnouncement(self,msgs,w=50,h=30,x=10,y=10,to=0):
        """Pop up a default announcement window with given messages."""
        win = self.add_window(1,'bmw',w,h,x,y)
        win.setBorder([(255,255,255),' ',(255,255,255),1])
        for msg in msgs:
            set = [(0,0,0),msg,(255,255,255),1]
            win.addMessages([set])
        self.announcement_win = win
        self.transitState(-55)
        self.addBinding('d',[self.transitState,[to]])
        return win

    def cb_addAnnouncement(self,set):
        """Callback for default announcement."""
        #BROKEN, not a proper callback.
        if len(set)==6:
            msgs, w, h, x, y, to = set
        else:
            msgs, w, h, x, y = set
            to = 0
        self.addAnnouncement(msgs,w,h,x,y,to)
    
    def addCompoundMenu(self,choices,w=50,h=30,x=10,y=10):
        """Add a default compound menu with given choices."""
        win = self.add_window(1,'cpw',w,h,x,y)
        for choice in choices:
            win.addChoice(choice[0],choice[1])
        return win

    def addMultiChoice(self,choices,w=50,h=30,x=10,y=10):
        """Add a multiple choice menu with given choices."""
        win = self.add_window(1,'mcw',w,h,x,y)
        for choice in choices:
            win.addChoice(choice[0],choice[1])
        return win

    def toggleWindow(self,window):
        """Toggle whether a window is visible or not."""
        self.win_man.toggleVisible(window)

    def hideWindow(self,window):
        """Hide a window."""
        self.win_man.hideWindow(window)

    def showWindow(self,window):
        """Unhide a window."""
        self.win_man.showWindow(window)

    def dismissAnnouncement(self):
        """Dismiss a shown announcement."""
        if self.announcement_win != -1:
            self.win_man.removeWindow(self.announcement_win)
        self.default_bindings()
    
    #interface work
    def addBinding(self,key,bind):
        """Add a key binding."""
        self.keyb.add_binding(key,bind)
    
    def removeBinding(self,key):
        """Remove a key binding."""
        self.keyb.remove_binding(key)
        if key in self.callback:
            del self.callback[key]

    def clearBindings(self):
        """Clear all key bindings."""
        self.callback = {}

    def addCallback(self,key,fct):
        """Add a key callback."""
        self.callback[key] = fct
        
    #entity work
    #[x,y,ent]
    def addEntity(self,x,y,tile,type,delay=-1):
        """Create a new entity and add it to the list and schedule."""
        ent = self.entMan.get_class(type)(x,y,tile)
        #self.entityList.append([ent.x,ent.y,ent])
        ent.set_attribute('delay',delay)
        ent.set_collision_check(self.checkCollision)
        ent.moveCallback = self.cb_moveEntity
        self.insertEntity(x,y,ent)
        
        self.sched.addSchedule(ent)
        return ent

    def insertEntity(self,x,y,ent):
        """Insert an entity at a position in the entity list."""
        pos = (x, y)
        if pos not in self.entityList:
            self.entityList[pos] = [ent]
        else:
            self.entityList[pos] += [ent]

    def addObject(self,obj,delay=1):
        """Add an object to the list and schedule."""
        self.objectList += [[obj.x,obj.y,obj]]
        obj.delay = delay

        self.objSched.addSchedule(obj)
        return obj

    def place_player(self,delay):
        """Add a player entity and set it as the current player."""
        map = self.get_map()
        tiles = map.getRightRect(0,0,3,map.height)
        tile = tiles[0]
        x = tile.x
        y = tile.y
        player = self.addEntity(x,y,[(255,0,0),'@',(0,0,255),0,0,1],
                                'player',delay)
        self.addObject(object.Camera(x,y,1,player))
        self.sched.setDominant(player)
        return player

    def movePlayerToSpawn(self):
        """Move player to the starting point for a Basic map."""
        map = self.get_map()
        tiles = map.getRightRect(0,0,3,map.height)
        tile = tiles[0]
        x = tile.x
        y = tile.y
        player = self.getPlayer()
        col = player.collision
        player.collision = 0
        player.move(x,y)
        player.collision = col

    def getPlayer(self):
        """Returns current player or None."""
        if self.player == None:
            for pos, ents in self.entityList.iteritems():
                for ent in ents:
                    if isinstance(ent,entity.Player):
                        self.player = ent
                        return ent
        return self.player

    def getCamera(self):
        """Returns current camera or None."""
        if self.camera == None:
            for ent in self.objectList:
                if isinstance(ent[2],object.Camera):
                     self.camera = ent[2]
                     return ent[2]
        return self.camera

    def getVisEntsByPos(self,x,y,r=1):
        """Return visible and not hidden entities around a point."""
        ret = []
        for i in range(x-r,x+r):
            for j in range(y-r,y+r):
                if (abs(i-x)<r and abs(j-y)<r) and ((i,j) in self.entityList):
                    for ent in self.entityList[(i,j)]:
                        if (ent.get_attribute('visible') and
                                not ent.get_attribute('hidden')):
                            ret += [ent]
        return ret

    def getEntsByPos(self,x,y,r=1):
        """Return all entities around a point."""
        ret = []
        for i in range(x-r,x+r):
            for j in range(y-r,y+r):
                if (abs(i-x)<r and abs(j-y)<r) and ((i,j) in self.entityList):
                    ret += self.entityList[(i,j)]
        return ret

    def getEntsByRect(self,x,y,w,h):
        """Return all entities inside a rectangle."""
        ret = []
        for i in range(x, x+w):
            for j in range(y, y+h):
                if (i,j) in self.entityList:
                    ret += self.entityList[(i,j)]
        return ret


    def checkCollision(self,ent,targetx,targety):
        """Default collision checker for entities."""
        tile = self.get_map().getTile(targetx,targety)
        if tile == None or tile.blocks:
            return 0
        ents = self.getEntsByPos(targetx,targety)
        ok = 1
        if ent.get_attribute('solid') == 1:
            for entt in ents:
                if entt.get_attribute('solid'):
                    ok = 0
                msgs = entt.collidedWith(ent)
                if msgs != []:
                    self.addMessages(msgs)
        return ok

    #inventory stuff
    def playerPickup(self):
        """Pick up everything under the player and display messages."""
        pl = self.getPlayer()
        list = self.getEntsByPos(pl.x,pl.y,1)
        for ent in list[:]:
            if ent.get_attribute('liftable'):
                self.entityList[(ent.x,ent.y)].remove(ent)
            else:
                list.remove(ent)
        msgs = pl.pickUp(list)
        self.addMessages(msgs)

    def showInventory(self):
        """Display inventory window."""
        pl = self.getPlayer()
        list = pl.gridInventory()
        self.invWin.setItems(list)
        self.clearBindings()
        self.addBinding('w',[self.invWin.moveUp,[]])
        self.addBinding('a',[self.invWin.moveLeft,[]])
        self.addBinding('s',[self.invWin.moveDown,[]])
        self.addBinding('d',[self.invWin.moveRight,[]])
        self.addBinding('e',[self.invWin.enter,[]])
        self.addCallback('e',self.cb_inventoryMenu)
        self.win_man.window.showWindow(self.invWin)

        
    def cb_inventoryMenu(self,ret):
        """Inventory menu callback function."""
        list = self.getPlayer().gridInventory()
        if ret != -1:
            self.addMenu(-51,0,[['Drop ' + list[ret-1][1][2],ret],
                        ['Exit.',0]], self.cb_examineMenu)
            self.transitState(-51)
            self.win_man.window.hideWindow(self.invWin)
            return
        #didn't select an item, end and return
        self.win_man.window.hideWindow(self.invWin)
        self.transitState(0)
        self.default_bindings()

    def cb_examineMenu(self,ret):
        """Examine menu callback function."""
        pl = self.getPlayer()
        list = pl.gridInventory()
        if ret != 0:
            self.dropEntity(list[ret-1][1][3])
            self.addMessages(['You drop the '+list[ret-1][1][2]+
                            ' onto the floor.'])
        self.win_man.window.hideWindow(self.invWin)
        self.transitState(0)
        self.default_bindings()


    def destroyEnts(self):
        """Destroy all entities except for the player"""
        #TODO except inventory
        pl = self.getPlayer()
        self.entityList = {(pl.x,pl.y) : [pl]}

    def populate_ents(self):
        """Populate the map with entities."""
        map = self.get_map()
        #let's add an end to the level first.
        tiles = map.getRect(map.width-2,map.height/2,10,1)
        tiles = tiles[0]
        tile = [self.game_win.bgcol, 'O', (255,255,255), 1, 1, 0]
        portal = self.addEntity(tiles.x, tiles.y, tile, 'trap')
        portal.events = [[self.newLevel,()]]

        #let's set up a list of various items that we'll create
        clses = ['item',        'item',        'item',         'item'       ]
        names = ['rock',        'string',      'net',          'bone'       ]
        fgcols =[ (255,178,115), (18,64,171), (18,64,171),  (255,178,115)   ]
        chars = [',',           '(',           '#',            '('          ]
        delays =[-1,             -1,            -1,             -1          ]

        clses += ['beast',      ]
        names += ['kobold',     ]
        fgcols +=[(255,178,115),]
        chars += ['k',          ]
        delays +=[0,            ]

        #split the ground in several bits
        rarity = 4
        for i in range(map.width/rarity):
            x = i*rarity
            #see if there's a spot we can leave a tile on there.
            tiles = map.getRect(x,random.randint(5,map.height-5),10,1)
            if tiles != []:
                #there is, let's leave one of those objects.
                r = random.randint(0,len(names)-1)
                #on a tile at random from the list.
                j = random.randint(0,len(tiles)-1)

                x = tiles[j].x
                y = tiles[j].y
                bgcol = (0,0,0)
                char = chars[r]
                fgcol = fgcols[r]
                bgset = 0
                blocksLight = 0
                blocks = 0

                delay = delays[r]
                if delay == 0:
                    delay = random.randint(1,10)

                tile = [bgcol,char,fgcol,bgset,blocks,blocksLight]
                ent = self.addEntity(x,y,tile,clses[r],delay)
                ent.name = names[r]

        #doors
#        for i in range(self.getMap().width):
#            r = random.randint(0,10)
#            if r == 1:
#                tiles = self.getMap().getRightRect(i,0,1,self.getMap().height)
#                if len(tiles) == 3:
#                    for tile in tiles:
#                        x = tile.x
#                        y = tile.y
#                        bgcol = (155,155,155)
#                        char = '+'
#                        fgcol = (255,125,125)
#                        bgset = 1
#                        tile = [bgcol, char, fgcol, bgset, 1, 1]
#                        self.addEntity(x,y,tile,'door')

        #beasts
#        rarity = 4
#        for i in range(self.getMap().width/rarity):
#            x = i*rarity
#            tiles = self.getMap().getRect(x,random.randint(5,self.getMap().height-5),10,1)
#            if tiles != []:
#                j = random.randint(0,len(tiles)-1)
#                x = tiles[j].x
#                y = tiles[j].y
#                bgcol = (0,0,0)
#                char = 'b'
#                fgcol = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
#                bgset = 0
#                blocksLight = 0
#                blocks = 1
#                tile = [bgcol,char,fgcol,bgset,blocks,blocksLight]
#                delay = random.randint(1,15)
#                ent = self.addEntity(x,y,tile,'beast',delay=delay)
                
    #menu work
    #default menu is added. Custom menus need functions in main.
    #addMenu(from_state,mid_state,to_state,choices,callback)
    #Callback is called with option chosen.
    #   MUST have self before opt.
    def addMenu(self,mid,to,choices,callback):
        """Add a new menu from the choices given."""
        self.addTransition(-140,mid,[0,(choices,callback)],self.menuInit)
        self.addTransition(mid,to,[1,()],self.menuDest)

    def menuInit(self,choices,callback):
        """Initialise a menu window."""
        if self.menu_win != -1:
            self.menuDest()
        self.menu_win = self.add_window(1,'cw',100,30,0,0)
        self.menu_win.setBorder([(255,255,255),' ',(255,255,255),1])
        self.menu_win.setChoices(choices)
        self.clearBindings()
        self.addBinding('w',[self.menu_win.moveUp,()])
        self.addBinding('s',[self.menu_win.moveDown,()])
        self.addBinding('d',[self.menu_win.enter,()])
        self.addCallback('d',callback)

    def menuDest(self):
        """Close a menu window."""
        self.win_man.removeWindow(self.menu_win)
        self.menu_win = -1
        self.default_bindings()
    
    #cutscene work
    def addCutscene(self,state,list,stateTo=0,timePass=0):
        """Add a new cutscene at the given state."""
        list += [stateTo]
        self.cutscenes[state] = list
        self.addTransition(-140,state,[0,()],self.enterCutscene)
        self.addTransition(state,stateTo,[timePass,()],self.exitCutscene)

    def enterCutscene(self,x):
        """Initialising for cutscene start."""
        #print 'Entered cutscene '+str(self.curState)+'.'
        self.clearBindings()

    def exitCutscene(self,x):
        """Deinitialising for cutscene end."""
        #print 'Exited cutscene. Onwards to state '+str(self.curState)+'.'
        self.cutsceneIndicator = 0
        self.default_bindings()

    def dropEntity(self,ent):
        """Drop an entity from player."""
        pl = self.getPlayer()
        id = pl.getContained(ent)
        pl.uncontainObject(id)
        pos = (ent.x, ent.y)
        self.insertEntity(pos[0],pos[1],ent)

    def cb_moveEntity(self,ent,x,y):
        """Entity move callback."""
        pos = (ent.x, ent.y)
        self.entityList[pos].remove(ent)
        self.insertEntity(x,y,ent)

    #state work
    #transition: [[[opt1,opt2,opt3],fct],assoc1,assoc2]
    #transitions is a dict of dict of list
    #           {'from':{'to':[[opts],fct]}}
    #opts: first = timePassing
    def addTransition(self,fro,to,opts,fct):
        """Add a state transition function, state -140 is wildcard."""
        if fro not in self.transitions:
            self.transitions[fro] = {}
        self.transitions[fro][to] = []
        self.transitions[fro][to] += [opts]
        if fct!=0:
            self.transitions[fro][to] += [fct]
        
    def transitState(self,to):
        """Trigger a state transition."""
        #print 'Transition from '+str(self.curState)+' to '+str(to)
        self.clearBindings()
        self.timePassing = 0
        found = 0
        if self.curState in self.transitions:
            if to in self.transitions[self.curState]:
                opts = self.transitions[self.curState][to][0]
                if opts[0]:
                    self.timePassing = 1
                self.transitions[self.curState][to][1](*opts[1])
                found = 1
            elif -140 in self.transitions[self.curState]:
                opts = self.transitions[self.curState][-140][0]
                if opts[0]:
                    self.timePassing = 1
                self.transitions[self.curState][-140][1](*opts[1])
                found = 1
        if not found:
            if -140 in self.transitions:
                if to in self.transitions[-140]:
                    opts = self.transitions[-140][to][0]
                    if opts[0]:
                        self.timePassing = 1
                    self.transitions[-140][to][1](*opts[1])
                elif -140 in self.transitions[-140]:
                    opts = self.transitions[-140][-140][0]
                    if opts[0]:
                        self.timePassing = 1
                    self.transitions[-140][-140][1](*opts[1])
        self.curState = to


    def syncEnts(self):
        """Syncronise entity lists."""
#        for x, y in self.entityList:
#            ents = self.entityList[(x,y)][:]
#            for ent in ents:
#                if ent.x != x or ent.y != y:
#                    self.entityList[(x,y)].remove(ent)
#                    self.insertEntity(x,y,ent)
        
    def update(self):
        """Update function, called every tick."""
        #updates
        #self.winMan.tick()


        #cutscenes
        if self.curState in self.cutscenes:
            #print 'In cutscene '+str(self.curState)
            if self.cutsceneIndicator<=len(self.cutscenes[self.curState])-2:
                set = self.cutscenes[self.curState][self.cutsceneIndicator]
                #print 'Running '+str(set[0])+' with '+str(set[1])
                set[0](set[1])
                self.cutsceneIndicator += 1
            else:
                self.transitState(
                        self.cutscenes[self.curState][self.cutsceneIndicator])


        #drawn
        if self.curState < 0:
            self.win_man.window.hideWindow(self.game_win)
        if self.curState >= 0:
            self.win_man.window.showWindow(self.game_win)
            cam = self.getCamera()
            map = self.get_map()
            if cam != None:
                self.game_win.updateLayer(0,cam.sortTiles(map.getTiles(),100,30))
                self.game_win.updateLayerWEnts(1,cam.sortEnts(
                        self.getVisEntsByPos(cam.x,cam.y,50),100,30))
                self.game_win.updateLayerWEnts(2,cam.sortEnts([self.getPlayer()],
                        100,30))
        self.win_man.draw()

        #input
        if self.curState not in self.cutscenes:
            ret = self.keyb.tick()
            for callback in self.callback:
                if callback in ret:
                    self.callback[callback](ret[callback])
        else:
            self.sched.sleep(0.25)
        if self.timePassing:
            self.sched.tick()

        self.objSched.tick()
        #self.syncEnts()
        #print 'Turn '+str(self.sched.ticks) 
        
    def quit(self):
        """Exit application."""
        self.exit = 1

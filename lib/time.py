
from __future__ import absolute_import
import time

class Scheduler:
    
    #ent = [delay,ent]
    def __init__(self,ents):
        self.ticks = 0
        self.queue = {}
        for ent in ents:
            self.addEntity(ent)
        self.dominant = 0

    def addFctSchedule(self,fct,delay):
        self.queue.setdefault(self.ticks + delay,[]).append([fct])
        
    def addSchedule(self,ent):
        #delay -1 == ent doesn't need regular updates
        delay = ent.getAttribute('delay')
        if delay != -1:
            self.queue.setdefault(self.ticks + delay,[]).append([delay,ent])

    def setDominant(self,ent):
        self.dominant = [ent.getAttribute('delay'),ent]
    
    def tick(self):
        done = 0
        while not done:
            sets = []
            while sets == [] and self.queue != {}:
                sets = self.queue.pop(self.ticks,[])
                self.ticks += 1
            for set in sets:
                if len(set)==2:
                    ent = set[1]
                    ent.update()
                    self.addSchedule(ent)
                elif len(set)==1:
                    fct = set[0]
                    fct()
            if not self.dominant:
                done = 1
            else:
                if self.dominant in sets:
                    done = 1

    def sleep(self,sec):
        time.sleep(sec)
        
                
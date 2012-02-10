
from __future__ import absolute_import
import time

class Scheduler:
    """Can schedule functions to be called a few ticks in the future.

    If dominant id is not set, it'll stop on the first draw_tiles it finds. Queue's keys are update numbers, value is a list
    containing tuples of the form (function, params, delay).
    """
    def __init__(self):
        self.ticks = 0
        self.queue = { }
        self.lookup = { }
        self.current_id = 0
        self.dominant = None

    def add_schedule(self, set, id=0):
        """Returns the id you can use to cancel a scheduled task."""
        if not id:
            id = self.current_id
            self.lookup[id] = set
            self.current_id += 1
        else:
            for key in self.lookup:
                if self.lookup[key] == set:
                    id = key
                    break
        fct, args, delay = set
        if self.ticks + delay not in self.queue:
            self.queue[self.ticks + delay] = []
        self.queue[self.ticks + delay].append(set)
        return id

    def cancel_schedule(self, id):
        """Cancels a schedule from running."""
        for tick in self.queue:
            sets = self.queue[tick]
            for set in sets:
                if self.lookup[id] == set:
                    sets.remove(set)
        del self.lookup[id]

    def set_dominant(self,id):
        """Call with None in order to stop every useful update."""
        if id is not None:
            self.dominant = self.lookup[id]
        else:
            self.dominant = None

    def tick(self):
        """Find the first useful update, then run everything in it; If one of the run functions was the dominant or
        dominant is None, stop after this, otherwise keep going."""
        done = 0
        while not done:
            sets = []
            while sets == [] and self.queue != {}:
                sets = self.queue.pop(self.ticks,[])
                self.ticks += 1
            for set in sets:
                # run the function
                set[0](*set[1])
                self.add_schedule(set,set[2])
                if self.dominant == set:
                    done = 1
            if self.dominant is None:
                done = 1

    def sleep(self,sec):
        time.sleep(sec)
        
                
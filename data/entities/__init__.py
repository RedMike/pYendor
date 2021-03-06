from base import Entity
import ethereal, mobs, items, traps, obstacle


class Lookup:
    """Simple entity lookup class.

    Subclass and replace initialisation with own classes as needed.
    Actual entity management is done in EntityManager.
    """

    def __init__(self):
        self.lookup = dict()
        self.lookup['player_spawn'] = ethereal.PlayerSpawn
        self.lookup['camera'] = ethereal.Camera
        self.lookup['item'] = items.Item
        self.lookup['mob'] = mobs.Mob
        self.lookup['humanoid'] = mobs.Humanoid
        self.lookup['kobold'] = mobs.Mob
        self.lookup['player'] = mobs.Player
        self.lookup['ethereal'] = ethereal.Ethereal
        self.lookup['bodypart'] = ethereal.Bodypart
        self.lookup['wound'] = ethereal.Wound
        self.lookup['container'] = items.Container
        self.lookup['door'] = traps.Door
        self.lookup['obstacle'] = obstacle.Obstacle
        self.lookup['boulder'] = obstacle.Boulder
        self.lookup['glove'] = items.Glove
        self.lookup['breastplate'] = items.Breastplate
        self.lookup['sword'] = items.Sword
        self.lookup['backpack'] = items.Backpack


    def get_class(self,str):
        """Returns a class as associated by lookup."""
        return self.lookup.get(str.lower(), Entity)
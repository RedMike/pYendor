from data.entities import Entity

class Obstacle(Entity):
    """Base blocking, visible, non-liftable, non-usable entity for subclassing."""

    def init(self):
        super(Obstacle,self).init()
        self.set_attributes('01100')
        self.char = 'O'

class Boulder(Obstacle):
    pass
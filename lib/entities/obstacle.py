import entity

class Boulder(entity.Obstacle):

    def was_collided(self, id, type):
        if type == self.parent.ATTEMPTED_INTERACTION:
            ent = self.parent.get_ent(id)
            if isinstance(ent, entity.Mob):
                ent_pos = self.parent.get_pos(id)
                pos = self.parent.get_pos(self.id)
                dx, dy = pos[0] - ent_pos[0], pos[1] - ent_pos[1]
                self.parent.move_ent(self.id,dx,dy)
                return False
        return False
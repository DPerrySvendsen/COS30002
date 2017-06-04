from GameObject import *

class World:

    def __init__(self, width, height):

        self.width = width
        self.height = height

        self.game_objects = []
        self.mouse_position = Vector2D(0,0)

    # ---

    def update(self):

        for game_object in self.game_objects:
            game_object.update()

        # Remove inactive GameObjects
        self.game_objects = list(filter(lambda game_object: game_object.active, self.game_objects))

    # ---

    def draw(self):

        for game_object in self.game_objects:
            game_object.draw()

        graphics.white_pen()
        graphics.text_at_pos(10, 25, 'Predictive aiming ' + ('on' if Soldier.predictive_aiming else 'off'))
        graphics.text_at_pos(10, 10, 'Weapon: ' + Soldier.weapon)

    # ---

    def add(self, game_object):

        self.game_objects.append(game_object)
        game_object.world = self



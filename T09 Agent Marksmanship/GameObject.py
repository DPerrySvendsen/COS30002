from utils.vector2d import *
from utils.graphics import graphics, KEY
import time
import pygame
import random

# ---

class GameObject:

    def __init__(self, x, y):

        self.world = None
        self.active = True
        self.position = Vector2D(x,y)
        self.color = 'WHITE'
        self.radius = 5

        self.velocity = Vector2D()
        self.previous_position = self.position

    # ---

    def update(self):
        self.velocity = self.position - self.previous_position
        self.previous_position = self.position.copy()

    # ---

    def draw(self):

        graphics.set_pen_color(name = self.color)
        graphics.set_stroke(2)
        graphics.circle(self.position, self.radius)

# ---

class Soldier(GameObject):

    weapon = 'Rifle'
    predictive_aiming = True

    weapon_types = {
        KEY._1: 'Rifle',
        KEY._2: 'Rocket',
        KEY._3: 'Shotgun',
        KEY._4: 'Grenade'
    }

    weapon_cooldown = {
        'Rifle':   0.5,
        'Rocket':  2.0,
        'Shotgun': 1.0,
        'Grenade': 1.5
    }

    def __init__(self, x, y):
        GameObject.__init__(self, x, y)

        self.color = 'WHITE'
        self.radius = 15

        self.last_fired = time.time() - Soldier.weapon_cooldown[Soldier.weapon]

    # ---

    def update(self):

        if time.time() - self.last_fired > Soldier.weapon_cooldown[Soldier.weapon]:
            self.last_fired = time.time()
            enemies = list(filter(lambda game_object : isinstance(game_object, Enemy), self.world.game_objects))
            if not enemies:
                return
            target = min(enemies, key = lambda enemy : self.position.distance_sq(enemy.position))
            self.fire(target)

    # ---

    def get_predicted_position(self, enemy_position, enemy_velocity, projectile_speed):

        estimated_time = (enemy_position - self.position).length() / projectile_speed
        return enemy_position + enemy_velocity * estimated_time

    # ---

    def fire(self, enemy):

        target_position = enemy.position

        if Soldier.predictive_aiming:
            projectile_speed = 20 if self.weapon in ['Rifle', 'Shotgun'] else 10
            target_position = self.get_predicted_position(enemy.position, enemy.velocity, projectile_speed)

        if Soldier.weapon == 'Rifle':
            self.world.add(Bullet(self.position, target_position))

        elif Soldier.weapon == 'Rocket':
            self.world.add(Rocket(self.position, target_position))

        elif Soldier.weapon == 'Shotgun':
            for i in range(5):
                self.world.add(ShotgunShell(self.position, target_position))

        elif Soldier.weapon == 'Grenade':
            self.world.add(Grenade(self.position, target_position))

# ---

class Projectile(GameObject):

    def __init__(self, position, target_position):
        GameObject.__init__(self, position.x, position.y)
        self.direction = (target_position - position).normalise()
        self.speed = 5

    # ---

    def update(self):

        self.position += self.direction * self.speed
        if not pygame.Rect(0, 0, self.world.width, self.world.height).collidepoint(self.position.x, self.position.y):
            self.active = False
            return
        for enemy in list(filter(lambda game_object: isinstance(game_object, Enemy), self.world.game_objects)):
            if (self.position - enemy.position).length_sq() < pow(self.radius + enemy.radius, 2):
                self.active = False
                enemy.active = False
                return
        GameObject.update(self)

# ---

class Bullet(Projectile):

    def __init__(self, position, target_position):
        Projectile.__init__(self, position, target_position)

        self.color = 'GREY'
        self.radius = 5
        self.speed = 20

# ---

class Rocket(Projectile):

    def __init__(self, position, target_position):
        Projectile.__init__(self, position, target_position)

        self.color = 'ORANGE'
        self.radius = 10
        self.speed = 10

# ---

class ShotgunShell(Projectile):

    def __init__(self, position, target_position):
        target_position += Vector2D(
            random.randrange(-100, 100),
            random.randrange(-100, 100)
        )
        Projectile.__init__(self, position, target_position)

        self.color = 'GREY'
        self.radius = 5
        self.speed = random.randrange(18, 22)

# ---

class Grenade(Projectile):

    def __init__(self, position, target_position):
        target_position += Vector2D(
            random.randrange(-50, 50),
            random.randrange(-50, 50)
        )
        Projectile.__init__(self, position, target_position)

        self.color = 'GREEN'
        self.radius = 10
        self.speed = 10

# ---

class Enemy(GameObject):

    def __init__(self, x, y):
        GameObject.__init__(self, x, y)

        self.speed = 10

        self.color = 'RED'
        self.radius = 15

    # ---

    def update(self):
        if (self.world.mouse_position - self.position).length_sq() > pow(self.radius, 2):
            self.position += (self.world.mouse_position - self.position).normalise() * self.speed
        GameObject.update(self)








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

        self.speed = 3
        self.waypoints = [self.position.copy()]
        self.current_waypoint = 0

        self.last_fired = time.time()
        self.last_stopped = time.time()

        self.mode = 'Patrol'
        self.mode_attack = 'Shooting'
        self.mode_patrol = 'Walking'

    # ---

    def update(self):

        target = self.get_closest_enemy(300)

        if self.mode == 'Patrol' and target:
            self.mode = 'Attack'
            self.color = 'RED'
        elif self.mode == 'Attack' and not target:
            self.mode = 'Patrol'
            self.color = 'WHITE'

        if self.mode == 'Patrol':
            self.patrol()
        if self.mode == 'Attack':
            self.attack(target)

    # ---

    def draw(self):
        GameObject.draw(self)

        secondary_mode = self.mode_patrol if self.mode == 'Patrol' else self.mode_attack

        graphics.white_pen()
        graphics.text_at_pos(self.position.x - 20, self.position.y + 40, self.mode)
        graphics.text_at_pos(self.position.x - 20, self.position.y + 25, '(' + secondary_mode + ')')

    # ---

    def patrol(self):

        if self.mode_patrol == 'Stopped' and time.time() - self.last_stopped > 1:
            self.mode_patrol = 'Walking'

        if self.mode_patrol == 'Walking':
            direction = (self.waypoints[self.current_waypoint] - self.position).normalise()
            self.position += direction * self.speed

            if self.position.distance_sq(self.waypoints[self.current_waypoint]) < 25:
                self.next_waypoint()
                self.last_stopped = time.time()
                self.mode_patrol = 'Stopped'

    # ---

    def attack(self, target):

        if self.mode_attack == 'Reloading' and time.time() - self.last_fired > Soldier.weapon_cooldown[Soldier.weapon]:
            self.mode_attack = 'Shooting'

        if self.mode_attack == 'Shooting':

            if time.time() - self.last_fired > Soldier.weapon_cooldown[Soldier.weapon]:
                self.fire(target)
                self.last_fired = time.time()

            # I've added a slight delay here so that the Shooting state is visible, otherwise it will flip back
            # Shooting within the same frame
            if time.time() - self.last_fired > Soldier.weapon_cooldown[Soldier.weapon] / 2:
                self.mode_attack = 'Reloading'

    # ---

    def add_waypoint(self, x, y):

        self.waypoints.append(Vector2D(x,y))

    # ---

    def next_waypoint(self):

        self.current_waypoint += 1
        if self.current_waypoint >= len(self.waypoints):
            self.current_waypoint = 0

    # ---

    def get_closest_enemy(self, in_radius):

        enemies = list(filter(lambda game_object : isinstance(game_object, Enemy), self.world.game_objects))
        if not enemies:
            return None
        target = min(enemies, key = lambda enemy : self.position.distance_sq(enemy.position))
        if self.position.distance_sq(target.position) > pow(in_radius, 2):
            return None
        return target

    # ---

    def get_predicted_position(self, enemy_position, enemy_velocity, projectile_speed):

        estimated_time = (enemy_position - self.position).length() / projectile_speed
        return enemy_position + enemy_velocity * estimated_time

    # ---

    def fire(self, enemy):

        target_position = enemy.position.copy()

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








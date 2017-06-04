from graphics      import egi
from path          import Path
from pyglet.window import key
from random        import random, randrange, uniform
from vector2d      import Vector2D, Point2D
from math          import radians, sin, cos

# ---

AGENT_MODES = {
    key._1: 'Wander',
    key._2: 'Seek',
    key._3: 'Arrive',
    key._4: 'Flee',
    key._5: 'Follow path',
    key._6: 'Hide',
    key.F1: 'Weighted sum'
}

# ---

class Agent(object):

    def __init__(self, world=None, scale=30.0, mode='Weighted sum', is_hunter = False):
        self.world = world
        self.mode  = mode
        self.scale = scale

        self.position     = Vector2D(randrange(self.world.cx), randrange(self.world.cy))
        self.velocity     = Vector2D()
        self.acceleration = Vector2D()

        direction    = radians(random()*360)
        self.heading = Vector2D(sin(direction), cos(direction))
        self.side    = self.heading.perp()

        self.max_speed = self.scale * uniform(10,15)

        self.path = Path()
        self.randomise_path()

        self.waypoint_threshold = self.scale * 1
        self.panic_radius       = self.scale * 20

        self.wander_target   = Vector2D(1,0)
        self.wander_distance = self.scale * 10
        self.wander_radius   = self.scale * 2
        self.wander_jitter   = self.scale * 1

        self.local_group_radius    = self.scale * 3
        self.separation_multiplier = 0.2
        self.cohesion_multiplier   = 0.4
        self.alignment_multiplier  = 0.3

        self.color = 'ORANGE'
        self.vehicle_shape = [
            Point2D(-1.0,  0.6),
            Point2D( 1.0,  0.0),
            Point2D(-1.0, -0.6)
        ]

        self.is_hunter = is_hunter

        if self.is_hunter:
            self.max_speed = self.scale * 10
            self.color = 'RED'
            self.vehicle_shape = [
                Point2D(-2.0,  1.5),
                Point2D( 1.0,  0.0),
                Point2D(-2.0, -1.5),
                Point2D(-1.0,  0.0)
            ]

    # ---

    def render(self):
        egi.set_pen_color(name=self.color)
        points = self.world.transform_points(
            self.vehicle_shape,
            self.position,
            self.heading,
            self.side,
            Vector2D(self.scale, self.scale)
        )
        egi.closed_shape(points)

        #egi.red_pen()
        #egi.circle(self.position, self.panic_radius)

        if self.mode == 'Wander1': # Disabled for now

            local_position = Vector2D(self.wander_distance, 0)
            world_position = self.world.transform_point(
                local_position,
                self.position,
                self.heading,
                self.side
            )
            egi.green_pen()
            egi.circle(world_position, self.wander_radius)

            local_position += self.wander_target
            world_position = self.world.transform_point(
                local_position,
                self.position,
                self.heading,
                self.side
            )
            egi.red_pen()
            egi.circle(world_position, 5)

        elif self.mode == 'Follow path':
            self.path.render()

    # ---

    def update(self, delta):
        self.velocity += self.get_acceleration(delta)
        self.velocity.truncate(self.max_speed)
        if self.velocity.length_sq() > 0.01:
            self.heading = self.velocity.get_normalised()
            self.side    = self.heading.perp()
        self.position += self.velocity * delta
        self.world.wrap_around(self.position)

    # ---

    def get_acceleration(self, delta):
        # Returns the updated acceleration based on the current behaviour
        if self.mode == 'Wander':
            return self.wander(delta)
        elif self.mode == 'Seek':
            return self.seek(self.world.target)
        elif self.mode == 'Arrive':
            return self.arrive(self.world.target)
        elif self.mode == 'Flee':
            return self.flee(self.world.target)
        elif self.mode == 'Follow path':
            return self.follow_path()
        elif self.mode == 'Hide':
            return self.hide(self.world.hunter.position, delta)
        elif self.mode == 'Weighted sum':
            return self.weighted_sum(delta)
        else:
            return Vector2D()

    # ---

    def wander(self, delta):
        # Generate random jitter
        jitter = Vector2D(
            uniform(-1, 1) * self.wander_jitter * delta,
            uniform(-1, 1) * self.wander_jitter * delta
        )
        # Apply jitter to wander_target and map to circle
        self.wander_target = (self.wander_target + jitter).normalise() * self.wander_radius
        # Take a copy (important) and position ahead of agent
        wander_target_position = self.wander_target.copy()
        wander_target_position.x += self.wander_distance
        # Transform to world space
        world_target = self.world.transform_point(wander_target_position, self.position, self.heading, self.side)
        return self.seek(world_target)

    # ---

    def seek(self, target_position):
        # Move toward target_position
        desired_velocity = Vector2D()
        to_target = target_position - self.position
        if to_target.length() > self.waypoint_threshold:
            desired_velocity = to_target.normalise() * self.max_speed
        return desired_velocity - self.velocity

    # ---

    def arrive(self, target_position):
        # Move toward target position, slowing on arrival
        to_target = target_position - self.position
        deceleration_threshold = self.waypoint_threshold * 10
        if to_target.length() < deceleration_threshold:
            # Slow down depending on how close the agent is to target_position
            proximity_multiplier = to_target.length() / deceleration_threshold
            desired_velocity     = to_target.normalise() * self.max_speed * proximity_multiplier
            return desired_velocity - self.velocity
        else:
            return self.seek(target_position)

    # ---

    def flee(self, hunter_position):
        # Move away from hunter_position
        to_hunter = self.position - hunter_position
        if to_hunter.length() < self.panic_radius - self.scale:
            # Speed up depending on how close the agent is to hunter_position
            proximity_multiplier = (self.panic_radius - to_hunter.length()) / self.panic_radius
            desired_velocity     = to_hunter.normalise() * self.max_speed * proximity_multiplier
            return desired_velocity - self.velocity
        else:
            return Vector2D()

    # ---

    def follow_path(self):
        #
        if self.path.is_finished():
            return self.arrive(self.path.current_pt())
        else:
            if (self.path.current_pt() - self.position).length() < self.waypoint_threshold:
                self.path.inc_current_pt()
            return self.seek(self.path.current_pt())

    # ---

    def randomise_path(self):
        cx = self.world.cx
        cy = self.world.cy
        margin = min(cx, cy) * 0.2
        self.path.create_random_path(8, margin, margin, cx - margin, cy - margin)

    # ---

    def weighted_sum(self, delta):
        steering_force = Vector2D();
        local_group = self.get_local_group(self.local_group_radius)

        steering_force += self.separation_multiplier * self.separation(local_group)
        if steering_force.length() > self.max_speed:
            return steering_force

        steering_force += self.cohesion_multiplier * self.cohesion(local_group)
        if steering_force.length() > self.max_speed:
            return steering_force

        steering_force += self.alignment_multiplier * self.alignment(local_group)
        if steering_force.length() > self.max_speed:
            return steering_force

        steering_force += self.wander(delta)
        steering_force.truncate(self.max_speed)
        return steering_force

    # ---

    def get_local_group(self, radius):
        return list(filter(lambda agent : agent != self and (agent.position - self.position).length_sq() < radius * radius, self.world.agents))

    # ---

    def cohesion(self, local_group):
        # Move toward center of group
        centre_mass = Vector2D()
        for agent in local_group:
            centre_mass += agent.position
        if len(local_group) > 0:
            centre_mass /= len(local_group)
            return self.seek(centre_mass).normalise() * self.max_speed
        else:
            return Vector2D()

    # ---

    def separation(self, local_group):
        # Move a set distance away from other agents
        steering_force = Vector2D()
        for agent in local_group:
            to_agent = self.position - agent.position
            steering_force += to_agent.normalise() / to_agent.length()
        return steering_force * self.max_speed

    # ---

    def alignment(self, local_group):
        # Move in the same direction as other agents
        avg_heading = Vector2D()
        for agent in local_group:
            avg_heading += agent.heading
        if len(local_group) > 0:
            avg_heading /= len(local_group)
            return avg_heading.normalise() * self.max_speed
        else:
            return Vector2D()

    # ---

    def hide(self, hunter_position, delta):

        to_hunter = self.position - hunter_position
        if to_hunter.length() > self.panic_radius:
            return self.weighted_sum(delta)

        best_hiding_spot = None;
        best_hiding_distance = None;

        for object_position in self.world.objects:

            hiding_spot     = self.get_hiding_spot(hunter_position, Vector2D(object_position.x, object_position.y))
            hiding_distance = self.position.distance_sq(hiding_spot)
            if not best_hiding_spot or hiding_distance < best_hiding_distance:
                best_hiding_spot     = hiding_spot
                best_hiding_distance = hiding_distance

            egi.red_pen()
            egi.cross(hiding_spot, 10)

        if best_hiding_spot:
            return self.arrive(best_hiding_spot)

        return self.flee(hunter_position)

    # ---

    def get_hiding_spot(self, hunter_position, object_position):

        # temp
        radius = 50
        distance_from_boundary = 30

        distance = radius + distance_from_boundary

        return object_position + (object_position - hunter_position).normalise() * distance

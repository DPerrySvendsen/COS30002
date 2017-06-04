'''Autonomous Agent Movement: Seek, Arrive and Flee

Created for COS30002 AI for Games, Lab 05
By Clinton Woodward cwoodward@swin.edu.au

'''
from graphics import egi, KEY
from pyglet import window, clock
from pyglet.gl import *

from vector2d import Vector2D, Point2D
from world import World
from agent import Agent, AGENT_MODES  # Agent with seek, arrive, flee and pursuit


def on_mouse_motion(x, y, dx, dy):
    world.target = Vector2D(x, y)


def on_key_press(symbol, modifiers):
    if symbol == KEY.P:
        world.paused = not world.paused
    elif symbol == KEY.Z:
        for agent in world.agents:
            agent.randomise_path()
    elif symbol == KEY.ENTER:
        for i in range(10):
            world.agents.append(Agent(world))
    elif symbol in AGENT_MODES:
        for agent in world.agents:
            if not agent.is_hunter:
                agent.mode = AGENT_MODES[symbol]
    elif symbol in [KEY.Q, KEY.A, KEY.W, KEY.S, KEY.E, KEY.D, KEY.R, KEY.F]:
        for agent in world.agents:
            if symbol == KEY.Q:
                agent.local_group_radius += 5
            if symbol == KEY.A:
                agent.local_group_radius -= 5
            if symbol == KEY.W:
                agent.separation_multiplier += 0.1
            if symbol == KEY.S:
                agent.separation_multiplier -= 0.1
            if symbol == KEY.E:
                agent.cohesion_multiplier += 0.1
            if symbol == KEY.D:
                agent.cohesion_multiplier -= 0.1
            if symbol == KEY.R:
                agent.alignment_multiplier += 0.1
            if symbol == KEY.F:
                agent.alignment_multiplier -= 0.1


def on_resize(cx, cy):
    world.cx = cx
    world.cy = cy


if __name__ == '__main__':

    # create a pyglet window and set glOptions
    win = window.Window(fullscreen=True, vsync=True, resizable=True)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    # needed so that egi knows where to draw
    egi.InitWithPyglet(win)
    # prep the fps display
    fps_display = clock.ClockDisplay()
    # register key and mouse event handlers
    win.push_handlers(on_key_press)
    win.push_handlers(on_mouse_motion)
    win.push_handlers(on_resize)

    # Create the world
    world = World(500, 500)

    # Add the hunter
    world.hunter = Agent(world, 30, 'Wander', True)
    world.agents.append(world.hunter)

    # Add the objects
    world.objects = [
        Point2D( 500, 200),
        Point2D( 750, 300),
        Point2D(1280, 250),
        Point2D( 630, 650),
        Point2D(1600, 800),
        Point2D(1200, 500)
    ]

    # Add some agents
    for i in range(10):
        world.agents.append(Agent(world))

    # unpause the world ready for movement
    world.paused = False

    while not win.has_exit:
        win.dispatch_events()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # show nice FPS bottom right (default)
        delta = clock.tick()
        world.update(delta)
        world.render()
        fps_display.draw()
        # swap the double buffer
        win.flip()


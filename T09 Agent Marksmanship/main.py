from pyglet.gl import *
from GameObject import *
from World import World
from utils.graphics import KEY

# ---

world = World(1200, 800)
world.add(Soldier(600,400))
world.add(Enemy(800,700))

# ---

def on_key_press(symbol, modifiers):
    if symbol == KEY.SPACE:
        Soldier.predictive_aiming = not Soldier.predictive_aiming
    elif symbol in Soldier.weapon_types:
        Soldier.weapon = Soldier.weapon_types[symbol]

# ---

def on_mouse_motion(x, y, dx, dy):

    world.mouse_position = Vector2D(x, y)

# ---

def on_mouse_press(x, y, button, modifiers):

    world.add(Enemy(x,y))

# ---

window = pyglet.window.Window(
    width  = 1200,
    height = 800,
    vsync     = True,
    resizable = True
)

glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
graphics.InitWithPyglet(window)

window.push_handlers(on_key_press)
window.push_handlers(on_mouse_motion)
window.push_handlers(on_mouse_press)

while not window.has_exit:

    window.dispatch_events()
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    world.update()
    world.draw()
    window.flip()


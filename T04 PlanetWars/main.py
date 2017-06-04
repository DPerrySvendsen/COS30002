''' Deceptive PlanetWars Simulation

Created by Michale Jensen (2011) and Clinton Woodward (2012)
contact: cwoodward@swin.edu.au

Updated 2015
- Added pyglet graphics support
- Added bot order rules (removed order exploit bugs/features)
- Added multi-player support

'''

from planet_wars import PlanetWars

from pyglet import window, clock, app, resource, sprite
from pyglet.window import key
from pyglet.gl import *
from pyglet.text import Label

COLOR_NAMES = {
    'BLACK':  (0.0, 0.0, 0.0, 1),
    'WHITE':  (1.0, 1.0, 1.0, 1),
    'RED':    (1.0, 0.0, 0.0, 1),
    'GREEN':  (0.0, 1.0, 0.0, 1),
    'BLUE':   (0.0, 0.0, 1.0, 1),
    'GREY':   (0.6, 0.6, 0.6, 1),
    'PINK':   (1.0, 0.7, 0.7, 1),
    'YELLOW': (1.0, 1.0, 0.0, 1),
    'ORANGE': (1.0, 0.7, 0.0, 1),
    'PURPLE': (1.0, 0.0, 0.7, 1),
    'BROWN':  (0.5, 0.35, 0.0, 1),
    'AQUA':   (0.0, 1.0, 1.0, 1),
    'DARK_GREEN':  (0.0, 0.4, 0.0, 1),
    'LIGHT_BLUE':  (0.6, 0.6, 1.0, 1),
    'LIGHT_GREY':  (0.9, 0.9, 0.9, 1),
    'LIGHT_RED':   (1.0, 0.6, 0.6, 1),
    'LIGHT_GREEN': (0.6, 1.0, 0.6, 1),
}


def to_rgb(a_gl_color):
    return tuple([int(x * 255) for x in a_gl_color])

COLOR_NAMES_255 = {k: to_rgb(v) for k, v in COLOR_NAMES.items()}
1
GAME_SIZE = (500, 500)
SCREEN_SIZE = (3 * GAME_SIZE[0], GAME_SIZE[1])

COLOR = {
    0: COLOR_NAMES['LIGHT_GREY'],
    1: COLOR_NAMES['LIGHT_RED'],  # (255, 0, 0), # red
    2: COLOR_NAMES['LIGHT_BLUE'],  # (0, 0, 255), # blue
    3: COLOR_NAMES['LIGHT_GREEN'],  # (0, 255, 0), # green
}

# todo: these should be based on data, not magic ...
PLANET_MIN_R = 0.85
PLANET_FACTOR = 0.05

DISPLAY = True

IMAGES = {
    'background': 'images/space.jpg',
}


class ScreenPlanet(object):

    def __init__(self, pos, owner, radius, view_radius, color, label):
        self.pos = pos
        self.owner = owner
        self.owner = owner
        self.radius = radius
        self.view_radius = view_radius
        self.color = color
        self.label = label


class ScreenFleet(object):

    def __init__(self, pos, owner, radius, view_radius, color, label):
        self.pos = pos
        self.owner = owner
        self.radius = radius
        self.view_radius = view_radius
        self.color = color
        self.label = label


class PlanetWarsScreenAdapter(object):
    # handles drawing/cached pos/size of PlanetWars game instance for a GUI

    def __init__(self, game, circle=None, margin=20):
        self.game = game
        self.planets = {}
        self.fleets = {}
        self.margin = margin
        self.circle = circle

        # images
        self.bk_img = resource.image(IMAGES['background'])
        self.bk_sprite = sprite.Sprite(self.bk_img)

    def draw(self):
        # draw background
        #self.bk_sprite.draw()
        # draw planets
        for k, p in self.planets.items():
            self.circle(p.pos, p.radius, color=p.color, filled=True)
            self.circle(p.pos, p.radius, color=COLOR_NAMES['WHITE'], filled=False)
            if p.owner != 0:  # 0 == neutral_id
                self.circle(p.pos, p.view_radius, color=p.color, filled=False)
            p.label.draw()
        # draw fleets
        for k, f in self.fleets.items():
            # self.circle(f.pos, f.radius, color=COLOR_NAMES['YELLOW'], filled=False)
            self.circle(f.pos, f.radius, color=f.color, filled=False)
            f.label.draw()

    def screen_resize(self, width, height):
        # if the screen has been resized, update point conversion factors
        self.max_y, self.max_x, self.min_y, self.min_x = self.game.extent
        # get game width and height
        self.dx = abs(self.max_x - self.min_x)
        self.dy = abs(self.max_y - self.min_y)
        # set display box width and height
        self.display_dx = width - self.margin * 2
        self.display_dy = height - self.margin * 2
        # get the smaller ratio (width height) for radius drawing
        self.ratio = min(self.display_dx / self.dx, self.display_dy / self.dy)

        # resize the background image also
        self.bk_img.width = width
        self.bk_img.height = height
        self.bk_sprite = sprite.Sprite(self.bk_img)

    def sync_all(self, view_id=0, label_type='num_ships'):
        # todo: only need to update label values and owner colour details of planets
        # recache all planets/fleets
        if view_id is 0:
            planets = self.game.planets
            fleets = self.game.fleets
        else:
            planets = self.game.players[view_id].planets
            fleets = self.game.players[view_id].fleets

        # Set which label_type detail to show (id, num_ships, vision etc)
        for k, p in planets.items():
            self.planets[k] = self._planet_stamp(p, p.__getattribute__(label_type))

        self.fleets.clear()
        for k, f in fleets.items():
            self.fleets[k] = self._fleet_stamp(f, f.num_ships)

    def _planet_stamp(self, planet, value):
        pos = self.game_to_screen(planet.x, planet.y)
        radius = (self.ratio * PLANET_MIN_R) + ((PLANET_FACTOR * self.ratio) * planet.growth_rate)
        view_radius = planet.vision_range() * self.ratio
        color = COLOR[planet.owner_id]
        label = Label(str(value), color=COLOR_NAMES_255['BLACK'],
                      x=pos[0], y=pos[1], anchor_x='center', anchor_y='center')
        return ScreenPlanet(pos, planet.owner_id, radius, view_radius, color, label)

    def _fleet_stamp(self, fleet, value):
        pos = self.game_to_screen(fleet.x, fleet.y)
        radius = 20.0
        view_radius = fleet.vision_range() * self.ratio
        color = COLOR[fleet.owner_id]
        label = Label(str(value), color=COLOR_NAMES_255['WHITE'],
                      x=pos[0], y=pos[1], anchor_x='center', anchor_y='center')
        return ScreenFleet(pos, fleet.owner_id, radius, view_radius, color, label)

    def game_to_screen(self, wx, wy):
        # convert xy values from game space to screen space
        x = ((wx - self.min_x) / self.dx) * self.display_dx + self.margin
        y = ((wy - self.min_y) / self.dy) * self.display_dy + self.margin
        return (x, y)


class PlanetWarsWindow(window.Window):

    def __init__(self, **kwargs):
        # rip out the game settings we want
        players = kwargs.pop('players')
        gamestate = kwargs.pop('gamestate')
        self.game = PlanetWars(gamestate)
        for p in players:
            self.game.add_player(p)
        self.max_tick = kwargs.pop('max_game_length')

        # set and use pyglet window settings
        kwargs.update({
            'width': 500,
            'height': 500,
            'vsync': True,
            'resizable': False,
        })
        super(PlanetWarsWindow, self).__init__(**kwargs)
        # create a pyglet window and set glOptions
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glClearColor(0., 0., 0., 1.0)  # Grey

        # current "pen" colour of lines
        self.pen_color = (1, 0, 0, 1.)
        self.stroke = 1.0  # - thickness default
        self.qobj = gluNewQuadric()
        # gluQuadricDrawStyle(self.qobj, GLU_FILL) #GLU_SILHOUETTE)

        # prep the fps display and some labels
        self.fps_display = clock.ClockDisplay()
        clWhite = (255, 255, 255, 255)
        self.step_label = Label('STEP', x=5, y=self.height - 20, color=clWhite)
        self.fps = 0
        self.set_fps(20)
        self.paused = True
        self.view_id = 0
        self.label_type = 'num_ships'

        # create adaptor to help with drawing
        self.adaptor = PlanetWarsScreenAdapter(self.game, self.circle)

        # prep the game (space!)
        self.reset_space()
        # add extra event handlers we need
        self.add_handlers()

    def reset_space(self):
        self.adaptor.screen_resize(self.width, self.height)
        self.adaptor.sync_all(self.view_id, self.label_type)

    def set_fps(self, fps):
        self.fps = max(fps, 5)
        clock.unschedule(self.update)
        clock.schedule_interval(self.update, 1.0 / self.fps)

    def update(self, args):
        # gets called by the scheduler at the step_fps interval set
        game = self.game
        if game:
            if not self.paused:
                game.update()
                self.adaptor.sync_all()

            # update step label
            msg = 'Step:' + str(game.tick)
            if self.paused:
                msg += ' [PAUSED]'
            msg += ', View:' + str(self.view_id)
            if self.view_id in game.players:
                msg += ' ' + game.players[self.view_id].name
            elif self.view_id == 0:
                msg += ' All '
            msg += str(game.tick)
            msg += ' Show: ' + self.label_type

            self.step_label.text = msg
            # Has the game ended? (Should we close?)
            if not self.game.is_alive() or self.game.tick >= self.max_tick:
                self.close()
        else:
            self.step_label.text = "---"

    def add_handlers(self):
        @self.event
        def on_resize(cx, cy):
            self.adaptor.screen_resize(cx, cy)
            pass

        @self.event
        def on_mouse_press(x, y, button, modifiers):
            pass

        @self.event
        def on_key_press(symbol, modifiers):
            # Single Player View, or All View
            if symbol == key.BRACKETLEFT:
                self.view_id = self.view_id - 1 if self.view_id > 1 else len(self.game.players)
            if symbol == key.BRACKETRIGHT:
                self.view_id = self.view_id + 1 if self.view_id < len(self.game.players) else 1
            # Everyone view
            elif symbol == key.A:
                self.view_id = 0 # == "all"
            # Planet attribute type to show?
            elif symbol == key.L:
                i = self.label_type
                l = ['id','num_ships','vision_age','owner_id']
                self.label_type = l[l.index(i)+1] if l.index(i) < (len(l)-1) else l[0]
            # Reset?
            elif symbol == key.R:
                self.reset_space()
            # Do one step
            elif symbol == key.N:
                self.game.update()
            # Pause toggle?
            elif symbol == key.P:
                self.paused = not self.paused
            # Speed up (+) or slow down (-) the sim
            elif symbol in [key.PLUS, key.EQUAL]:
                self.set_fps(self.fps + 5)
            elif symbol == key.MINUS:
                self.set_fps(self.fps - 5)

            self.adaptor.sync_all(self.view_id, self.label_type)

        @self.event
        def on_draw():
            self.clear()
            self.fps_display.draw()
            self.step_label.draw()
            self.adaptor.draw()

    def set_pen_color(self, color=None, name=None):
        if name is not None:
            color = COLOR_NAMES[name]
        self.curr_color = color
        glColor4f(*self.curr_color)

    def set_stroke(self, stroke):
        self.stroke = stroke
        glLineWidth(self.stroke)

    def circle(self, pos, radius, color=None, filled=True):
        if color:
            self.set_pen_color(color)
        if filled:
            gluQuadricDrawStyle(self.qobj, GLU_FILL)
        else:
            gluQuadricDrawStyle(self.qobj, GLU_SILHOUETTE)
        glPushMatrix()
        glTranslatef(pos[0], pos[1], 0.0)
        gluDisk(self.qobj, 0, radius, 32, 1)
        glPopMatrix()

    def line(self, x1=0, y1=0, x2=0, y2=0, pos1=None, pos2=None):
        ''' Draw a single line. Either with xy values, or two position (that
            contain x and y values). Uses existing colour and stroke values. '''
        if pos1 is not None and pos2 is not None:
            x1, y1, x2, y2 = pos1[0], pos1[1], pos2[0], pos2[1]
        glBegin(GL_LINES)
        glVertex2f(x1, y1)
        glVertex2f(x2, y2)
        glEnd()


if __name__ == '__main__':
    gamestate = open('./maps/map5.txt').read()
             #[Red,Blue]
    players = ['TestBot2', 'TestBot']
    window = PlanetWarsWindow(gamestate=gamestate, players=players, max_game_length=500)
    app.run()
    window.game.logger.flush()

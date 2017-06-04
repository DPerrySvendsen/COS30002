from graphics import graphics
from pyglet.window import key
from pyglet.gl import *
from pyglet.text import Label
from box_world import BoxWorld, search_modes, display_settings
import time
from math import hypot

# ---

class BoxWorldWindow(pyglet.window.Window):

    mouse_modes = {
        key._1: 'clear',
        key._2: 'mud',
        key._3: 'water',
        key._4: 'wall',
        key._5: 'start',
        key._6: 'target',
    }
    mouse_mode = 'target'

    # search mode cycles through the search algorithm used by box_world
    search_mode = 0

    # ---

    def __init__(self, filename, **kwargs):
        
        kwargs.update({
            'width':  500,
            'height': 500,
            'vsync':     True,
            'resizable': True,
        })
        super(BoxWorldWindow, self).__init__(**kwargs)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        graphics.InitWithPyglet(self)
        graphics.text_color(name='BLACK')

        glClearColor(0.9, 0.9, 0.9, 1.0) # Grey

        self.world = BoxWorld.FromFile(filename, self.get_size())
        self.world.reset_navgraph()

        # prep the fps display and some labels
        self.fps_display = None
        colour_black = (0,0,0, 255)
        self.labels = {
            'mouse':  Label('', x=5,   y=self.height-20, color=colour_black),
            'search': Label('', x=120, y=self.height-20, color=colour_black),
            'status': Label('', x=300, y=self.height-20, color=colour_black),
        }
        self._update_label()

        self.add_handlers()

        self.limit = 0 # Unlimited

    # ---
    
    def _update_label(self, key=None, text='---'):
        
        if key == 'mouse' or key is None:
            self.labels['mouse'].text = 'Kind: '+self.mouse_mode
        if key == 'search' or key is None:
            self.labels['search'].text = 'Search: '+ search_modes[self.search_mode]
        if key == 'status' or key is None:
            self.labels['status'].text = 'Status: '+ text

    # ---

    def add_handlers(self):

        @self.event
        def on_resize(cx, cy):
            self.world.resize(cx, cy-25)
            # reposition the labels.
            for key, label in list(self.labels.items()):
                label.y = cy-20

        @self.event
        def on_mouse_press(x, y, button, modifiers):
            if button == 1: # left
                box = self.world.get_box_by_pos(x,y)
                if box:
                    if self.mouse_mode == 'start':
                        self.world.set_start(box.node.idx)
                    elif self.mouse_mode == 'target':
                        if self.world.boxes[box.node.idx].marker == 'T':
                            self.world.unset_target(box.node.idx)
                        else:
                            self.world.set_target(box.node.idx)
                        # A* (3) for one target, Dijkstra (2) for multiple targets
                        self.search_mode = 3 if len(self.world.targets) == 1 else 2
                    else:
                        box.set_kind(self.mouse_mode)
                    self.world.reset_navgraph()
                    self._update_label('search')
                    self.plan_path()
                    self._update_label('status','graph changed')


        @self.event
        def on_key_press(symbol, modifiers):
            # mode change?
            if symbol in self.mouse_modes:
                self.mouse_mode = self.mouse_modes[symbol]
                self._update_label('mouse')

            # Change search mode? (Algorithm)
            elif symbol == key.M:
                self.search_mode += 1
                if self.search_mode >= len(search_modes):
                    self.search_mode = 0
            elif symbol == key.N:
                self.search_mode -= 1
                if self.search_mode < 0:
                    self.search_mode = len(search_modes)-1
                self._update_label('search')
                self.plan_path()
            # Plan a path using the current search mode?
            elif symbol == key.SPACE:
                self.plan_path()
            elif symbol == key.E:
                display_settings['EDGES_ON'] = not display_settings['EDGES_ON']
            elif symbol == key.L:
                display_settings['LABELS_ON'] = not display_settings['LABELS_ON']
            elif symbol == key.C:
                display_settings['CENTER_ON'] = not display_settings['CENTER_ON']
            elif symbol == key.B:
                display_settings['BOXLINES_ON'] = not display_settings['BOXLINES_ON']
            elif symbol == key.U:
                display_settings['BOXUSED_ON'] = not display_settings['BOXUSED_ON']
            elif symbol == key.P:
                display_settings['PATH_ON'] = not display_settings['PATH_ON']
            elif symbol == key.T:
                display_settings['TREE_ON'] = not display_settings['TREE_ON']

            elif symbol == key.UP:
                self.limit += 1
                self.plan_path()
                self._update_label('status', 'limit=%d' % self.limit)
            elif symbol == key.DOWN:
                if self.limit-1 > 0:
                    self.limit -= 1
                    self.plan_path()
                    self._update_label('status', 'limit=%d' % self.limit)
            elif symbol == key._0:
                self.limit = 0
                self.plan_path()
                self._update_label('status', 'limit=%d' % self.limit)

    # ---

    def dist(self, a, b):
        return abs(hypot(a.x - b.x, a.y - b.y))

    # ---

    def redraw(self):
        self.clear()
        self.on_draw()
        self.flip()
        time.sleep(0.01)

    # ---

    def plan_path(self):
        self.world.plan_path(search_modes[self.search_mode], self.limit)
        self._update_label('status', 'path planned')
        print(self.world.path.report(0))

        if self.world.path:
            for rt_idx in self.world.path.path:
                offset = 8
                target_position = self.world.get_box_by_idx(rt_idx)._vc
                while self.dist(self.world.agent_position, target_position) > offset * 2:
                    if self.world.agent_position.x > target_position.x + offset:
                        self.world.agent_position.x -= offset
                    elif self.world.agent_position.x < target_position.x - offset:
                        self.world.agent_position.x += offset
                    if self.world.agent_position.y > target_position.y + offset:
                        self.world.agent_position.y -= offset
                    elif self.world.agent_position.y < target_position.y - offset:
                        self.world.agent_position.y += offset
                    self.redraw()

    # ---

    def on_draw(self):
        self.clear()
        self.world.draw()
        if self.fps_display:
            self.fps_display.draw()
        for key, label in list(self.labels.items()):
            label.draw()

# ---

if __name__ == '__main__':

    import sys
    window = BoxWorldWindow(sys.argv[1] if len(sys.argv) > 1 else 'map1.txt')
    pyglet.app.run()


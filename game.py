#!/usr/bin/env python
from cocos.director import director
from cocos.layer import Layer, ColorLayer
from cocos.scene import Scene
import pyglet
from pyglet.window import key
import pymunk
from pymunk.pygame_util import draw
from models import Player

__author__ = 'aikikode'


class Game(Layer):
    is_event_handler = True  # enable pyglet's events

    def __init__(self):
        super(Game, self).__init__()
        self.width, self.height = director.get_window_size()
        self.space = pymunk.Space()
        self.space.gravity = (0.0, -900.0)
        #
        cl = ColorLayer(112, 66, 20, 50, width=self.width, height=self.height)
        self.add(cl, z=-1)
        #
        self.create_container()
        self.model = Player((150, 700))
        self.space.add(self.model.body, self.model.shape)
        self.add(self.model.image)
        self.schedule(self.update)

    def create_container(self):
        space = self.space
        ss = [
            pymunk.Segment(space.static_body, (0, 0), (self.width, 0), 5),
            pymunk.Segment(space.static_body, (self.width, 0), (self.width, max(self.height * 10, 1000)), 5),
            pymunk.Segment(space.static_body, (0, 0), (0, max(self.height * 10, 1000)), 5)
        ]
        for s in ss:
            s.elasticity = 0.95
        self.space.add(ss)

    def update(self, dt):
        dt = 1.0 / 100.
        self.space.step(dt)
        self.model.update(dt)

    def on_key_press(self, k, m):
        if k in (key.LEFT, key.RIGHT, key.SPACE):
            if k == key.LEFT:
                pass
                #self.model.block_left()
            elif k == key.RIGHT:
                pass
            elif k == key.SPACE:
                pass
        return False


def get_new_game():
    scene = Scene()
    game = Game()
    scene.add(game, z=0, name="game layer")
    return scene

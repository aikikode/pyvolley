#!/usr/bin/env python
from cocos.director import director
from cocos.layer import Layer
from cocos.text import Label

__author__ = 'aikikode'


class Hud(Layer):
    def __init__(self):
        super(Hud, self).__init__()
        self.width, self.height = director.get_window_size()
        self.player_1_score = Label(text="0", position=((10, self.height - 40)))
        self.player_2_score = Label(text="0", position=((self.width - 40, self.height - 40)), anchor_x="right")
        self.add(self.player_1_score)
        self.add(self.player_2_score)

#!/usr/bin/env python
import cocos
import pymunk

__author__ = 'aikikode'


class Player(object):
    def __init__(self, pos):
        head_mass = 10
        self.head_radius = head_radius = 25
        #body_mass = 20
        #body_radius = 35
        inertia = pymunk.moment_for_circle(head_mass, 0, head_radius, (0, 0))
                  #pymunk.moment_for_circle(body_mass, 0, body_radius, (0, 0))
        self.body = pymunk.Body(head_mass, inertia)
        self.body.position = pos
        head_shape = pymunk.Circle(self.body, self.head_radius, (0, 0))
        head_shape.elasticity = 0.9
        self.shape = head_shape
        self.image = cocos.sprite.Sprite('data/images/ball.png')
        self.image.position = pos

    def update(self, dt):
        self.image.position = self.body.position

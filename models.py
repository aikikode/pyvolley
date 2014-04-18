#!/usr/bin/env python
import cocos
import pyglet
import pymunk
import constants

__author__ = 'aikikode'

pyglet.resource.path = [constants.IMAGES_RESOURCE]
pyglet.resource.reindex()


class Ball(object):
    def __init__(self, pos):
        self.mass = mass = 100
        self.radius = radius = 50
        inertia = pymunk.moment_for_circle(mass, 0, radius, (0, 0))
        self.body = pymunk.Body(mass, inertia)
        self.body.position = pos
        self.body.velocity_limit = 1000
        shape = pymunk.Circle(self.body, self.radius, (0, 0))
        shape.elasticity = 0.9
        shape.friction = 0.9
        shape.collision_type = 0
        self.shape = shape
        self.sprite = cocos.sprite.Sprite('volleyball.png')
        self.sprite.scale = 5/6.
        self.sprite.position = pos

    def update(self, dt):
        self.sprite.position = self.body.position


class Player(object):
    def __init__(self, pos, image):
        self.head_radius = 45
        self.body_radius = 60
        self.body = pymunk.Body(100000, pymunk.inf)
        self.body.position = pos
        self.body.velocity_limit = 900
        head_shape = pymunk.Circle(self.body, self.head_radius, (0, 45))
        head_shape.layers = 0b001
        head_shape.collision_type = 1
        head_shape.elasticity = 0.95
        self.head_shape = head_shape
        body_shape = pymunk.Circle(self.body, self.body_radius, (0, -30))
        body_shape.layers = 0b100
        body_shape.elasticity = 0.95
        body_shape.collision_type = 1
        self.body_shape = body_shape
        self.sprite = cocos.sprite.Sprite(image)
        self.sprite.position = pos

    def update(self, dt):
        self.sprite.position = self.body.position
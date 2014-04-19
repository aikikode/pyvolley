#!/usr/bin/env python
import cocos
import math
import pyglet
import pymunk
import constants

__author__ = 'aikikode'

pyglet.resource.path = [constants.IMAGES_RESOURCE]
pyglet.resource.reindex()


class Ball(object):
    def __init__(self, pos):
        self.mass = mass = constants.BALL_MASS
        self.radius = radius = constants.BALL_RADIUS
        inertia = pymunk.moment_for_circle(mass, 0, radius, (0, 0))
        self.body = pymunk.Body(mass, inertia)
        self.body.position = pos
        self.body.velocity_limit = constants.BALL_VELOCITY_LIMIT
        self.body.apply_force(constants.BALL_ADDITIONAL_FORCE)
        shape = pymunk.Circle(self.body, self.radius, (0, 0))
        shape.elasticity = 0.95
        shape.friction = 0.9
        shape.collision_type = 0
        self.shape = shape
        self.sprite = cocos.sprite.Sprite('volleyball.png')
        self.sprite.scale = 5/6.
        self.sprite.position = pos
        self.indicator = cocos.sprite.Sprite('ball_indicator.png')
        self.indicator.position = (pos[0], 0)

    def set_indicator_height(self, height):
        self.indicator.position = (self.indicator.position[0], height)

    def update(self, dt):
        self.sprite.position = self.body.position
        self.sprite.rotation = -self.body.angle * 180. / math.pi
        self.indicator.position = (self.sprite.position[0], self.indicator.position[1])


class Player(object):
    def __init__(self, pos, image):
        self.head_radius = 45
        self.body_radius = 60
        self.body = pymunk.Body(constants.PLAYER_MASS, pymunk.inf)
        self.body.position = pos
        self.body.apply_force(constants.PLAYER_ADDITIONAL_FORCE)
        head_shape = pymunk.Circle(self.body, self.head_radius, (0, 45))
        head_shape.layers = 0b001
        head_shape.collision_type = 1
        head_shape.elasticity = 0.99
        head_shape.friction = 0.8
        self.head_shape = head_shape
        body_shape = pymunk.Circle(self.body, self.body_radius, (0, -30))
        body_shape.layers = 0b100
        body_shape.elasticity = 0.99
        body_shape.collision_type = 1
        body_shape.friction = 0.9
        self.body_shape = body_shape
        self.sprite = cocos.sprite.Sprite(image)
        self.sprite.position = pos

    def update(self, dt):
        self.sprite.position = self.body.position

    def move_left(self, speed=constants.PLAYER_SPEED):
        self.body.velocity.x = -speed
        self.body_shape.friction = 0

    def move_right(self, speed=constants.PLAYER_SPEED):
        self.body.velocity.x = speed
        self.body_shape.friction = 0

    def jump(self, speed=constants.PLAYER_JUMP_SPEED):
        if self.body.position[1] <= 90 + 20:
            self.body.velocity.y = speed

    def stop(self):
        self.body.velocity.x = 0
        self.body_shape.friction = 1

    def reset(self, pos):
        self.body.position = pos
        self.body.velocity = ((0, 0))
        self.body.reset_forces()
        self.body.apply_force(constants.PLAYER_ADDITIONAL_FORCE)

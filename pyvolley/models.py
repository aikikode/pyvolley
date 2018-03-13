#!/usr/bin/env python
import math

import cocos
import pymunk

import constants

__author__ = 'aikikode'


class Ball(object):
    def __init__(self, pos):
        self.mass = mass = constants.BALL_MASS
        self.radius = radius = constants.BALL_RADIUS
        inertia = pymunk.moment_for_circle(mass, 0, radius, (0, 0))
        self.body = pymunk.Body(mass, inertia)
        self.body.position = pos
        self.body.velocity_limit = constants.BALL_VELOCITY_LIMIT
        self.body.apply_force_at_local_point(
            constants.BALL_ADDITIONAL_FORCE, (0, 0)
        )
        shape = pymunk.Circle(self.body, self.radius, (0, 0))
        shape.elasticity = 0.99
        shape.friction = 0.9
        shape.collision_type = 0
        self.shape = shape
        self.sprite = cocos.sprite.Sprite('volleyball.png')
        self.sprite.scale = 5 / 6.
        self.sprite.position = pos
        self.shadow_sprite = cocos.sprite.Sprite('ball_shadow.png')
        self.shadow_sprite.position = (pos[0] + (pos[1] - constants.GROUND_OFFSET) / 1.5, constants.GROUND_OFFSET)
        self.indicator = cocos.sprite.Sprite('ball_indicator.png')
        self.indicator.position = (pos[0], 0)

    def set_indicator_height(self, height):
        self.indicator.position = (self.indicator.position[0], height)

    def update(self, dt):
        self.sprite.position = pos = self.body.position
        self.shadow_sprite.position = (pos[0] + (pos[1] - constants.GROUND_OFFSET) / 1.5, constants.GROUND_OFFSET)
        self.sprite.rotation = -self.body.angle * 180. / math.pi
        self.indicator.position = (self.sprite.position[0], self.indicator.position[1])


class Player(object):
    def __init__(self, pos, image):
        self.head_radius = 45
        self.body_radius = 60

        # Use inf inertia to prevent player head from falling to the ground
        self.body = pymunk.Body(constants.PLAYER_MASS, pymunk.inf)
        self.body.position = pos
        self.body.apply_force_at_local_point(
            constants.PLAYER_ADDITIONAL_FORCE, (0, 0)
        )
        head_shape = pymunk.Circle(self.body, self.head_radius, (0, 45))
        # Use layers to prevent body and head collision
        head_shape.layers = 0b001
        head_shape.collision_type = 1
        head_shape.elasticity = 2  # >1 to increase ball speed on impact
        head_shape.friction = 0.8
        self.head_shape = head_shape
        body_shape = pymunk.Circle(self.body, self.body_radius, (0, -30))
        body_shape.layers = 0b100
        body_shape.elasticity = 2  # >1 to increase ball speed on impact
        body_shape.collision_type = 1
        body_shape.friction = 0.9
        self.body_shape = body_shape
        self.sprite = cocos.sprite.Sprite(image)
        self.sprite.position = pos
        self.shadow_sprite = cocos.sprite.Sprite('player_shadow.png')
        self.shadow_sprite.position = (pos[0] + (pos[1] - constants.GROUND_OFFSET) / 1.5, constants.GROUND_OFFSET)
        self._is_jumping = False

    def update(self, dt):
        self.sprite.position = pos = self.body.position
        self.shadow_sprite.position = (pos[0] + (pos[1] - constants.GROUND_OFFSET) / 1.5, constants.GROUND_OFFSET)
        if self._is_jumping:
            self.jump()

    def move_left(self, speed=constants.PLAYER_SPEED):
        self.body.velocity.x = -speed
        self.body_shape.friction = 0

    def move_right(self, speed=constants.PLAYER_SPEED):
        self.body.velocity.x = speed
        self.body_shape.friction = 0

    def start_jumping(self):
        self._is_jumping = True

    def stop_jumping(self):
        self._is_jumping = False

    def jump(self, speed=constants.PLAYER_JUMP_SPEED):
        if self.body.position[1] <= 90 + constants.GROUND_OFFSET:
            self.body.velocity.y = speed

    def stop(self):
        self.body.velocity.x = 0
        self.body_shape.friction = 1

    def reset(self, pos):
        self.body.position = pos
        self.body.velocity = (0, 0)
        self.body.force = (0, 0)
        self.body.apply_force_at_local_point(
            constants.PLAYER_ADDITIONAL_FORCE, (0, 0)
        )

#!/usr/bin/env python
from cocos.director import director, cocos
from cocos.layer import Layer, ColorLayer
from cocos.scene import Scene
from pyglet.window import key, pyglet
import pymunk
import constants
from hud import Hud
from models import Ball, Player

__author__ = 'aikikode'

pyglet.resource.path = [constants.IMAGES_RESOURCE]
pyglet.resource.reindex()

SPEED = 800
JUMP_SPEED = 900


class Game(Layer):
    is_event_handler = True  # enable pyglet's events

    def __init__(self):
        super(Game, self).__init__()
        self.width, self.height = director.get_window_size()
        self.space = pymunk.Space()
        self.space.gravity = (0.0, -900.0)
        # Background image
        bg = cocos.sprite.Sprite('background.png')
        bg.position = (self.width / 2., self.height / 2.)
        self.add(bg, z=-1)
        #
        self.create_container()
        # Add ball
        self.ball = Ball((self.width / 4., 400))
        self.space.add(self.ball.body, self.ball.shape)
        self.add(self.ball.sprite)
        self.ball.body.sleep()
        # Add player 1
        self.player_1 = Player((200, 176/2), "player_1.png")
        self.space.add(self.player_1.body, self.player_1.body_shape, self.player_1.head_shape)
        self.add(self.player_1.sprite)
        # Add player 2
        self.player_2 = Player((self.width - 200, 176/2), "player_2.png")
        self.space.add(self.player_2.body, self.player_2.body_shape, self.player_2.head_shape)
        self.add(self.player_2.sprite)
        #
        self.schedule(self.update)
        self.space.add_collision_handler(1, 2, begin=self.on_player_hits_wall, post_solve=self.on_player_hits_wall)
        self.space.add_collision_handler(1, 4, begin=self.on_player_hits_wall, post_solve=self.on_player_hits_wall)
        self.space.add_collision_handler(1, 3, begin=self.on_player_hits_ground, post_solve=self.on_player_hits_ground)
        self.space.add_collision_handler(0, 1, begin=self.on_player_hits_ball)
        self.space.add_collision_handler(0, 4, begin=lambda x, y: False)
        self.space.add_collision_handler(0, 3, begin=self.on_ball_hits_ground)
        self.game_active = True

    def reset_ball(self, player):
        if player == self.player_1:
            #self.ball.body.reset_forces()
            #self.ball.body.velocity = (0, 0)
            self.ball.body.position = ((self.width / 4., 400))
            self.ball.body.sleep()
        elif player == self.player_2:
            #self.ball.body.reset_forces()
            #self.ball.body.velocity = (0, 0)
            self.ball.body.position = ((3 * self.width / 4., 400))
            self.ball.body.sleep()
        self.game_active = True

    def on_player_hits_wall(self, space, arbiter):
        if arbiter.shapes[0] in [self.player_1.body_shape, self.player_1.head_shape]:
            self.player_1.body.velocity.x = 0
        elif arbiter.shapes[0] in [self.player_2.body_shape, self.player_2.head_shape]:
            self.player_2.body.velocity.x = 0
        return True

    def on_player_hits_ground(self, space, arbiter):
        if arbiter.shapes[0] in [self.player_1.body_shape]:
            self.player_1.body.velocity.y = 0
        elif arbiter.shapes[0] in [self.player_2.body_shape]:
            self.player_2.body.velocity.y = 0
        return True

    def on_player_hits_ball(self, space, arbiter):
        if self.ball.body.is_sleeping:
            self.ball.body.activate()
        return True

    def on_ball_hits_ground(self, space, arbiter):
        self.game_active = False
        return True

    def create_container(self):
        space = self.space
        # Add left and right screen borders
        ss = [
            pymunk.Segment(space.static_body, (self.width, 0), (self.width, max(self.height * 10, 1000)), 5),
            pymunk.Segment(space.static_body, (0, 0), (0, max(self.height * 10, 1000)), 5)
        ]
        for s in ss:
            s.elasticity = 0.95
            s.collision_type = 2
        space.add(ss)
        # Add ground
        ground = pymunk.Segment(space.static_body, (0, 0), (self.width, 0), 5)
        ground.elasticity = 0.5
        ground.collision_type = 3
        ground.friction = 0.99
        space.add(ground)
        # Add net
        net = pymunk.Segment(space.static_body, (self.width / 2., 0), (self.width / 2., 400), 5)
        net.elasticity = 0.95
        net.collision_type = 2
        space.add(net)
        net_sprite = cocos.sprite.Sprite('net.png')
        net_sprite.position = (self.width / 2., 200)
        self.add(net_sprite)
        # Add virtual net to prevent players from jumping to each other field
        virtual_net = pymunk.Segment(space.static_body, (self.width / 2., 0), (self.width / 2., max(self.height * 10, 1000)), 5)
        virtual_net.elasticity = 0.95
        virtual_net.collision_type = 4
        space.add(virtual_net)

    def update(self, dt):
        dt = 1.0 / 80.
        self.space.step(dt)
        self.ball.update(dt)
        self.player_1.update(dt)
        self.player_2.update(dt)
        if not self.game_active and self.ball.body.velocity.y <= 5:
            if self.ball.body.position[0] <= self.width / 2.:
                self.reset_ball(self.player_2)
            else:
                self.reset_ball(self.player_1)

    def on_key_press(self, k, m):
        if self.game_active:
            if k in (key.LEFT, key.RIGHT, key.UP):
                if k == key.LEFT:
                    self.player_2.body.velocity.x = -SPEED
                elif k == key.RIGHT:
                    self.player_2.body.velocity.x = SPEED
                elif k == key.UP:
                    if self.player_2.body.position[1] <= 95:
                        self.player_2.body.velocity.y = JUMP_SPEED
            elif k in (key.A, key.D, key.W):
                if k == key.A:
                    self.player_1.body.velocity.x = -SPEED
                elif k == key.D:
                    self.player_1.body.velocity.x = SPEED
                elif k == key.W:
                    if self.player_1.body.position[1] <= 95:
                        self.player_1.body.velocity.y = JUMP_SPEED
        return False

    def on_key_release(self, k, m):
        if k in (key.LEFT, key.RIGHT, key.UP):
            if k == key.LEFT or k == key.RIGHT:
                self.player_2.body.velocity.x = 0
            elif k == key.UP:
                pass
        elif k in (key.A, key.D, key.W):
            if k == key.A or k == key.D:
                self.player_1.body.velocity.x = 0
            elif k == key.W:
                pass
        return False


def get_new_game():
    scene = Scene()
    game = Game()
    hud = Hud()
    scene.add(game, z=0, name="game layer")
    scene.add(hud, z=1, name="hud layer")
    return scene

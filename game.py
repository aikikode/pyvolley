#!/usr/bin/env python
import random
from cocos.director import director, cocos
from cocos.layer import Layer
from cocos.scene import Scene
from pyglet.window import key, pyglet
import pymunk
import constants
from gamectrl import GameCtrl
from hud import Hud
from models import Ball, Player

__author__ = 'aikikode'

pyglet.resource.path = [constants.IMAGES_RESOURCE]
pyglet.resource.reindex()

SPEED = constants.PLAYER_SPEED
JUMP_SPEED = constants.PLAYER_JUMP_SPEED


class Game(Layer):
    is_event_handler = True  # enable pyglet's events

    def __init__(self):
        super(Game, self).__init__()
        self.width, self.height = director.get_window_size()
        self.space = pymunk.Space()
        self.space.gravity = constants.GRAVITY
        # Background image
        bg = cocos.sprite.Sprite('background.png')
        bg.position = (self.width / 2., self.height / 2.)
        self.add(bg, z=-1)
        # Add player 1
        self.players = []
        self.players.append(Player((200, 176/2), "player_1.png"))
        self.space.add(self.players[0].body, self.players[0].body_shape, self.players[0].head_shape)
        self.add(self.players[0].sprite)
        # Add player 2
        self.players.append(Player((self.width - 200, 176/2), "player_2.png"))
        self.space.add(self.players[1].body, self.players[1].body_shape, self.players[1].head_shape)
        self.add(self.players[1].sprite)
        # Add ball
        self.reset_ball()
        # Add walls and net
        self.create_container()
        #
        self.schedule(self.update)
        self.space.add_collision_handler(1, 2, begin=self.on_player_hits_wall, post_solve=self.on_player_hits_wall)
        self.space.add_collision_handler(1, 4, begin=self.on_player_hits_net, post_solve=self.on_player_hits_net)
        self.space.add_collision_handler(1, 5, begin=self.on_player_hits_net, post_solve=self.on_player_hits_net)
        self.space.add_collision_handler(1, 3, begin=self.on_player_hits_ground, post_solve=self.on_player_hits_ground)
        self.space.add_collision_handler(0, 1, begin=self.on_player_hits_ball)
        self.space.add_collision_handler(0, 4, begin=lambda x, y: False)
        self.space.add_collision_handler(0, 3, begin=self.on_ball_hits_ground)
        self.game_active = True
        self.schedule_pause_ball = True
        # Configure event manager to send game events to control module
        self.event_manager = pyglet.event.EventDispatcher()
        self.event_manager.register_event_type('on_ball_hits_ground')
        self.event_manager.register_event_type('on_player_hits_ball')

    def reset_ball(self, player=None):
        try:
            self.space.remove(self.ball.body, self.ball.shape)
            self.remove(self.ball.sprite)
            self.remove(self.ball.indicator)
        except AttributeError:
            pass
        # Add ball
        if not player:
            random.seed()
            player = random.sample(self.players, 1)[0]
        if player == self.players[0]:
            self.ball = Ball((self.width / 4., 400))
        else:
            self.ball = Ball((3 * self.width / 4., 400))
        self.space.add(self.ball.body, self.ball.shape)
        self.add(self.ball.sprite)
        # self.ball.body.sleep()
        self.ball.set_indicator_height(self.height - 10)
        self.add(self.ball.indicator)
        self.players[0].reset((200, 176/2))
        self.players[1].reset((self.width - 200, 176/2))
        self.schedule_pause_ball = True
        self.game_active = True

    def pause_ball(self):
        self.ball.body.sleep()

    def on_player_hits_wall(self, space, arbiter):
        if arbiter.shapes[0] in [self.players[0].body_shape, self.players[0].head_shape]:
            self.players[0].body.velocity.x = 0
            self.players[0].body.position.x = 70
        elif arbiter.shapes[0] in [self.players[1].body_shape, self.players[1].head_shape]:
            self.players[1].body.velocity.x = 0
            self.players[1].body.position.x = self.width - 70
        return True

    def on_player_hits_net(self, space, arbiter):
        if arbiter.shapes[0] in [self.players[0].body_shape, self.players[0].head_shape]:
            self.players[0].body.velocity.x = 0
            self.players[0].body.position.x = self.width / 2 - 60 - 15
        elif arbiter.shapes[0] in [self.players[1].body_shape, self.players[1].head_shape]:
            self.players[1].body.velocity.x = 0
            self.players[1].body.position.x = self.width / 2 + 60 + 15
        return True

    def on_player_hits_ground(self, space, arbiter):
        if arbiter.shapes[0] in [self.players[0].body_shape]:
            self.players[0].body.velocity.y = 0
        elif arbiter.shapes[0] in [self.players[1].body_shape]:
            self.players[1].body.velocity.y = 0
        return True

    def on_player_hits_ball(self, space, arbiter):
        self.event_manager.dispatch_event('on_player_hits_ball', self)
        if self.ball.body.is_sleeping:
            self.ball.body.activate()
        return True

    def on_ball_hits_ground(self, space, arbiter):
        if self.game_active:
            self.game_active = False
            self.event_manager.dispatch_event('on_ball_hits_ground', self)
        return True

    def create_container(self):
        space = self.space
        # Add left and right screen borders
        border_width = 50
        ss = [
            pymunk.Segment(space.static_body, (self.width + border_width, 0), (self.width + border_width, max(self.height * 10, 1000)), border_width),
            pymunk.Segment(space.static_body, (-border_width, 0), (-border_width, max(self.height * 10, 1000)), border_width)
        ]
        for s in ss:
            s.elasticity = 0.95
            s.collision_type = 2
        space.add(ss)
        # Add ground
        ground_body = space.static_body
        ground = pymunk.Segment(ground_body, (0, 0), (self.width, 0), 15)
        ground.elasticity = 0.5
        ground.collision_type = 3
        ground.friction = 0.99
        space.add(ground)
        # Add net
        net = pymunk.Segment(space.static_body, (self.width / 2., 0), (self.width / 2., 400), 20)
        net.elasticity = 0.95
        net.collision_type = 5
        space.add(net)
        net_sprite = cocos.sprite.Sprite('net.png')
        net_sprite.position = (self.width / 2., 200)
        self.add(net_sprite)
        # Add virtual net to prevent players from jumping to each other field
        virtual_net = pymunk.Segment(space.static_body, (self.width / 2., 0), (self.width / 2., max(self.height * 10, 1000)), 20)
        virtual_net.elasticity = 0.95
        virtual_net.collision_type = 4
        space.add(virtual_net)
        # Add simple motor to prevent players from sliding
        self.space.add(pymunk.constraint.SimpleMotor(self.players[0].body, ground_body, 0))
        self.space.add(pymunk.constraint.SimpleMotor(self.players[1].body, ground_body, 0))

    def get_ball_player(self):
        return 0 if self.ball.body.position[0] <= self.width / 2. else 1

    def get_other_player(self, player):
        return self.players[1] if player == self.players[0] else self.players[0]

    def update(self, dt):
        dt = 1.0 / 120.
        self.space.step(dt)
        self.ball.update(dt)
        self.players[0].update(dt)
        self.players[1].update(dt)
        if self.schedule_pause_ball:
            self.schedule_pause_ball = False
            self.pause_ball()

    def on_key_press(self, k, m):
        if self.game_active:
            if k in (key.LEFT, key.RIGHT, key.UP):
                if k == key.LEFT:
                    self.players[1].move_left()
                elif k == key.RIGHT:
                    self.players[1].move_right()
                elif k == key.UP:
                    self.players[1].jump()
            elif k in (key.A, key.D, key.W):
                if k == key.A:
                    self.players[0].move_left()
                elif k == key.D:
                    self.players[0].move_right()
                elif k == key.W:
                    self.players[0].jump()
        return False

    def on_key_release(self, k, m):
        if k in (key.LEFT, key.RIGHT, key.UP):
            if (k == key.LEFT and self.players[1].body.velocity.x < 0) or\
                    (k == key.RIGHT and self.players[1].body.velocity.x > 0):
                self.players[1].stop()
            elif k == key.UP:
                pass
        elif k in (key.A, key.D, key.W):
            if (k == key.A and self.players[0].body.velocity.x < 0) or\
                    (k == key.D and self.players[0].body.velocity.x > 0):
                self.players[0].stop()
            elif k == key.W:
                pass
        return False


def get_new_game():
    scene = Scene()
    game = Game()
    hud = Hud()
    game_ctrl = GameCtrl(game, hud)
    scene.add(game, z=0, name="game layer")
    scene.add(game_ctrl, z=1, name="game control layer")
    scene.add(hud, z=2, name="hud layer")
    return scene

#!/usr/bin/env python
import ConfigParser
import random

from cocos.director import director, cocos
from cocos.layer import Layer, ColorLayer
from cocos.scene import Scene
from cocos.text import Label
import pyglet
from pyglet.window import key
import pymunk

import constants
from gamectrl import GameCtrl
from hud import Hud
from models import Ball, Player


__author__ = 'aikikode'


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
        # Save all sprites that need to be rendered on top and render them last
        self.top_sprites = []
        # Add walls and net
        self.create_container()
        # Add player 1
        self.players = []
        self.players.append(Player((200, 176/2 + constants.GROUND_OFFSET), "player_1.png"))
        self.space.add(self.players[0].body, self.players[0].body_shape, self.players[0].head_shape)
        self.add(self.players[0].shadow_sprite)
        self.top_sprites.append(self.players[0].sprite)
        # Add player 2
        self.players.append(Player((self.width - 200, 176/2 + constants.GROUND_OFFSET), "player_2.png"))
        self.space.add(self.players[1].body, self.players[1].body_shape, self.players[1].head_shape)
        self.add(self.players[1].shadow_sprite)
        self.top_sprites.append(self.players[1].sprite)
        # Add ball
        self.reset_ball()
        # Use 'schedule_interval' instead of 'schedule' to have control over game speed
        self.schedule_interval(self.update, 1./constants.FPS)
        # Add custom collision handlers
        self.space.add_collision_handler(1, 2, begin=lambda x, y: False)  # Player should not collide with 'ball wall'
        self.space.add_collision_handler(1, 4, begin=self.on_player_hits_net, post_solve=self.on_player_hits_net)
        self.space.add_collision_handler(1, 6, begin=self.on_player_hits_virtual_wall, post_solve=self.on_player_hits_virtual_wall)
        self.space.add_collision_handler(1, 5, begin=self.on_player_hits_net, post_solve=self.on_player_hits_net)
        self.space.add_collision_handler(1, 3, begin=self.on_player_hits_ground, post_solve=self.on_player_hits_ground)
        self.space.add_collision_handler(0, 1, begin=self.on_player_hits_ball)
        self.space.add_collision_handler(0, 3, begin=self.on_ball_hits_ground)
        self.space.add_collision_handler(0, 4, begin=lambda x, y: False)  # Ball should not collide with 'player walls'
        self.game_ended = False
        self.game_active = True
        self.schedule_pause_ball = True
        # Configure event manager to send game events to control module
        self.event_manager = pyglet.event.EventDispatcher()
        self.event_manager.register_event_type('on_ball_hits_ground')
        self.event_manager.register_event_type('on_player_hits_ball')
        # Read settings and keybindings
        self.config_player = [{}, {}]
        self.read_settings()
        self.stop_player_sliding()

    def read_settings(self):
        config = ConfigParser.RawConfigParser()
        try:
            config.read(constants.CONFIG_FILE)
            self.config_player[0]['name'] = config.get("PLAYER1", "name")
            self.config_player[0]['left'] = int(config.get("PLAYER1", "left"))
            self.config_player[0]['right'] = int(config.get("PLAYER1", "right"))
            self.config_player[0]['jump'] = int(config.get("PLAYER1", "jump"))
            self.config_player[1]['name'] = config.get("PLAYER2", "name")
            self.config_player[1]['left'] = int(config.get("PLAYER2", "left"))
            self.config_player[1]['right'] = int(config.get("PLAYER2", "right"))
            self.config_player[1]['jump'] = int(config.get("PLAYER2", "jump"))
        except Exception as e:
            # Default controls
            self.config_player[0]['name'] = 'Player1'
            self.config_player[0]['left'] = key.A
            self.config_player[0]['right'] = key.D
            self.config_player[0]['jump'] = key.W
            self.config_player[1]['name'] = 'Player2'
            self.config_player[1]['left'] = key.LEFT
            self.config_player[1]['right'] = key.RIGHT
            self.config_player[1]['jump'] = key.UP

    def reset_ball(self, player=None):
        try:
            self.space.remove(self.ball.body, self.ball.shape)
            self.remove(self.ball.sprite)
            self.remove(self.ball.shadow_sprite)
            self.remove(self.ball.indicator)
            # Remove player sprites to add them after on top of ball shadow
            self.remove(self.players[0].sprite)
            self.remove(self.players[1].sprite)
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
        self.add(self.ball.shadow_sprite)
        self.add(self.ball.sprite)
        self.ball.set_indicator_height(self.height - 10)
        self.add(self.ball.indicator)
        self.players[0].reset((200, 176/2 + constants.GROUND_OFFSET))
        self.players[1].reset((self.width - 200, 176/2 + constants.GROUND_OFFSET))
        self.schedule_pause_ball = True
        self.game_active = True
        self.render_top_sprites()

    def render_top_sprites(self):
        for sprite in self.top_sprites:
            self.add(sprite)

    def pause_ball(self):
        self.ball.body.sleep()

    def on_player_hits_net(self, space, arbiter):
        if arbiter.shapes[0] in [self.players[0].body_shape, self.players[0].head_shape]:
            self.players[0].body.velocity.x = 0
            self.players[0].body.position.x = self.width / 2 - 60 - 15
        elif arbiter.shapes[0] in [self.players[1].body_shape, self.players[1].head_shape]:
            self.players[1].body.velocity.x = 0
            self.players[1].body.position.x = self.width / 2 + 60 + 15
        return True

    def on_player_hits_virtual_wall(self, space, arbiter):
        if arbiter.shapes[0] in [self.players[0].body_shape, self.players[0].head_shape]:
            self.players[0].body.velocity.x = 0
            self.players[0].body.position.x = 0
        elif arbiter.shapes[0] in [self.players[1].body_shape, self.players[1].head_shape]:
            self.players[1].body.velocity.x = 0
            self.players[1].body.position.x = self.width
        return True

    def on_player_hits_ground(self, space, arbiter):
        if arbiter.shapes[0] in [self.players[0].body_shape]:
            self.players[0].body.velocity.y = 0
        elif arbiter.shapes[0] in [self.players[1].body_shape]:
            self.players[1].body.velocity.y = 0
        return True

    def on_player_hits_ball(self, space, arbiter):
        if not self.game_active:
            return False
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
        # Add left and right screen borders for ball
        border_width = 50
        ss = [
            pymunk.Segment(space.static_body, (self.width + border_width, 0), (self.width + border_width, max(self.height * 10, 1000)), border_width),
            pymunk.Segment(space.static_body, (-border_width, 0), (-border_width, max(self.height * 10, 1000)), border_width)
        ]
        for s in ss:
            s.elasticity = 0.95
            s.collision_type = 2
        space.add(ss)
        # Add left and right screen borders for player
        border_width = 50
        ss = [
            pymunk.Segment(space.static_body, (self.width + border_width, 0), (self.width + border_width, max(self.height * 10, 1000)), 5),
            pymunk.Segment(space.static_body, (-border_width, 0), (-border_width, max(self.height * 10, 1000)), 5)
        ]
        for s in ss:
            s.elasticity = 0
            s.collision_type = 6
        space.add(ss)
        # Add ground
        self.ground_body = ground_body = space.static_body
        ground = pymunk.Segment(ground_body, (0, 0), (self.width, 0), constants.GROUND_OFFSET)
        ground.elasticity = 0.5
        ground.collision_type = 3
        ground.friction = 0.99
        space.add(ground)
        # Add net
        net = pymunk.Segment(space.static_body, (self.width / 2., 0), (self.width / 2., 450), 20)
        net.elasticity = 0.95
        net.collision_type = 5
        space.add(net)
        net_shadow_sprite = cocos.sprite.Sprite('net_shadow.png')
        net_shadow_sprite.position = (self.width / 2. + 150, 50)
        self.add(net_shadow_sprite)
        net_sprite = cocos.sprite.Sprite('net.png')
        net_sprite.position = (self.width / 2., 450 / 2.)
        self.top_sprites.append(net_sprite)
        # Add virtual net to prevent players from jumping to each other field
        virtual_net = pymunk.Segment(space.static_body, (self.width / 2., 0), (self.width / 2., max(self.height * 10, 1000)), 20)
        virtual_net.elasticity = 0.95
        virtual_net.collision_type = 4
        space.add(virtual_net)

    def stop_player_sliding(self):
        # Add simple motor to prevent players from sliding on the ground
        self.space.add(pymunk.constraint.SimpleMotor(self.players[0].body, self.ground_body, 0))
        self.space.add(pymunk.constraint.SimpleMotor(self.players[1].body, self.ground_body, 0))

    def get_ball_player(self):
        return 0 if self.ball.body.position[0] <= self.width / 2. else 1

    def update(self, dt):
        dt = constants.GAME_SPEED / float(constants.FPS)
        self.space.step(dt)
        self.ball.update(dt)
        self.players[0].update(dt)
        self.players[1].update(dt)
        if self.schedule_pause_ball:
            self.schedule_pause_ball = False
            self.pause_ball()

    def on_key_press(self, k, m):
        if self.game_active and not self.game_ended:
            if k == self.config_player[1]['left']:
                self.players[1].move_left()
            elif k == self.config_player[1]['right']:
                self.players[1].move_right()
            elif k == self.config_player[1]['jump']:
                self.players[1].start_jumping()
            elif k == self.config_player[0]['left']:
                self.players[0].move_left()
            elif k == self.config_player[0]['right']:
                self.players[0].move_right()
            elif k == self.config_player[0]['jump']:
                self.players[0].start_jumping()
        return False

    def on_key_release(self, k, m):
        if (k == self.config_player[1]['left'] and self.players[1].body.velocity.x < 0) or\
                (k == self.config_player[1]['right'] and self.players[1].body.velocity.x > 0):
            self.players[1].stop()
        elif k == self.config_player[1]['jump']:
            self.players[1].stop_jumping()
        if (k == self.config_player[0]['left'] and self.players[0].body.velocity.x < 0) or\
                    (k == self.config_player[0]['right'] and self.players[0].body.velocity.x > 0):
            self.players[0].stop()
        elif k == self.config_player[0]['jump']:
            self.players[0].stop_jumping()
        return False


class EndGame(Layer):
    def __init__(self):
        super(EndGame, self).__init__()
        self.background = ColorLayer(0, 0, 0, 170)
        self.label = Label()

    def reset(self):
        self.remove(self.background)
        self.remove(self.label)

    def show_win_screen(self, text="", position=(0, 0)):
        self.add(self.background)
        self.label = Label(text, position, font_name='Edit Undo Line BRK', font_size=32, anchor_x='center')
        self.add(self.label)


def get_new_game():
    scene = Scene()
    game = Game()
    hud = Hud()
    end_game = EndGame()
    game_ctrl = GameCtrl(game, hud, end_game)
    scene.add(game, z=0, name="game layer")
    scene.add(game_ctrl, z=1, name="game control layer")
    scene.add(hud, z=2, name="hud layer")
    scene.add(end_game, z=3, name="end game layer")
    return scene

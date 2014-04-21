#!/usr/bin/env python
#from __future__ import division, print_function
import ConfigParser
import cocos
from cocos.actions import JumpBy, Repeat, MoveBy, Reverse
from cocos.director import director, cocos
from cocos.layer import MultiplexLayer, Layer
from cocos.menu import *
from cocos.scene import Scene
from cocos.text import Label
import pyglet
from pyglet.window import key
import constants
import os, stat

__author__ = 'aikikode'


class BackgroundLayer(Layer):
    def __init__(self):
        super(BackgroundLayer, self).__init__()
        self.width, self.height = director.get_window_size()
        # Background image
        bg = cocos.sprite.Sprite('background.png')
        bg.position = (self.width / 2., self.height / 2.)
        self.add(bg, z=0)
        # Add moving player
        player = cocos.sprite.Sprite('player_1.png')
        player.position = (150, 176/2 + 25)
        action = MoveBy((150, 0), 1)
        player.do(Repeat(action + Reverse(action)))
        self.add(player, z=1)
        # Add bouncing ball
        ball = cocos.sprite.Sprite('volleyball.png')
        ball.scale = 5/6.
        ball.position = (self.width - 200, 25 + 30)
        action = Repeat(JumpBy((0, 0), 300, 1, 1.5))
        ball.do(action)
        self.add(ball, z=1)


class MainMenu(Menu):
    def __init__(self):
        super(MainMenu, self).__init__('PyVolley')
        self.menu_anchor_x = CENTER
        self.menu_anchor_y = CENTER

        self.font_title['font_name'] = 'Edit Undo Line BRK'
        self.font_title['font_size'] = 72
        self.font_title['color'] = (0, 255, 0, 255)
        self.font_item['font_name'] = 'Edit Undo Line BRK',
        self.font_item['font_size'] = 46
        self.font_item['color'] = (0, 0, 0, 200)
        self.font_item_selected['font_name'] = 'Edit Undo Line BRK'
        self.font_item_selected['font_size'] = 56
        self.font_item_selected['color'] = (0, 0, 0, 255)

        items = [MenuItem('Start', self.on_start_game),
                 MenuItem('Options', self.on_options),
                 MenuItem('Scores', self.on_scores),
                 MenuItem('Quit', self.on_quit)]
        self.create_menu(items, shake(), shake_back())

    def on_start_game(self):
        import game
        director.push(game.get_new_game())

    def on_options(self):
        self.parent.switch_to(1)

    def on_scores(self):
        pass

    def on_quit(self):
        pyglet.app.exit()


class OptionsMenu(Menu):
    def __init__(self):
        super(OptionsMenu, self).__init__('Options')

        self.menu_anchor_x = CENTER
        self.menu_anchor_y = CENTER

        self.font_title['font_name'] = 'Edit Undo Line BRK'
        self.font_title['font_size'] = 72
        self.font_title['color'] = (0, 255, 0, 255)
        self.font_item['font_name'] = 'Edit Undo Line BRK',
        self.font_item['font_size'] = 32
        self.font_item['color'] = (0, 0, 0, 200)
        self.font_item_selected['font_name'] = 'Edit Undo Line BRK'
        self.font_item_selected['font_size'] = 46
        self.font_item_selected['color'] = (0, 0, 0, 255)

        items = [ToggleMenuItem('Show FPS:', self.on_show_fps, director.show_FPS),
                 MenuItem('Toggle fullscreen', self.on_toggle_fullscreen),
                 MenuItem('Configure controls', self.on_configure_controls),
                 MenuItem('Back', self.on_quit)]
        self.create_menu(items, shake(), shake_back())

    def on_toggle_fullscreen(self):
        director.window.set_fullscreen(not director.window.fullscreen)

    def on_quit(self):
        self.parent.switch_to(0)

    def on_show_fps(self, value):
        director.show_FPS = value

    def on_configure_controls(self):
        self.parent.switch_to(2)


class PlayersSetup(Layer):
    is_event_handler = True  # enable pyglet's events

    def __init__(self):
        super(PlayersSetup, self).__init__()
        self.width, self.height = director.get_window_size()
        self.players = [{}, {}]
        self.label = Label("Player 1", (300, self.height - 50), font_name='Edit Undo Line BRK', font_size=32, anchor_x='center', color=(0, 0, 0, 255))
        self.add(self.label)
        self.label_height = self.height - 150
        label = Label("left", (self.width / 3., self.label_height), font_name='Edit Undo Line BRK', font_size=30, anchor_x='center', color=(0, 0, 0, 255))
        self.add(label)
        self.read_settings()
        self.options = ["left", "right", "jump", "left", "right", "jump"]
        self.cur_option = 0

    def read_settings(self):
        config = ConfigParser.RawConfigParser()
        try:
            config.read(constants.CONFIG_FILE)
            self.players[0]['name'] = config.get("PLAYER1", "name")
            self.players[0]['left'] = config.get("PLAYER1", "left")
            self.players[0]['right'] = config.get("PLAYER1", "right")
            self.players[0]['jump'] = config.get("PLAYER1", "jump")
            self.players[1]['name'] = config.get("PLAYER2", "name")
            self.players[1]['left'] = config.get("PLAYER2", "left")
            self.players[1]['right'] = config.get("PLAYER2", "right")
            self.players[1]['jump'] = config.get("PLAYER2", "jump")
        except Exception as e:
            self.players[0]['name'] = 'Player1'
            self.players[0]['left'] = key.A
            self.players[0]['right'] = key.D
            self.players[0]['jump'] = key.W
            self.players[1]['name'] = 'Player2'
            self.players[1]['left'] = key.LEFT
            self.players[1]['right'] = key.RIGHT
            self.players[1]['jump'] = key.UP

    def save_settings(self):
        config = ConfigParser.RawConfigParser()
        try:
            if not config.has_section("PLAYER1"):
                config.add_section("PLAYER1")
            for elem in ['name', 'left', 'right', 'jump']:
                config.set("PLAYER1", elem, self.players[0][elem])
            if not config.has_section("PLAYER2"):
                config.add_section("PLAYER2")
            for elem in ['name', 'left', 'right', 'jump']:
                config.set("PLAYER2", elem, self.players[1][elem])
            with open(constants.CONFIG_FILE, 'w+') as configfile:
                os.chmod(constants.CONFIG_FILE, stat.S_IRUSR | stat.S_IWUSR)
                config.write(configfile)
        except Exception as e:
            print("Unable to save settings")

    def on_key_press(self, k, m):
        self.players[int(self.cur_option / 3)][self.options[self.cur_option]] = k
        label = Label(key.symbol_string(k), (self.width * 2 / 3., self.label_height), font_name='Edit Undo Line BRK', font_size=30, anchor_x='center', color=(0, 0, 0, 255))
        self.add(label)
        self.cur_option += 1
        self.label_height -= 100
        if self.cur_option == 3:
            label = Label("Player 2", (300, self.label_height), font_name='Edit Undo Line BRK', font_size=32, anchor_x='center', color=(0, 0, 0, 255))
            self.add(label)
            self.label_height -= 100
        if self.cur_option < len(self.options):
            label = Label(self.options[self.cur_option], (self.width / 3., self.label_height), font_name='Edit Undo Line BRK', font_size=30, anchor_x='center', color=(0, 0, 0, 255))
            self.add(label)
        else:
            self.save_settings()
            self.parent.switch_to(0)


if __name__ == '__main__':
    director.init(resizable=False, width=1280, height=960)
    scene = Scene()
    scene.add(BackgroundLayer(), z=0)
    scene.add(MultiplexLayer(
        MainMenu(),
        OptionsMenu(),
        PlayersSetup(),
    ), z=1)
    director.run(scene)

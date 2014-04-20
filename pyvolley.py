#!/usr/bin/env python
from __future__ import division, print_function
import cocos
from cocos.actions import JumpBy, Repeat, MoveBy, Reverse
from cocos.director import director, cocos
from cocos.layer import MultiplexLayer, Layer
from cocos.menu import *
from cocos.scene import Scene
import pyglet
import constants

__author__ = 'aikikode'

pyglet.resource.path = [constants.IMAGES_RESOURCE]
pyglet.resource.reindex()


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
        player.position = (200, 176/2 + 25)
        action = MoveBy((300, 0), 2)
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
                 MenuItem('Back', self.on_quit)]
        self.create_menu(items, shake(), shake_back())

    def on_toggle_fullscreen(self):
        director.window.set_fullscreen(not director.window.fullscreen)

    def on_quit(self):
        self.parent.switch_to(0)

    def on_show_fps(self, value):
        director.show_FPS = value


if __name__ == '__main__':
    director.init(resizable=False, width=1280, height=960)
    scene = Scene()
    scene.add(BackgroundLayer(), z=0)
    scene.add(MultiplexLayer(
        MainMenu(),
        OptionsMenu(),
        #ScoresLayer(),
    ), z=1)
    director.run(scene)

#!/usr/bin/env python
from __future__ import division, print_function
from cocos.director import director
from cocos.layer import MultiplexLayer
from cocos.menu import *
from cocos.scene import Scene
import pyglet

__author__ = 'aikikode'


class MainMenu(Menu):
    def __init__(self):
        super(MainMenu, self).__init__('PyVolley')
        self.menu_anchor_x = CENTER
        self.menu_anchor_y = CENTER

        self.font_title['font_name'] = 'Edit Undo Line BRK'
        self.font_title['font_size'] = 72
        self.font_item['font_name'] = 'Edit Undo Line BRK',
        self.font_item['font_size'] = 46
        self.font_item_selected['font_name'] = 'Edit Undo Line BRK'
        self.font_item_selected['font_size'] = 56

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
        self.font_item['font_name'] = 'Edit Undo Line BRK',
        self.font_item['font_size'] = 32
        self.font_item_selected['font_name'] = 'Edit Undo Line BRK'
        self.font_item_selected['font_size'] = 46

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
    director.init(resizable=False, width=1024, height=768)
    scene = Scene()
    scene.add(MultiplexLayer(
        MainMenu(),
        OptionsMenu(),
        #ScoresLayer(),
    ), z=1)
    director.run(scene)

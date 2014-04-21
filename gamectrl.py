#!/usr/bin/env python
from cocos.director import director
from cocos.layer import Layer
import pyglet
import constants
import game
from threading import Timer

__author__ = 'aikikode'


class GameCtrl(Layer):
    def __init__(self, game, hud):
        super(GameCtrl, self).__init__()
        self.game = game
        self.hud = hud
        self.game.event_manager.push_handlers(self)
        self.score = [0, 0]
        self.inning = self.game.get_ball_player()
        self.update_scores()
        # Player can hit the ball only X times in a row
        self.hit_count_limit = 3
        self.hit_count = 0
        self.current_player = self.inning
        self.player_volume = 0.05
        self.whistle_sound = pyglet.resource.media('whistle.wav', streaming=False)
        self.ball_hit_sound = pyglet.resource.media('ball_hit.wav', streaming=False)

    def play(self, sound):
        music_player = pyglet.media.Player()
        music_player.volume = self.player_volume
        music_player.queue(sound)
        music_player.play()

    def scored(self, player):
        self.play(self.whistle_sound)
        if player == self.inning:
            self.score[player] += 1
            if self.score[player] >= constants.SCORE_LIMIT:
                # TODO: win/loose screen
                director.replace(game.get_new_game())
        else:
            self.inning = 1 if self.inning == 0 else 0
        self.update_scores()
        Timer(2, self.game.reset_ball, (self.game.players[player],)).start()

    def get_current_player(self):
        return self.game.get_ball_player()

    def on_ball_hits_ground(self, emitter):
        self.scored(1 if self.game.get_ball_player() == 0 else 0)

    def update_scores(self):
        self.hud.players_score[self.inning].element.text = "{}!".format(self.score[self.inning])
        self.hud.players_score[not self.inning].element.text = "{}".format(self.score[not self.inning])

    def on_player_hits_ball(self, emitter):
        if self.game.game_active:
            self.play(self.ball_hit_sound)
            if self.get_current_player() == self.current_player:
                self.hit_count += 1
            else:
                self.hit_count = 1
                self.current_player = self.get_current_player()
            if self.hit_count > self.hit_count_limit:
                self.game.game_active = False
                self.scored(1 if self.current_player == 0 else 0)

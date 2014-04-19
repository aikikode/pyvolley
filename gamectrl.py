#!/usr/bin/env python
from cocos.director import director
from cocos.layer import Layer
import constants
import game

__author__ = 'aikikode'


class GameCtrl(Layer):
    def __init__(self, game, hud):
        super(GameCtrl, self).__init__()
        self.game = game
        self.hud = hud
        self.game.event_manager.push_handlers(self)
        self.score = [0, 0]
        self.inning = self.game.player_to_index(self.game.get_ball_player())
        self.update_scores()

    def on_ball_hits_ground(self, emitter):
        player = self.game.player_to_index(self.game.get_other_player(self.game.get_ball_player()))
        if player == self.inning:
            self.score[player] += 1
            if self.score[player] >= constants.SCORE_LIMIT:
                # TODO: win/loose screen
                director.replace(game.get_new_game())
        else:
            self.inning = 1 if self.inning == 0 else 0
        self.update_scores()

    def update_scores(self):
        self.hud.players_score[self.inning].element.text = "{}!".format(self.score[self.inning])
        self.hud.players_score[not self.inning].element.text = "{}".format(self.score[not self.inning])

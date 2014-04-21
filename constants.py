import math
import pyglet

IMAGES_RESOURCE = "data/images"
SOUNDS_RESOURCE = "data/sounds"

pyglet.resource.path = [IMAGES_RESOURCE, SOUNDS_RESOURCE]
pyglet.resource.reindex()

GRAVITY = (0.0, -900.0)

BALL_MASS = 20
BALL_RADIUS = 50
BALL_VELOCITY_LIMIT = 2000
BALL_ADDITIONAL_FORCE = (0, -math.pow(10, 4)*7)

PLAYER_MASS = math.pow(10, 4)
PLAYER_ADDITIONAL_FORCE = (0, -math.pow(10, 8))
PLAYER_JUMP_SPEED = 3100
PLAYER_SPEED = 1500

SCORE_LIMIT = 15

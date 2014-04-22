import math
import pyglet

IMAGES_RESOURCE = "data/images"
SOUNDS_RESOURCE = "data/sounds"
CONFIG_FILE = "settings.cfg"

pyglet.resource.path = [IMAGES_RESOURCE, SOUNDS_RESOURCE]
pyglet.resource.reindex()

GRAVITY = (0.0, -900.0)

BALL_MASS = 10
BALL_RADIUS = 50
BALL_VELOCITY_LIMIT = 2000
BALL_ADDITIONAL_FORCE = (0, -math.pow(10, 4)*4)

PLAYER_MASS = math.pow(10, 6)
PLAYER_ADDITIONAL_FORCE = (0, -math.pow(10, 10))
PLAYER_JUMP_SPEED = 3100
PLAYER_SPEED = 2000

SCORE_LIMIT = 15

FPS = 60
GAME_SPEED = 0.5

GROUND_OFFSET = 50

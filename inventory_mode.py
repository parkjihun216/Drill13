from pathlib import Path

from pico2d import *

image = None
ball_choices = {SDLK_0: 0, SDLK_1: 1, SDLK_2: 2}


def init():
    global image
    image = load_image(str(Path(__file__).with_name('item_select.png')))


def finish():
    global image
    image = None


def handle_event(event, boy):
    if event.type == SDL_KEYDOWN and event.key in ball_choices:
        boy.select_ball(ball_choices[event.key])
        return True
    return False


def render():
    image.draw(get_canvas_width() / 2, get_canvas_height() / 2)

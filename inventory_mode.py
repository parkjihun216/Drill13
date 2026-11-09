from pathlib import Path

from pico2d import *
import game_framework
import game_world
import play_mode

image = None


def init():
    global image
    image = load_image(str(Path(__file__).with_name('item_select.png')))


def finish():
    global image
    image = None


def handle_events():
    for event in get_events():
        if event.type == SDL_QUIT:
            game_framework.quit()
            return


def update():
    pass


def render():
    clear_canvas()
    game_world.render()
    image.draw(get_canvas_width() / 2, get_canvas_height() / 2)
    update_canvas()

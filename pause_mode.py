from pathlib import Path

from pico2d import *
import game_framework
import game_world
import play_mode

image = None


def init():
    global image
    image = load_image(str(Path(__file__).with_name('pause.png')))


def finish():
    global image
    image = None


def handle_events():
    events = get_events()
    # Apply releases only on resume so the paused pose stays unchanged.
    play_mode.paused_key_releases.extend(
        event for event in events if event.type == SDL_KEYUP
    )
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
            return
        elif (event.type == SDL_KEYDOWN and event.key == SDLK_p
              and not getattr(event, 'repeat', 0)):
            game_framework.pop_mode()
            return


def update():
    pass


def render():
    clear_canvas()
    game_world.render()
    width, height = get_canvas_width(), get_canvas_height()
    image.draw(width / 2, height / 2, width, height)
    update_canvas()

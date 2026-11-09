from pathlib import Path

from pico2d import *
import game_framework
import game_world
import play_mode

image = None
ball_choices = {SDLK_0: 0, SDLK_1: 1, SDLK_2: 2}


def init():
    global image
    image = load_image(str(Path(__file__).with_name('item_select.png')))


def finish():
    global image
    image = None


def handle_events():
    events = get_events()
    # Replay releases on resume to avoid leaving movement keys held down.
    play_mode.paused_key_releases.extend(
        event for event in events if event.type == SDL_KEYUP
    )
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
            return
        elif (event.type == SDL_KEYDOWN and event.key == SDLK_i
              and not getattr(event, 'repeat', 0)):
            game_framework.pop_mode()
            return
        elif event.type == SDL_KEYDOWN and event.key in ball_choices:
            play_mode.boy.select_ball(ball_choices[event.key])


def update():
    pass


def render():
    clear_canvas()
    game_world.render()
    image.draw(get_canvas_width() / 2, get_canvas_height() / 2)
    update_canvas()

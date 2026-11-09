import game_framework
from pico2d import *

def init():
    global image
    global logo_start_time
    image = load_image('tuk_credit.png')
    logo_start_time = get_time()
def finish():
    global image
    del image
def handle_events():
    for event in get_events():
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()

def render():
    clear_canvas()
    image.draw(400, 300)
    update_canvas()

def update():
    global logo_start_time
    if get_time() - logo_start_time >= 2.0:
        import title_mode
        game_framework.change_mode(title_mode)

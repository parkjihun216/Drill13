from pico2d import *
from boy import Boy
from grass import Grass
import game_world
import game_framework
import inventory_mode
boy = None
paused_at = None
paused_key_releases = []
def handle_events():
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
            return
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            import title_mode
            game_framework.change_mode(title_mode)
            return
        elif event.type == SDL_KEYDOWN and event.key == SDLK_i:
            if not getattr(event, 'repeat', 0):
                if inventory_mode.image is None:
                    inventory_mode.init()
                else:
                    inventory_mode.finish()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_p:
            if not getattr(event, 'repeat', 0):
                import pause_mode
                game_framework.push_mode(pause_mode)
                paused_key_releases.extend(
                    e for e in event_list if e.type == SDL_KEYUP
                )
                return
        else:
            if (inventory_mode.image is not None
                    and inventory_mode.handle_event(event, boy)):
                continue
            boy.handle_event(event)
def init():
    global boy
    grass = Grass()
    game_world.add_object(grass, 0)
    boy = Boy()
    game_world.add_object(boy, 1)
def update():
    game_world.update()
def render():
    clear_canvas()
    game_world.render()
    if inventory_mode.image is not None:
        inventory_mode.render()
    update_canvas()
def pause():
    global paused_at
    paused_at = get_time()
    paused_key_releases.clear()

def resume():
    global paused_at
    # Do not count paused time toward the boy's five-second idle timer.
    boy.idle_started_at += get_time() - paused_at
    paused_at = None
    for event in paused_key_releases:
        boy.handle_event(event)
    paused_key_releases.clear()

def finish():
    global boy, paused_at
    inventory_mode.finish()
    game_world.clear()
    boy = None
    paused_at = None
    paused_key_releases.clear()

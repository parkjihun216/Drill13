from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from sdl2 import (SDL_KEYDOWN, SDL_KEYUP, SDL_QUIT, SDLK_0, SDLK_1,
                  SDLK_2, SDLK_i, SDLK_p, SDLK_RIGHT, SDLK_SPACE)

import game_framework
import game_world
import inventory_mode
import pause_mode
import play_mode


def key(keycode, event_type=SDL_KEYDOWN, repeat=0):
    return SimpleNamespace(type=event_type, key=keycode, repeat=repeat)


class InventoryModeTests(unittest.TestCase):
    def setUp(self):
        self.now = 10.0
        self.overlay = Mock()
        for patcher in (
            patch('boy.load_image', return_value=Mock()),
            patch('grass.load_image', return_value=Mock()),
            patch('inventory_mode.load_image', return_value=self.overlay),
            patch('pause_mode.load_image', return_value=Mock()),
            patch('boy.get_time', side_effect=lambda: self.now),
            patch('play_mode.get_time', side_effect=lambda: self.now),
        ):
            patcher.start()
            self.addCleanup(patcher.stop)
        game_world.clear()
        game_framework.stack = [play_mode]
        game_framework.running = True
        play_mode.init()

    def tearDown(self):
        while game_framework.stack:
            game_framework.stack.pop().finish()
        game_framework.running = False

    def send(self, mode, *events):
        with patch.object(mode, 'get_events', return_value=list(events)):
            mode.handle_events()

    def open_inventory(self):
        self.send(play_mode, key(SDLK_i))
        self.assertEqual(game_framework.stack, [play_mode, inventory_mode])

    def test_i_toggles_inventory_and_preserves_game_objects(self):
        player = play_mode.boy
        objects = [layer[:] for layer in game_world.world]
        self.open_inventory()
        inventory_mode.load_image.assert_called_once_with(
            str(Path(inventory_mode.__file__).with_name('item_select.png')))
        self.send(inventory_mode, key(SDLK_i))
        self.assertEqual(game_framework.stack, [play_mode])
        self.assertIs(play_mode.boy, player)
        self.assertEqual(game_world.world, objects)
        self.assertIsNone(inventory_mode.image)

    def test_number_keys_select_and_persist_after_reopening(self):
        self.open_inventory()
        for keycode, selection in ((SDLK_0, 0), (SDLK_1, 1), (SDLK_2, 2)):
            self.send(inventory_mode, key(keycode))
            self.assertEqual(play_mode.boy.ball_type, selection)
        self.send(inventory_mode, key(SDLK_i))
        self.open_inventory()
        self.assertEqual(play_mode.boy.ball_type, 2)

    def test_repeated_i_does_not_open_or_close_inventory(self):
        self.send(play_mode, key(SDLK_i, repeat=1))
        self.assertEqual(game_framework.stack, [play_mode])
        self.open_inventory()
        self.send(inventory_mode, key(SDLK_i, repeat=1))
        self.assertEqual(game_framework.stack, [play_mode, inventory_mode])

    def test_world_and_idle_timer_pause_while_inventory_is_open(self):
        self.open_inventory()
        self.now = 110.0
        with patch.object(game_world, 'update') as update:
            inventory_mode.update()
        update.assert_not_called()
        self.send(inventory_mode, key(SDLK_i))
        play_mode.boy.update()
        self.assertEqual(play_mode.boy.state, 'IDLE')
        self.assertEqual(play_mode.boy.idle_started_at, 110.0)

    def test_key_release_is_applied_when_closing_inventory(self):
        self.send(play_mode, key(SDLK_RIGHT))
        self.open_inventory()
        self.send(inventory_mode, key(SDLK_RIGHT, SDL_KEYUP))
        self.assertEqual(play_mode.boy.state, 'RUN')
        self.send(inventory_mode, key(SDLK_i))
        self.assertEqual(play_mode.boy.state, 'IDLE')
        self.assertEqual(play_mode.boy.pressed_keys, set())

    def test_releases_in_opening_and_closing_batches_are_preserved(self):
        for opening_batch in (True, False):
            with self.subTest(opening_batch=opening_batch):
                self.send(play_mode, key(SDLK_RIGHT))
                release = key(SDLK_RIGHT, SDL_KEYUP)
                if opening_batch:
                    self.send(play_mode, key(SDLK_i), release)
                    self.send(inventory_mode, key(SDLK_i))
                else:
                    self.open_inventory()
                    self.send(inventory_mode, key(SDLK_i), release)
                self.assertEqual(play_mode.boy.state, 'IDLE')
                self.assertEqual(play_mode.paused_key_releases, [])

    def test_inventory_does_not_forward_space_to_player(self):
        self.open_inventory()
        with patch.object(play_mode.boy, 'fire_ball') as fire:
            self.send(inventory_mode, key(SDLK_SPACE))
        fire.assert_not_called()

    def test_window_close_quits_from_inventory(self):
        self.open_inventory()
        self.send(inventory_mode, SimpleNamespace(type=SDL_QUIT))
        self.assertFalse(game_framework.running)

    def test_overlay_draws_at_canvas_center_after_world(self):
        self.open_inventory()
        calls = Mock()
        calls.attach_mock(self.overlay.draw, 'overlay')
        with patch.object(inventory_mode, 'clear_canvas'), \
                patch.object(inventory_mode, 'update_canvas'), \
                patch.object(inventory_mode, 'get_canvas_width', return_value=1024), \
                patch.object(inventory_mode, 'get_canvas_height', return_value=768), \
                patch.object(game_world, 'render') as render:
            calls.attach_mock(render, 'world')
            inventory_mode.render()
        self.overlay.draw.assert_called_once_with(512, 384)
        self.assertEqual([call[0] for call in calls.mock_calls], ['world', 'overlay'])

    def test_existing_pause_toggle_still_works(self):
        self.send(play_mode, key(SDLK_p))
        self.assertEqual(game_framework.stack, [play_mode, pause_mode])
        self.send(pause_mode, key(SDLK_p))
        self.assertEqual(game_framework.stack, [play_mode])


if __name__ == '__main__':
    unittest.main()

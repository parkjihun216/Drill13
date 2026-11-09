import unittest
from unittest.mock import Mock, patch

from ball import Ball
from boy import Boy
import game_world


class BallSelectionTests(unittest.TestCase):
    def setUp(self):
        game_world.clear()
        self.addCleanup(game_world.clear)
        self.small_image, self.large_image = Mock(), Mock()
        assets = {'ball21x21.png': self.small_image,
                  'ball41x41.png': self.large_image}
        for patcher in (
            patch.dict(Ball.images, {}, clear=True),
            patch('ball.load_image', side_effect=assets.__getitem__),
            patch('boy.load_image', return_value=Mock()),
            patch('boy.get_time', return_value=10.0),
        ):
            patcher.start()
            self.addCleanup(patcher.stop)
        self.boy = Boy()

    def test_default_selection_fires_small_ball(self):
        self.boy.fire_ball()
        ball, = game_world.world[1]
        self.assertIs(ball.image, self.small_image)
        self.assertEqual((ball.x, ball.y, ball.velocity), (400, 90, 10))

    def test_zero_disables_firing(self):
        self.boy.select_ball(0)
        self.boy.fire_ball()
        self.assertEqual(game_world.world[1], [])

    def test_selection_changes_only_future_balls(self):
        self.boy.select_ball(2)
        self.boy.fire_ball()
        self.boy.select_ball(1)
        self.boy.fire_ball()
        large, small = game_world.world[1]
        self.assertIs(large.image, self.large_image)
        self.assertIs(small.image, self.small_image)
        self.boy.select_ball(0)
        self.boy.fire_ball()
        self.assertEqual(game_world.world[1], [large, small])

    def test_large_ball_uses_facing_direction_and_own_sprite(self):
        self.boy.select_ball(2)
        self.boy.face_dir = -1
        self.boy.fire_ball()
        ball, = game_world.world[1]
        self.assertEqual(ball.velocity, -10)
        ball.draw()
        self.large_image.draw.assert_called_once_with(400, 90)

    def test_sprite_is_loaded_once_per_size(self):
        with patch('ball.load_image', return_value=self.small_image) as load:
            first = Ball(10, 10, 10)
            second = Ball(20, 10, 10)
        load.assert_called_once_with('ball21x21.png')
        self.assertIs(first.image, second.image)

    def test_large_ball_is_removed_after_leaving_canvas(self):
        ball = Ball(795, 90, 10, 2)
        game_world.add_object(ball)
        with patch('ball.get_canvas_width', return_value=800):
            game_world.update()
        self.assertEqual(game_world.world[1], [])

    def test_new_player_restores_default_selection(self):
        self.boy.select_ball(0)
        self.assertEqual(Boy().ball_type, 1)


if __name__ == '__main__':
    unittest.main()

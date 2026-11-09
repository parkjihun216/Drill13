from pico2d import get_canvas_width, load_image

import game_world


class Ball:
    images = {}
    image_files = {1: 'ball21x21.png', 2: 'ball41x41.png'}

    def __init__(self, x, y, velocity, size=1):
        if size not in Ball.images:
            Ball.images[size] = load_image(Ball.image_files[size])
        self.image = Ball.images[size]
        self.x, self.y = x, y
        self.velocity = velocity

    def update(self):
        self.x += self.velocity
        if self.x < 0 or self.x > get_canvas_width():
            game_world.remove_object(self)

    def draw(self):
        self.image.draw(self.x, self.y)

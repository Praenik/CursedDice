import math

import arcade
from PIL import Image, ImageDraw

from constants import SCREEN_HEIGHT, SCREEN_WIDTH
from core import dices


class BugbearBoulder(arcade.Sprite):
    def __init__(self, start_x, start_y, target_x, target_y):
        super().__init__()

        self.center_x = start_x
        self.center_y = start_y
        self.speed = 4.8
        self.max_lifetime = 4.0
        self.life_timer = 0.0

        self.texture = self._create_texture()
        self.width = 22
        self.height = 22

        dx = target_x - start_x
        dy = target_y - start_y
        distance = math.hypot(dx, dy)
        if distance == 0:
            dir_x, dir_y = 1.0, 0.0
        else:
            dir_x, dir_y = dx / distance, dy / distance

        self.velocity_x = dir_x * self.speed
        self.velocity_y = dir_y * self.speed

    def update(self, delta_time, player):
        self.life_timer += delta_time
        if self.life_timer >= self.max_lifetime:
            self.kill()
            return

        self.center_x += self.velocity_x * delta_time * 60
        self.center_y += self.velocity_y * delta_time * 60
        self.angle += 420 * delta_time

        if self.right < 0 or self.left > SCREEN_WIDTH or self.top < 0 or self.bottom > SCREEN_HEIGHT:
            self.kill()
            return

        self._check_hit(player)

    def _check_hit(self, player):
        if not player.is_alive():
            self.kill()
            return

        collision_distance = (self.width / 2) + (player.width / 2)
        distance = math.hypot(player.center_x - self.center_x, player.center_y - self.center_y)
        if distance <= collision_distance:
            damage = dices.roll_dice(6) + dices.roll_dice(6) + 3
            player.take_damage(damage)
            player.show_combat_feedback(f"-{damage}", (255, 120, 120))
            self.kill()

    def _create_texture(self):
        img = Image.new("RGBA", (22, 22), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.ellipse((1, 1, 20, 20), fill=(105, 90, 78, 255), outline=(225, 215, 205, 255), width=2)
        draw.line([(5, 7), (10, 4), (16, 8)], fill=(65, 55, 50, 255), width=2)
        draw.line([(6, 15), (13, 17), (18, 13)], fill=(65, 55, 50, 255), width=2)
        return arcade.Texture(img)

import math

import arcade
from PIL import Image, ImageDraw

from constants import SCREEN_HEIGHT, SCREEN_WIDTH


class Arrow(arcade.Sprite):
    def __init__(
        self,
        start_x,
        start_y,
        aim_x,
        aim_y,
        damage,
        attack_bonus,
        attacker=None,
        attack_disadvantage=False,
    ):
        super().__init__()

        self.center_x = start_x
        self.center_y = start_y
        self.damage = damage
        self.attack_bonus = attack_bonus
        self.attacker = attacker
        self.attack_disadvantage = attack_disadvantage

        self.speed = 8.0
        self.max_lifetime = 2.0
        self.life_timer = 0.0

        self.texture = self._create_texture()
        self.width = 22
        self.height = 6

        dir_x, dir_y = self._normalize(aim_x - start_x, aim_y - start_y)
        self.velocity_x = dir_x * self.speed
        self.velocity_y = dir_y * self.speed
        self.angle = -math.degrees(math.atan2(dir_y, dir_x))

    def update(self, delta_time, enemies):
        self.life_timer += delta_time
        if self.life_timer >= self.max_lifetime:
            self.kill()
            return

        self.center_x += self.velocity_x * delta_time * 60
        self.center_y += self.velocity_y * delta_time * 60

        if (
            self.right < 0
            or self.left > SCREEN_WIDTH
            or self.top < 0
            or self.bottom > SCREEN_HEIGHT
        ):
            self.kill()
            return

        self._check_hit(enemies)

    def _check_hit(self, enemies):
        for enemy in enemies:
            if not enemy.is_alive():
                continue

            collision_distance = (self.width / 2) + (enemy.width / 2)
            if self._distance_to(enemy) <= collision_distance:
                enemy.resolve_attack(
                    self.attack_bonus,
                    self.damage,
                    attacker=self.attacker,
                    disadvantage=self.attack_disadvantage,
                )
                self.kill()
                return

    def _distance_to(self, enemy):
        dx = enemy.center_x - self.center_x
        dy = enemy.center_y - self.center_y
        return math.hypot(dx, dy)

    def _normalize(self, dx, dy):
        distance = math.hypot(dx, dy)
        if distance == 0:
            return 1.0, 0.0
        return dx / distance, dy / distance

    def _create_texture(self):
        img = Image.new("RGBA", (22, 6), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.rectangle((0, 2, 15, 3), fill=(160, 110, 60, 255))
        draw.polygon([(15, 0), (21, 3), (15, 5)], fill=(200, 200, 200, 255))
        draw.polygon([(0, 0), (4, 3), (0, 5)], fill=(230, 230, 230, 200))
        return arcade.Texture(img)

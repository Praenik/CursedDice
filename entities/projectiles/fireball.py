import math

import arcade
from PIL import Image, ImageDraw

from constants import SCREEN_HEIGHT, SCREEN_WIDTH


class Fireball(arcade.Sprite):
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

        self.speed = 4.5
        self.turn_rate = 4.0
        self.homing_radius = 140
        self.max_lifetime = 3.0
        self.life_timer = 0.0
        self.target = None

        self.texture = self._create_texture()
        self.width = 16
        self.height = 16

        dir_x, dir_y = self._normalize(aim_x - start_x, aim_y - start_y)
        self.velocity_x = dir_x * self.speed
        self.velocity_y = dir_y * self.speed

    def update(self, delta_time, enemies):
        self.life_timer += delta_time
        if self.life_timer >= self.max_lifetime:
            self.kill()
            return

        self._update_target(enemies)
        if self.target is not None:
            self._home_to_target(delta_time)

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

    def _update_target(self, enemies):
        if self.target is not None:
            if self.target.is_alive() and self._distance_to(self.target) <= self.homing_radius * 1.5:
                return
            self.target = None

        nearest_enemy = None
        nearest_distance = self.homing_radius
        for enemy in enemies:
            if not enemy.is_alive():
                continue

            distance = self._distance_to(enemy)
            if distance < nearest_distance:
                nearest_enemy = enemy
                nearest_distance = distance

        self.target = nearest_enemy

    def _home_to_target(self, delta_time):
        desired_x = self.target.center_x - self.center_x
        desired_y = self.target.center_y - self.center_y
        dir_x, dir_y = self._normalize(desired_x, desired_y)
        desired_vx = dir_x * self.speed
        desired_vy = dir_y * self.speed

        steer_strength = min(1.0, self.turn_rate * delta_time)
        self.velocity_x += (desired_vx - self.velocity_x) * steer_strength
        self.velocity_y += (desired_vy - self.velocity_y) * steer_strength

        dir_x, dir_y = self._normalize(self.velocity_x, self.velocity_y)
        self.velocity_x = dir_x * self.speed
        self.velocity_y = dir_y * self.speed

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
        img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.ellipse((0, 0, 15, 15), fill=(200, 40, 30, 255))
        draw.ellipse((3, 3, 12, 12), fill=(255, 120, 40, 255))
        draw.ellipse((6, 6, 9, 9), fill=(255, 210, 120, 255))
        return arcade.Texture(img)

import math

import arcade
from PIL import Image, ImageDraw

from constants import COLOR_WARRIOR
from core import dices
from entities.player import Player


class Fighter(Player):
    def __init__(self, name="Воин"):
        stats = {
            "strength": 16,
            "dexterity": 12,
            "constitution": 16,
            "intelligence": 8,
            "wisdom": 10,
            "charisma": 10,
        }
        super().__init__(name, stats)
        self.class_name = "Воин"
        self.class_description = "Мастер клинка и щита. Вынослив и смертоносен в ближнем бою."
        self.color = COLOR_WARRIOR

        self.attack_range = 100
        self.attack_angle = 90
        self.attack_damage = 8
        self.speed = 1

        self.texture = self._create_texture()

    def _create_texture(self):
        img = Image.new("RGBA", (40, 40), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.rectangle([(0, 0), (39, 39)], fill=self.color, outline=(255, 255, 255), width=2)
        return arcade.Texture(img)

    def draw_preview(self, center_x, center_y):
        arcade.draw_lbwh_rectangle_filled(
            center_x - 40,
            center_y - 40,
            80,
            80,
            self.color,
        )

    def get_attack_targets(self, enemies, aim_x, aim_y):
        direction_x, direction_y = self._get_attack_direction(aim_x, aim_y)
        min_dot = math.cos(math.radians(self.attack_angle / 2))
        targets = []

        for enemy in enemies:
            if not enemy.is_alive():
                continue

            dx = enemy.center_x - self.center_x
            dy = enemy.center_y - self.center_y
            distance = math.hypot(dx, dy)

            if distance == 0 or distance > self.attack_range:
                continue

            enemy_dir_x = dx / distance
            enemy_dir_y = dy / distance
            dot = (direction_x * enemy_dir_x) + (direction_y * enemy_dir_y)
            if dot >= min_dot:
                targets.append(enemy)

        return targets

    def draw_attack_indicator(self, aim_x, aim_y):
        direction_x, direction_y = self._get_attack_direction(aim_x, aim_y)
        center_angle = math.degrees(math.atan2(direction_y, direction_x))
        half_angle = self.attack_angle / 2
        start_angle = center_angle - half_angle
        end_angle = center_angle + half_angle

        arcade.draw_arc_outline(
            self.center_x,
            self.center_y,
            self.attack_range * 2,
            self.attack_range * 2,
            arcade.color.WHITE,
            start_angle,
            end_angle,
            2,
        )

        left_radians = math.radians(start_angle)
        right_radians = math.radians(end_angle)
        arcade.draw_line(
            self.center_x,
            self.center_y,
            self.center_x + (math.cos(left_radians) * self.attack_range),
            self.center_y + (math.sin(left_radians) * self.attack_range),
            arcade.color.WHITE,
            2,
        )
        arcade.draw_line(
            self.center_x,
            self.center_y,
            self.center_x + (math.cos(right_radians) * self.attack_range),
            self.center_y + (math.sin(right_radians) * self.attack_range),
            arcade.color.WHITE,
            2,
        )

    def get_attack_damage(self):
        total_damage = dices.roll_dice(self.attack_damage, self.get_modifier("strength"))
        return max(1, total_damage)

    def get_attack_modifier(self):
        return self.get_modifier("strength")

    def _get_attack_direction(self, aim_x, aim_y):
        dx = aim_x - self.center_x
        dy = aim_y - self.center_y
        distance = math.hypot(dx, dy)
        if distance == 0:
            return 1.0, 0.0
        return dx / distance, dy / distance

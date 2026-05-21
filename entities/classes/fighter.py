import math

import arcade

from core import dices
from entities.player import Player


class Fighter(Player):
    CLASS_NAME = "Воин"
    CLASS_DESCRIPTION = "Мастер клинка и щита. Медленнее других, зато особенно хорош в ближнем бою."
    DEFAULT_STATS = {
        "strength": 16,
        "dexterity": 12,
        "constitution": 16,
        "intelligence": 8,
        "wisdom": 10,
        "charisma": 10,
    }
    PREVIEW_TEXTURE_NAME = "fighter/fighter.png"

    def __init__(self, name=CLASS_NAME):
        super().__init__(name, self.DEFAULT_STATS)
        self.class_name = self.CLASS_NAME
        self.class_description = self.CLASS_DESCRIPTION
        self.attack_range = 100
        self.attack_angle = 90
        self.attack_damage = 8
        self.speed = 1

        self.set_class_texture(self.PREVIEW_TEXTURE_NAME)
        self.set_attack_animation(
            [
                {"texture_name": "fighter/fighter_attack_1.png", "body_height_override": self.base_body_height},
                {"texture_name": "fighter/fighter_attack_2.png", "body_height_override": self.base_body_height},
                {"texture_name": "fighter/fighter_attack_3.png", "body_height_override": self.base_body_height},
                {"texture_name": "fighter/fighter_attack.png", "body_height_override": self.base_body_height},
                {"texture_name": "fighter/fighter_attack.png", "body_height_override": self.base_body_height},
                {"texture_name": "fighter/fighter_attack_3.png", "body_height_override": self.base_body_height},
                {"texture_name": "fighter/fighter_attack_2.png", "body_height_override": self.base_body_height},
                {"texture_name": "fighter/fighter_attack_1.png", "body_height_override": self.base_body_height},
            ],
            duration=0.42,
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
            if (direction_x * enemy_dir_x) + (direction_y * enemy_dir_y) >= min_dot:
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

        for angle in (start_angle, end_angle):
            radians = math.radians(angle)
            arcade.draw_line(
                self.center_x,
                self.center_y,
                self.center_x + (math.cos(radians) * self.attack_range),
                self.center_y + (math.sin(radians) * self.attack_range),
                arcade.color.WHITE,
                2,
            )

    def get_attack_damage(self):
        return max(1, dices.roll_dice(self.attack_damage, self.get_modifier("strength")))

    def get_attack_modifier(self):
        return self.get_modifier("strength")

    def _get_attack_direction(self, aim_x, aim_y):
        dx = aim_x - self.center_x
        dy = aim_y - self.center_y
        distance = math.hypot(dx, dy)
        if distance == 0:
            return 1.0, 0.0
        return dx / distance, dy / distance

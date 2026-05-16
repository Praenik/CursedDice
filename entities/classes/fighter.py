import math

import arcade

from core import dices
from entities.player import Player


class Fighter(Player):
    CLASS_NAME = "\u0412\u043e\u0438\u043d"
    CLASS_DESCRIPTION = (
        "\u041c\u0430\u0441\u0442\u0435\u0440 \u043a\u043b\u0438\u043d\u043a\u0430 \u0438 \u0449\u0438\u0442\u0430. "
        "\u0412\u044b\u043d\u043e\u0441\u043b\u0438\u0432 \u0438 \u0441\u043c\u0435\u0440\u0442\u043e\u043d\u043e\u0441\u0435\u043d "
        "\u0432 \u0431\u043b\u0438\u0436\u043d\u0435\u043c \u0431\u043e\u044e."
    )
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

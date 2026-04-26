import arcade
from PIL import Image, ImageDraw

from constants import COLOR_RANGER
from core import dices
from entities.player import Player
from entities.projectiles.arrow import Arrow


class Ranger(Player):
    def __init__(self, name="Следопыт"):
        stats = {
            "strength": 12,
            "dexterity": 16,
            "constitution": 14,
            "intelligence": 10,
            "wisdom": 14,
            "charisma": 8,
        }
        super().__init__(name, stats)
        self.class_name = "Следопыт"
        self.class_description = "Быстрый стрелок, который держит дистанцию и точно работает по одиночным целям."
        self.color = COLOR_RANGER

        self.attack_range = 180
        self.attack_damage = 8
        self.attack_cooldown = 0.4
        self.speed = 2.0

        self.texture = self._create_texture()

    def _create_texture(self):
        img = Image.new("RGBA", (40, 40), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        points = [(20, 5), (5, 35), (35, 35)]
        draw.polygon(points, fill=self.color, outline=(255, 255, 255))
        return arcade.Texture(img)

    def draw_preview(self, center_x, center_y):
        size = 50
        arcade.draw_triangle_filled(
            center_x,
            center_y + size,
            center_x - size,
            center_y - size,
            center_x + size,
            center_y - size,
            self.color,
        )

    def get_attack_damage(self):
        total_damage = dices.roll_dice(self.attack_damage, self.get_modifier("dexterity"))
        return total_damage

    def get_attack_modifier(self):
        return self.get_modifier("dexterity")

    def execute_attack(self, game_view, aim_x, aim_y):
        arrow = Arrow(
            self.center_x,
            self.center_y,
            aim_x,
            aim_y,
            self.get_attack_damage(),
            self.get_attack_modifier(),
        )
        game_view.player_projectiles.append(arrow)

    def draw_attack_indicator(self, aim_x, aim_y):
        return

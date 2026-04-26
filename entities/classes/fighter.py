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

    def get_attack_damage(self):
        total_damage = dices.roll_dice(self.attack_damage, self.get_modifier("strength"))
        return max(1, total_damage)

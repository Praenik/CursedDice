import arcade
from PIL import Image, ImageDraw

from constants import COLOR_RANGER
from entities.player import Player


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
        self.class_description = "Меткий стрелок и следопыт. Предпочитает дальний бой и скрытность."
        self.color = COLOR_RANGER
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

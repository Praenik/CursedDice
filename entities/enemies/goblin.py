import arcade
from PIL import Image, ImageDraw

from entities.enemy import Enemy


class Goblin(Enemy):
    def __init__(self, name="Гоблин"):
        super().__init__(
            name,
            {
                "strength": 8,
                "dexterity": 14,
                "constitution": 10,
                "intelligence": 8,
                "wisdom": 8,
                "charisma": 6,
            },
        )
        self.base_speed = 1
        self.detection_range = 250
        self.color = (100, 200, 100)
        self.texture = self._create_texture()

    def _create_texture(self):
        img = Image.new("RGBA", (30, 30), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.polygon([(15, 2), (28, 15), (15, 28), (2, 15)], fill=self.color, outline=(255, 255, 255), width=2)
        draw.ellipse([(9, 10), (13, 14)], fill=(255, 255, 255))
        draw.ellipse([(17, 10), (21, 14)], fill=(255, 255, 255))
        return arcade.Texture(img)

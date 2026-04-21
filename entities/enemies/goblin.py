from entities.enemy import Enemy
import arcade
from PIL import Image, ImageDraw


class Goblin(Enemy):
    """Гоблин — слабый, но быстрый враг."""

    def __init__(self, name="Гоблин"):
        stats = {
            'strength': 8,
            'dexterity': 14,
            'constitution': 10,
            'intelligence': 8,
            'wisdom': 8,
            'charisma': 6
        }
        super().__init__(name, stats)

        self.base_speed = 2.5  # Базовая скорость гоблина
        self.detection_range = 250
        self.wander_range = 120
        self.color = (100, 200, 100)  # Зелёный

        # Создаём текстуру
        self.texture = self._create_texture()

    def _create_texture(self):
        """Создаёт текстуру для гоблина (зелёный ромб)."""
        img = Image.new('RGBA', (30, 30), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Ромб
        points = [(15, 2), (28, 15), (15, 28), (2, 15)]
        draw.polygon(points, fill=self.color, outline=(255, 255, 255), width=2)

        # Глаза (две белые точки)
        draw.ellipse([(9, 10), (13, 14)], fill=(255, 255, 255))
        draw.ellipse([(17, 10), (21, 14)], fill=(255, 255, 255))

        return arcade.Texture(img)
from constants import COLOR_RANGER
from entities.player import Player
import arcade
from PIL import Image, ImageDraw


class Ranger(Player):
    """Следопыт — ловкий стрелок и знаток дикой природы."""

    def __init__(self, name="Следопыт"):
        stats = {
            'strength': 12,
            'dexterity': 16,
            'constitution': 14,
            'intelligence': 10,
            'wisdom': 14,
            'charisma': 8
        }
        super().__init__(name, stats)
        self.class_name = "Следопыт"
        self.class_description = "Меткий стрелок и следопыт. Предпочитает дальний бой и скрытность."
        self.color = COLOR_RANGER

        # Создаём текстуру
        self.texture = self._create_texture()

    def _create_texture(self):
        """Создаёт текстуру для класса (зелёный треугольник)."""
        img = Image.new('RGBA', (40, 40), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        points = [(20, 5), (5, 35), (35, 35)]
        draw.polygon(points, fill=self.color, outline=(255, 255, 255))
        return arcade.Texture(img)
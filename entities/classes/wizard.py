from constants import COLOR_WIZARD
from entities.player import Player
import arcade
from PIL import Image, ImageDraw


class Wizard(Player):
    """Волшебник — хрупкий, но владеющий разрушительной магией."""

    def __init__(self, name="Волшебник"):
        stats = {
            'strength': 8,
            'dexterity': 10,
            'constitution': 10,
            'intelligence': 16,
            'wisdom': 12,
            'charisma': 10
        }
        super().__init__(name, stats)
        self.class_name = "Волшебник"
        self.class_description = "Повелитель тайных знаний и магии. Хрупок, но способен уничтожать врагов заклинаниями."
        self.color = COLOR_WIZARD

        # Создаём текстуру
        self.texture = self._create_texture()

    def _create_texture(self):
        """Создаёт текстуру для класса (синий круг)."""
        img = Image.new('RGBA', (40, 40), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.ellipse([(5, 5), (34, 34)], fill=self.color, outline=(255, 255, 255), width=2)
        return arcade.Texture(img)
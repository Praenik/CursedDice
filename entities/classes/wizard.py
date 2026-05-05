import arcade
from PIL import Image, ImageDraw

from constants import COLOR_WIZARD
from core import dices
from entities.player import Player
from entities.projectiles.fireball import Fireball


class Wizard(Player):
    def __init__(self, name="Волшебник"):
        stats = {
            "strength": 8,
            "dexterity": 10,
            "constitution": 10,
            "intelligence": 16,
            "wisdom": 12,
            "charisma": 10,
        }
        super().__init__(name, stats)
        self.class_name = "Волшебник"
        self.class_description = "Повелитель тайных знаний и магии. Хрупок, но опасен на расстоянии."
        self.color = COLOR_WIZARD

        self.attack_damage = 6
        self.attack_cooldown = 0.5
        self.speed = 1.5

        self.texture = self._create_texture()

    def _create_texture(self):
        img = Image.new("RGBA", (40, 40), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.ellipse([(5, 5), (34, 34)], fill=self.color, outline=(255, 255, 255), width=2)
        return arcade.Texture(img)

    def draw_preview(self, center_x, center_y):
        arcade.draw_circle_filled(center_x, center_y, 40, self.color)

    def get_attack_damage(self):
        total_damage = dices.roll_dice(self.attack_damage, self.get_modifier("intelligence"))
        return total_damage

    def get_attack_modifier(self):
        return self.get_modifier("intelligence")

    def execute_attack(self, game_view, aim_x, aim_y):
        fireball = Fireball(
            self.center_x,
            self.center_y,
            aim_x,
            aim_y,
            self.get_attack_damage(),
            self.get_attack_modifier(),
            attacker=self,
            attack_disadvantage=self.consume_attack_disadvantage(),
        )
        game_view.player_projectiles.append(fireball)

    def draw_attack_indicator(self, aim_x, aim_y):
        return

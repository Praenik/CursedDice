from core import dices
from entities.player import Player
from entities.projectiles.fireball import Fireball


class Wizard(Player):
    CLASS_NAME = "Волшебник"
    CLASS_DESCRIPTION = "Хрупкий маг, зато его снаряд подруливает к целям и прощает не самый точный выстрел."
    DEFAULT_STATS = {
        "strength": 8,
        "dexterity": 10,
        "constitution": 10,
        "intelligence": 16,
        "wisdom": 12,
        "charisma": 10,
    }
    PREVIEW_TEXTURE_NAME = "wizard/wizard.png"

    def __init__(self, name=CLASS_NAME):
        super().__init__(name, self.DEFAULT_STATS)
        self.class_name = self.CLASS_NAME
        self.class_description = self.CLASS_DESCRIPTION
        self.attack_damage = 6
        self.attack_cooldown = 0.5
        self.speed = 1.5

        self.set_class_texture(self.PREVIEW_TEXTURE_NAME)
        self.set_attack_animation(
            [
                "wizard/wizard_attack_1.png",
                "wizard/wizard_attack_2.png",
            ]
        )

    def get_attack_damage(self):
        return dices.roll_dice(self.attack_damage, self.get_modifier("intelligence"))

    def get_attack_modifier(self):
        return self.get_modifier("intelligence")

    def execute_attack(self, game_view, aim_x, aim_y):
        self._spawn_projectile_attack(game_view, Fireball, aim_x, aim_y)

    def draw_attack_indicator(self, aim_x, aim_y):
        return

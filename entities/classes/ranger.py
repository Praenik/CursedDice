from core import dices
from entities.player import Player
from entities.projectiles.arrow import Arrow


class Ranger(Player):
    CLASS_NAME = "Следопыт"
    CLASS_DESCRIPTION = "Быстрый стрелок, который держит дистанцию и стабильно разбирает одиночные цели."
    DEFAULT_STATS = {
        "strength": 12,
        "dexterity": 16,
        "constitution": 14,
        "intelligence": 10,
        "wisdom": 14,
        "charisma": 8,
    }
    PREVIEW_TEXTURE_NAME = "ranger/ranger.png"

    def __init__(self, name=CLASS_NAME):
        super().__init__(name, self.DEFAULT_STATS)
        self.class_name = self.CLASS_NAME
        self.class_description = self.CLASS_DESCRIPTION
        self.attack_range = 180
        self.attack_damage = 8
        self.attack_cooldown = 0.4
        self.speed = 2.0

        self.set_class_texture(self.PREVIEW_TEXTURE_NAME)
        self.set_attack_animation(
            [
                "ranger/ranger_attack_1.png",
                "ranger/ranger_attack_2.png",
            ]
        )

    def get_attack_damage(self):
        return dices.roll_dice(self.attack_damage, self.get_modifier("dexterity"))

    def get_attack_modifier(self):
        return self.get_modifier("dexterity")

    def execute_attack(self, game_view, aim_x, aim_y):
        self._spawn_projectile_attack(game_view, Arrow, aim_x, aim_y)

    def draw_attack_indicator(self, aim_x, aim_y):
        return

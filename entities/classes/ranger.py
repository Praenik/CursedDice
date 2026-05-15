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
        self.attack_range = 180
        self.attack_damage = 8
        self.attack_cooldown = 0.4
        self.speed = 2.0

        self.set_class_texture("ranger/ranger.png")
        self.set_attack_animation(
            [
                {
                    "texture_name": "ranger/ranger_attack_1.png",
                    "body_height_override": self.base_body_height,
                    "match_base_texture_height": True,
                },
                {
                    "texture_name": "ranger/ranger_attack_2.png",
                    "body_height_override": self.base_body_height,
                    "match_base_texture_height": True,
                },
                {"texture_name": "ranger/ranger.png", "body_height_override": self.base_body_height},
                {
                    "texture_name": "ranger/ranger_attack_3.png",
                    "body_height_override": self.base_body_height,
                    "match_base_texture_height": True,
                },
                {
                    "texture_name": "ranger/ranger_attack.png",
                    "body_height_override": self.base_body_height,
                    "match_base_texture_height": True,
                },
                {
                    "texture_name": "ranger/ranger_attack.png",
                    "body_height_override": self.base_body_height,
                    "match_base_texture_height": True,
                },
                {
                    "texture_name": "ranger/ranger_attack_1.png",
                    "body_height_override": self.base_body_height,
                    "match_base_texture_height": True,
                },
                {
                    "texture_name": "ranger/ranger_attack_1.png",
                    "body_height_override": self.base_body_height,
                    "match_base_texture_height": True,
                },
            ],
            duration=0.36,
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
            attacker=self,
            attack_disadvantage=self.consume_attack_disadvantage(),
        )
        game_view.player_projectiles.append(arrow)

    def draw_attack_indicator(self, aim_x, aim_y):
        return

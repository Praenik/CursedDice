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
        self.attack_damage = 6
        self.attack_cooldown = 0.5
        self.speed = 1.5

        self.set_class_texture("wizard/wizard.png")
        self.set_attack_animation(
            [
                {"texture_name": "wizard/wizard_attack_1.png", "body_height_override": self.base_body_height},
                {"texture_name": "wizard/wizard_attack_2.png", "body_height_override": self.base_body_height},
                {"texture_name": "wizard/wizard_attack_3.png", "body_height_override": self.base_body_height},
                {"texture_name": "wizard/wizard_attack.png", "body_height_override": self.base_body_height},
                {"texture_name": "wizard/wizard_attack.png", "body_height_override": self.base_body_height},
                {"texture_name": "wizard/wizard_attack_3.png", "body_height_override": self.base_body_height},
                {"texture_name": "wizard/wizard_attack_2.png", "body_height_override": self.base_body_height},
                {"texture_name": "wizard/wizard_attack_1.png", "body_height_override": self.base_body_height},
            ],
            duration=0.44,
        )

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

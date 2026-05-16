from core import dices
from entities.player import Player
from entities.projectiles.fireball import Fireball


class Wizard(Player):
    CLASS_NAME = "\u0412\u043e\u043b\u0448\u0435\u0431\u043d\u0438\u043a"
    CLASS_DESCRIPTION = (
        "\u041f\u043e\u0432\u0435\u043b\u0438\u0442\u0435\u043b\u044c \u0442\u0430\u0439\u043d\u044b\u0445 \u0437\u043d\u0430\u043d\u0438\u0439 "
        "\u0438 \u043c\u0430\u0433\u0438\u0438. \u0425\u0440\u0443\u043f\u043e\u043a, \u043d\u043e \u043e\u043f\u0430\u0441\u0435\u043d "
        "\u043d\u0430 \u0440\u0430\u0441\u0441\u0442\u043e\u044f\u043d\u0438\u0438."
    )
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

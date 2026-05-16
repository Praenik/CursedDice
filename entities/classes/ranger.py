from core import dices
from entities.player import Player
from entities.projectiles.arrow import Arrow


class Ranger(Player):
    CLASS_NAME = "\u0421\u043b\u0435\u0434\u043e\u043f\u044b\u0442"
    CLASS_DESCRIPTION = (
        "\u0411\u044b\u0441\u0442\u0440\u044b\u0439 \u0441\u0442\u0440\u0435\u043b\u043e\u043a, \u043a\u043e\u0442\u043e\u0440\u044b\u0439 "
        "\u0434\u0435\u0440\u0436\u0438\u0442 \u0434\u0438\u0441\u0442\u0430\u043d\u0446\u0438\u044e \u0438 \u0442\u043e\u0447\u043d\u043e "
        "\u0440\u0430\u0431\u043e\u0442\u0430\u0435\u0442 \u043f\u043e \u043e\u0434\u0438\u043d\u043e\u0447\u043d\u044b\u043c \u0446\u0435\u043b\u044f\u043c."
    )
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

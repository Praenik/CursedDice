import arcade
from PIL import Image, ImageDraw

from core import dices
from entities.enemy import Enemy

MISS_FEEDBACK_COLOR = (210, 210, 230)
MAGIC_FEEDBACK_COLOR = (255, 230, 120)


class Nilbog(Enemy):
    def __init__(self, name="Нильбог"):
        super().__init__(
            name,
            {
                "strength": 8,
                "dexterity": 14,
                "constitution": 10,
                "intelligence": 10,
                "wisdom": 8,
                "charisma": 15,
            },
        )
        self.base_speed = 1.15
        self.detection_range = 5000
        self.attack_cooldown = 3.5
        self.attack_range = 320
        self.color = (190, 70, 210)

        self.reversal_available = True
        self.nilbogism_save_dc = 12
        self.nilbogism_charm_duration = 0.5
        self.nilbogism_charm_speed_multiplier = 0.8
        self.mocking_word_save_dc = 12
        self.texture = self._create_texture()

    def resolve_attack(self, attack_bonus, damage, attacker=None, disadvantage=False):
        if self._nilbogism_blocks_attack(attacker):
            return False

        hit, attack_roll = self.is_hit_by(attack_bonus, disadvantage)
        if not hit:
            self.show_combat_feedback(f"{attack_roll}/{self.get_armor_class()}", MISS_FEEDBACK_COLOR)
            return False

        if self._try_reversal_of_fortune():
            return False

        self.take_damage(damage)
        self.show_combat_feedback(f"-{damage}", (255, 120, 120))
        return True

    def attack_player(self, player, enemies_list=None):
        if self.attack_timer > 0:
            return

        wisdom_save = dices.roll_d20(player.get_modifier("wisdom"))
        if wisdom_save < self.mocking_word_save_dc:
            damage = dices.roll_dice(4) + dices.roll_dice(4)
            player.take_damage(damage)
            player.add_attack_disadvantage()
            player.show_combat_feedback(f"-{damage}", (210, 110, 255))
            self.show_combat_feedback("Mocking Word", MAGIC_FEEDBACK_COLOR)
        else:
            player.show_combat_feedback(f"{wisdom_save}/{self.mocking_word_save_dc}", MISS_FEEDBACK_COLOR)

        self.attack_timer = self.attack_cooldown

    def _nilbogism_blocks_attack(self, attacker):
        if attacker is None:
            return False

        charisma_save = dices.roll_d20(attacker.get_modifier("charisma"))
        if charisma_save >= self.nilbogism_save_dc:
            return False

        attacker.charm(self, self.nilbogism_charm_duration, self.nilbogism_charm_speed_multiplier)
        attacker.show_combat_feedback("Очарован", (255, 220, 120))

        self.show_combat_feedback("Nilbogism", MAGIC_FEEDBACK_COLOR)
        return True

    def _try_reversal_of_fortune(self):
        if not self.reversal_available or self.current_hp >= self.max_hp:
            return False

        self.reversal_available = False
        previous_hp = self.current_hp
        self.heal(dices.roll_dice(6))
        healed = self.current_hp - previous_hp
        self.show_combat_feedback(f"0 +{healed}", (120, 255, 170))
        return True

    def _create_texture(self):
        img = Image.new("RGBA", (34, 38), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        outline = (255, 255, 255)
        face = (115, 200, 95)
        crown = (245, 205, 75)
        robe = self.color
        eye = (35, 25, 45)

        draw.polygon([(6, 13), (10, 3), (16, 11), (22, 3), (28, 13)], fill=crown, outline=outline)
        draw.ellipse([(5, 10), (29, 33)], fill=face, outline=outline, width=2)
        draw.polygon([(7, 25), (27, 25), (31, 37), (3, 37)], fill=robe, outline=outline)
        draw.ellipse([(10, 18), (14, 22)], fill=eye)
        draw.ellipse([(20, 18), (24, 22)], fill=eye)
        draw.arc([(12, 21), (23, 30)], 10, 170, fill=eye, width=2)
        draw.polygon([(4, 19), (0, 15), (5, 24)], fill=face, outline=outline)
        draw.polygon([(30, 19), (34, 15), (29, 24)], fill=face, outline=outline)

        return arcade.Texture(img)

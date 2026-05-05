import arcade
from PIL import Image, ImageDraw

from core import dices
from entities.enemy import Enemy
from entities.projectiles.bugbear_boulder import BugbearBoulder


class Bugbear(Enemy):
    def __init__(self, name="Багбир"):
        stats = {
            "strength": 17,
            "dexterity": 14,
            "constitution": 14,
            "intelligence": 11,
            "wisdom": 12,
            "charisma": 11,
        }
        super().__init__(name, stats)

        self.base_hp = 30
        self.max_hp = self.base_hp + self.get_modifier("constitution")
        self.current_hp = self.max_hp

        self.base_speed = 1.25
        self.detection_range = 520
        self.attack_cooldown = 2.6
        self.attack_range = 70
        self.ranged_attack_range = 520
        self.ranged_attack_cooldown = 10.0
        self.ranged_attack_timer = 0.0
        self.color = (135, 95, 55)
        self.texture = self._create_texture()

    def attack_player(self, player):
        if self.attack_timer > 0:
            return

        damage = dices.roll_dice(6) + dices.roll_dice(6)
        player.resolve_attack(self.get_attack_modifier(), damage)
        self.attack_timer = self.attack_cooldown

    def update_ranged_attack(self, delta_time, player, projectile_list):
        if self.ranged_attack_timer > 0:
            self.ranged_attack_timer -= delta_time

        if (
            self.ranged_attack_timer > 0
            or not self.is_alive()
            or not player.is_alive()
            or self._distance_to(player) > self.ranged_attack_range
        ):
            return

        projectile_list.append(
            BugbearBoulder(
                self.center_x,
                self.center_y,
                player.center_x,
                player.center_y,
            )
        )
        self.ranged_attack_timer = self.ranged_attack_cooldown
        self.show_combat_feedback("Бросок", (255, 220, 120))

    def _create_texture(self):
        img = Image.new("RGBA", (58, 58), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        outline = (245, 235, 220)
        fur = self.color
        dark_fur = (75, 55, 40)
        armor = (70, 80, 90)
        eye = (245, 210, 80)

        draw.ellipse((8, 14, 50, 54), fill=fur, outline=outline, width=3)
        draw.ellipse((12, 6, 46, 40), fill=fur, outline=outline, width=3)
        draw.polygon([(13, 12), (5, 4), (9, 22)], fill=dark_fur, outline=outline)
        draw.polygon([(45, 12), (53, 4), (49, 22)], fill=dark_fur, outline=outline)

        draw.rectangle((14, 35, 44, 55), fill=armor, outline=outline, width=2)
        draw.ellipse((19, 20, 25, 26), fill=eye)
        draw.ellipse((33, 20, 39, 26), fill=eye)
        draw.polygon([(26, 28), (32, 28), (29, 33)], fill=(45, 30, 25))
        draw.line([(22, 37), (36, 37)], fill=(45, 30, 25), width=3)

        draw.line((5, 32, 0, 49), fill=dark_fur, width=5)
        draw.line((53, 32, 57, 49), fill=dark_fur, width=5)
        draw.line((0, 49, 10, 50), fill=outline, width=3)
        draw.line((57, 49, 47, 50), fill=outline, width=3)

        return arcade.Texture(img)

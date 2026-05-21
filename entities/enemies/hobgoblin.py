import arcade
from PIL import Image, ImageDraw

from core import dices
from entities.enemy import Enemy


class Hobgoblin(Enemy):
    def __init__(self, name="Хобгоблин"):
        super().__init__(
            name,
            {
                "strength": 13,
                "dexterity": 12,
                "constitution": 12,
                "intelligence": 10,
                "wisdom": 10,
                "charisma": 9,
            },
        )
        self.base_speed = 1.4
        self.detection_range = 290
        self.attack_damage = 8
        self.attack_cooldown = 2.7
        self.attack_range = 55
        self.martial_advantage_used = False
        self.martial_advantage_ally_range = 90
        self.current_enemies_list = None
        self.color = (165, 70, 45)
        self.texture = self._create_texture()

    def update(self, delta_time: float = 1 / 60, player=None, enemies_list=None):
        self.current_enemies_list = enemies_list
        super().update(delta_time, player, enemies_list)

    def attack_player(self, player):
        if self.attack_timer > 0:
            return

        hit, attack_roll = player.is_hit_by(self.get_attack_modifier())
        if hit:
            base_damage = dices.roll_dice(self.attack_damage)
            bonus_damage = self._get_martial_advantage_damage(player)
            total_damage = base_damage + bonus_damage
            player.take_damage(total_damage)
            player.show_combat_feedback(f"-{total_damage}", (255, 120, 120))
            if bonus_damage > 0:
                self.show_combat_feedback("+2d6", (255, 210, 110))
        else:
            player.show_combat_feedback(f"{attack_roll}/{player.get_armor_class()}", (210, 210, 230))

        self.attack_timer = self.attack_cooldown

    def _get_martial_advantage_damage(self, target):
        if self.martial_advantage_used or not self._has_ally_near_target(target):
            return 0

        self.martial_advantage_used = True
        return dices.roll_dice(6) + dices.roll_dice(6)

    def _has_ally_near_target(self, target):
        if self.current_enemies_list is None:
            return False

        for ally in self.current_enemies_list:
            if ally is self or not ally.is_alive():
                continue
            if arcade.get_distance_between_sprites(ally, target) <= self.martial_advantage_ally_range:
                return True

        return False

    def _create_texture(self):
        img = Image.new("RGBA", (36, 38), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        outline = (245, 245, 245)
        armor = (80, 90, 105)
        skin = self.color
        plume = (220, 35, 35)
        eye = (250, 230, 120)

        draw.rectangle([(9, 15), (27, 35)], fill=armor, outline=outline, width=2)
        draw.ellipse([(7, 6), (29, 27)], fill=skin, outline=outline, width=2)
        draw.rectangle([(10, 1), (26, 11)], fill=armor, outline=outline, width=2)
        draw.polygon([(14, 1), (18, -3), (22, 1)], fill=plume)
        draw.ellipse([(12, 15), (16, 19)], fill=eye)
        draw.ellipse([(20, 15), (24, 19)], fill=eye)
        draw.line([(13, 24), (23, 24)], fill=(35, 20, 20), width=2)
        draw.line([(4, 18), (0, 30)], fill=armor, width=3)
        draw.line([(32, 18), (35, 30)], fill=armor, width=3)
        draw.line([(4, 30), (10, 31)], fill=outline, width=2)
        draw.line([(35, 30), (28, 31)], fill=outline, width=2)

        return arcade.Texture(img)

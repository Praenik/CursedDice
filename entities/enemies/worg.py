import arcade
from PIL import Image, ImageDraw

from core import dices
from entities.enemy import Enemy


class Worg(Enemy):
    def __init__(self, name="Ворг"):
        super().__init__(
            name,
            {
                "strength": 16,
                "dexterity": 13,
                "constitution": 13,
                "intelligence": 7,
                "wisdom": 11,
                "charisma": 8,
            },
        )
        self.base_speed = 1.8
        self.detection_range = 320
        self.attack_damage = 8
        self.attack_cooldown = 2.2
        self.attack_range = 55
        self.bite_save_dc = 13
        self.bite_stun_duration = 1.0
        self.color = (85, 95, 105)
        self.texture = self._create_texture()

    def attack_player(self, player, enemies_list=None):
        if self.attack_timer > 0:
            return

        damage = dices.roll_dice(self.attack_damage)
        hit = player.resolve_attack(self.get_attack_modifier(), damage)
        if hit:
            strength_save = dices.roll_d20(player.get_modifier("strength"))
            if strength_save < self.bite_save_dc:
                player.stun(self.bite_stun_duration)

        self.attack_timer = self.attack_cooldown

    def _create_texture(self):
        img = Image.new("RGBA", (44, 30), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        outline = (235, 235, 235)
        shadow = (45, 50, 55)
        eye = (230, 55, 45)

        draw.ellipse([(6, 9), (33, 24)], fill=self.color, outline=outline, width=2)
        draw.polygon([(29, 8), (42, 15), (29, 22)], fill=self.color, outline=outline)
        draw.polygon([(30, 9), (34, 2), (36, 11)], fill=shadow, outline=outline)
        draw.polygon([(35, 11), (40, 6), (39, 15)], fill=shadow, outline=outline)
        draw.rectangle([(10, 21), (14, 28)], fill=shadow)
        draw.rectangle([(24, 21), (28, 28)], fill=shadow)
        draw.polygon([(7, 14), (1, 10), (6, 18)], fill=shadow, outline=outline)
        draw.ellipse([(34, 13), (37, 16)], fill=eye)
        draw.line([(39, 17), (42, 17)], fill=outline, width=1)

        return arcade.Texture(img)

import arcade

from entities.entity import Entity


class Player(Entity, arcade.Sprite):
    def __init__(self, name="Игрок", stats=None):
        Entity.__init__(self, name, stats)
        arcade.Sprite.__init__(self)

        self.class_name = "Авантюрист"
        self.class_description = ""
        self.speed = 3

        self.attack_range = 0
        self.attack_damage = 0
        self.attack_cooldown = 0.5
        self.attack_timer = 0.0
        self.is_attacking = False

    def update(self, delta_time: float = 1 / 60):
        if not self.is_alive():
            self.color = arcade.color.GRAY
            self.change_x = 0
            self.change_y = 0
            return

        super().update()

        if self.attack_timer > 0:
            self.attack_timer -= delta_time
            if self.attack_timer <= 0:
                self.is_attacking = False

    def attack(self):
        if self.can_attack():
            self.is_attacking = True
            self.attack_timer = self.attack_cooldown
            return True
        return False

    def can_attack(self):
        return self.attack_timer <= 0

    def get_attack_damage(self):
        return 0

    def get_attack_targets(self, enemies, aim_x, aim_y):
        targets = []
        for enemy in enemies:
            if not enemy.is_alive():
                continue
            if arcade.get_distance_between_sprites(self, enemy) <= self.attack_range:
                targets.append(enemy)
        return targets

    def draw_attack_indicator(self, aim_x, aim_y):
        arcade.draw_circle_outline(
            self.center_x,
            self.center_y,
            self.attack_range,
            arcade.color.WHITE,
            2,
        )

    def draw_preview(self, center_x, center_y):
        return

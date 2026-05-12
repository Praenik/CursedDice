import math

import arcade
from PIL import Image

from core.resources import resource_path
from entities.entity import Entity

PLAYER_TEXTURES_DIR = resource_path("assets", "textures", "player")
PLAYER_TEXTURE_MAX_SIZE = 84
PLAYER_PREVIEW_MAX_SIZE = 160


class Player(Entity, arcade.Sprite):
    def __init__(self, name="Игрок", stats=None):
        Entity.__init__(self, name, stats)
        arcade.Sprite.__init__(self)
        self.color = arcade.color.WHITE
        self.texture_right = None
        self.texture_left = None
        self.facing_direction = 1

        self.class_name = "Авантюрист"
        self.class_description = ""
        self.speed = 3

        self.attack_range = 0
        self.attack_damage = 0
        self.attack_cooldown = 0.5
        self.attack_timer = 0.0
        self.is_attacking = False
        self.stun_timer = 0.0
        self.charm_timer = 0.0
        self.charm_target = None
        self.charm_speed_multiplier = 1.0
        self.next_attack_disadvantage = False
        self.max_short_rest_charges = 2
        self.short_rest_charges = self.max_short_rest_charges
        self.max_long_rest_charges = 1
        self.long_rest_charges = self.max_long_rest_charges
        self.texture_name = None

    def update(self, delta_time: float = 1 / 60):
        self.update_combat_feedback(delta_time)
        self._update_stun(delta_time)
        self._update_charm(delta_time)

        if not self.is_alive():
            self.color = arcade.color.GRAY
            self.change_x = 0
            self.change_y = 0
            return

        if self.is_stunned():
            self.change_x = 0
            self.change_y = 0
            self.is_attacking = False
        elif self.is_charmed():
            self._apply_charm_movement()

        self._update_facing_direction()
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
        return self.attack_timer <= 0 and not self.is_stunned() and not self.is_charmed()

    def stun(self, duration):
        self.stun_timer = max(self.stun_timer, duration)
        self.is_attacking = False
        self.change_x = 0
        self.change_y = 0

    def is_stunned(self):
        return self.stun_timer > 0

    def _update_stun(self, delta_time):
        if self.stun_timer > 0:
            self.stun_timer = max(0.0, self.stun_timer - delta_time)

    def charm(self, target, duration, speed_multiplier):
        self.charm_target = target
        self.charm_timer = max(self.charm_timer, duration)
        self.charm_speed_multiplier = speed_multiplier
        self.is_attacking = False
        self.change_x = 0
        self.change_y = 0

    def is_charmed(self):
        return self.charm_timer > 0 and self.charm_target is not None

    def _update_charm(self, delta_time):
        if self.charm_target is not None and not self.charm_target.is_alive():
            self.charm_timer = 0.0
            self.charm_target = None
            self.charm_speed_multiplier = 1.0
            return

        if self.charm_timer > 0:
            self.charm_timer = max(0.0, self.charm_timer - delta_time)
            if self.charm_timer <= 0:
                self.charm_target = None
                self.charm_speed_multiplier = 1.0
        elif self.charm_target is not None:
            self.charm_target = None
            self.charm_speed_multiplier = 1.0

    def add_attack_disadvantage(self):
        self.next_attack_disadvantage = True

    def consume_attack_disadvantage(self):
        has_disadvantage = self.next_attack_disadvantage
        self.next_attack_disadvantage = False
        return has_disadvantage

    def use_short_rest(self):
        if not self._can_rest(self.short_rest_charges):
            return False

        heal_amount = math.ceil(self.max_hp / 2)
        healed = self._heal_from_rest(heal_amount)
        if healed <= 0:
            return False

        self.short_rest_charges -= 1
        self.show_combat_feedback(f"+{healed}", (120, 255, 170))
        return True

    def use_long_rest(self):
        if not self._can_rest(self.long_rest_charges):
            return False

        healed = self._heal_from_rest(self.max_hp)
        if healed <= 0:
            return False

        self.long_rest_charges -= 1
        self.show_combat_feedback(f"+{healed}", (120, 255, 170))
        return True

    def _can_rest(self, charges):
        return charges > 0 and self.is_alive() and self.current_hp < self.max_hp

    def _heal_from_rest(self, amount):
        previous_hp = self.current_hp
        self.heal(amount)
        return self.current_hp - previous_hp

    def _apply_charm_movement(self):
        dx = self.charm_target.center_x - self.center_x
        dy = self.charm_target.center_y - self.center_y
        distance = math.hypot(dx, dy)

        if distance == 0:
            self.change_x = 0
            self.change_y = 0
            return

        charm_speed = self.speed * self.charm_speed_multiplier
        self.change_x = (dx / distance) * charm_speed
        self.change_y = (dy / distance) * charm_speed
        self.is_attacking = False

    def get_attack_damage(self):
        return 0

    def get_attack_modifier(self):
        return 0

    def execute_attack(self, game_view, aim_x, aim_y):
        damage = self.get_attack_damage()
        attack_bonus = self.get_attack_modifier()
        disadvantage = self.consume_attack_disadvantage()
        targets = self.get_attack_targets(game_view.enemies_list, aim_x, aim_y)
        for enemy in targets:
            enemy.resolve_attack(attack_bonus, damage, attacker=self, disadvantage=disadvantage)

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
        preview_texture = self.texture_right or self.texture
        if not preview_texture:
            return

        preview_width, preview_height = self._get_scaled_dimensions(
            preview_texture.width,
            preview_texture.height,
            PLAYER_PREVIEW_MAX_SIZE,
        )
        arcade.draw_texture_rect(
            preview_texture,
            arcade.XYWH(center_x, center_y, preview_width, preview_height),
        )

    def set_class_texture(self, texture_name):
        texture_path = PLAYER_TEXTURES_DIR / texture_name
        self.texture_name = texture_name
        self.texture_right, self.texture_left = self._load_cropped_textures(texture_path)
        self.facing_direction = 1
        self.texture = self.texture_right
        self.sync_hit_box_to_texture()
        self.width, self.height = self._get_scaled_dimensions(
            self.texture.width,
            self.texture.height,
            PLAYER_TEXTURE_MAX_SIZE,
        )

    def _load_cropped_textures(self, texture_path):
        with Image.open(texture_path) as image:
            rgba_image = image.convert("RGBA")

        alpha_bbox = rgba_image.getchannel("A").getbbox()
        if alpha_bbox is not None:
            rgba_image = rgba_image.crop(alpha_bbox)

        right_image = rgba_image.copy()
        left_image = rgba_image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        return arcade.Texture(right_image), arcade.Texture(left_image)

    def _update_facing_direction(self):
        if self.change_x < 0:
            self._set_facing_direction(-1)
        elif self.change_x > 0:
            self._set_facing_direction(1)

    def _set_facing_direction(self, direction):
        if direction == self.facing_direction:
            return

        self.facing_direction = direction
        new_texture = self.texture_right if direction > 0 else self.texture_left
        if new_texture is None:
            return

        self.texture = new_texture
        self.sync_hit_box_to_texture()

    def _get_scaled_dimensions(self, width, height, max_size):
        largest_side = max(width, height)
        if largest_side <= 0:
            return width, height

        scale = max_size / largest_side
        return width * scale, height * scale

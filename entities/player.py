import math
from functools import lru_cache

import arcade
from PIL import Image

from core.resources import resource_path
from entities.entity import Entity

PLAYER_TEXTURES_DIR = resource_path("assets", "textures", "player")
PLAYER_DRAW_SIZE = 84
DEFAULT_PLAYER_NAME = "Игрок"
DEFAULT_CLASS_NAME = "Авантюрист"
HEAL_FEEDBACK_COLOR = (120, 255, 170)


@lru_cache(maxsize=None)
def load_player_textures(texture_name):
    texture_path = PLAYER_TEXTURES_DIR / texture_name
    if not texture_path.exists():
        raise FileNotFoundError(f"Player texture '{texture_name}' was not found in {PLAYER_TEXTURES_DIR}")

    with Image.open(texture_path) as image:
        rgba_image = image.convert("RGBA")

    return (
        arcade.Texture(rgba_image.copy()),
        arcade.Texture(rgba_image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)),
    )

class Player(Entity, arcade.Sprite):
    def __init__(self, name=DEFAULT_PLAYER_NAME, stats=None):
        Entity.__init__(self, name, stats)
        arcade.Sprite.__init__(self)

        self.color = arcade.color.WHITE
        self.texture_right = None
        self.texture_left = None
        self.attack_animation_frames = []
        self.facing_direction = 1

        self.class_name = DEFAULT_CLASS_NAME
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
            self._stop_motion()
            return

        if self.is_stunned():
            self._stop_action()
        elif self.is_charmed():
            self._apply_charm_movement()

        self._update_facing_direction()
        super().update()
        self._tick_attack_timer(delta_time)

    def attack(self):
        if not self.can_attack():
            return False

        self.is_attacking = True
        self.attack_timer = self.attack_cooldown
        return True

    def can_attack(self):
        return self.attack_timer <= 0 and not self.is_stunned() and not self.is_charmed()

    def stun(self, duration):
        self.stun_timer = max(self.stun_timer, duration)
        self._stop_action()

    def is_stunned(self):
        return self.stun_timer > 0

    def _update_stun(self, delta_time):
        if self.stun_timer > 0:
            self.stun_timer = max(0.0, self.stun_timer - delta_time)

    def charm(self, target, duration, speed_multiplier):
        self.charm_target = target
        self.charm_timer = max(self.charm_timer, duration)
        self.charm_speed_multiplier = speed_multiplier
        self._stop_action()

    def is_charmed(self):
        return self.charm_timer > 0 and self.charm_target is not None

    def _update_charm(self, delta_time):
        if self.charm_target is not None and not self.charm_target.is_alive():
            self._clear_charm()
            return

        if self.charm_timer > 0:
            self.charm_timer = max(0.0, self.charm_timer - delta_time)
            if self.charm_timer <= 0:
                self._clear_charm()
        elif self.charm_target is not None:
            self._clear_charm()

    def _clear_charm(self):
        self.charm_timer = 0.0
        self.charm_target = None
        self.charm_speed_multiplier = 1.0

    def add_attack_disadvantage(self):
        self.next_attack_disadvantage = True

    def consume_attack_disadvantage(self):
        had_disadvantage = self.next_attack_disadvantage
        self.next_attack_disadvantage = False
        return had_disadvantage

    def use_short_rest(self):
        if self.short_rest_charges <= 0 or not self.is_alive() or self.current_hp >= self.max_hp:
            return False

        old_hp = self.current_hp
        self.heal(math.ceil(self.max_hp / 2))
        self.short_rest_charges -= 1
        self.show_combat_feedback(f"+{self.current_hp - old_hp}", HEAL_FEEDBACK_COLOR)
        return True

    def use_long_rest(self):
        if self.long_rest_charges <= 0 or not self.is_alive() or self.current_hp >= self.max_hp:
            return False

        old_hp = self.current_hp
        self.heal(self.max_hp)
        self.long_rest_charges -= 1
        self.show_combat_feedback(f"+{self.current_hp - old_hp}", HEAL_FEEDBACK_COLOR)
        return True

    def _apply_charm_movement(self):
        dx = self.charm_target.center_x - self.center_x
        dy = self.charm_target.center_y - self.center_y
        distance = math.hypot(dx, dy)
        if distance == 0:
            self._stop_motion()
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

        for enemy in self.get_attack_targets(game_view.enemies_list, aim_x, aim_y):
            enemy.resolve_attack(attack_bonus, damage, attacker=self, disadvantage=disadvantage)

    def _spawn_projectile_attack(self, game_view, projectile_cls, aim_x, aim_y):
        game_view.player_projectiles.append(
            projectile_cls(
                self.center_x,
                self.center_y,
                aim_x,
                aim_y,
                self.get_attack_damage(),
                self.get_attack_modifier(),
                attacker=self,
                attack_disadvantage=self.consume_attack_disadvantage(),
            )
        )

    def get_attack_targets(self, enemies, aim_x, aim_y):
        targets = []
        for enemy in enemies:
            if enemy.is_alive() and arcade.get_distance_between_sprites(self, enemy) <= self.attack_range:
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

    def set_class_texture(self, texture_name):
        self.texture_name = texture_name
        self.texture_right, self.texture_left = load_player_textures(texture_name)
        self.facing_direction = 1
        self.texture = self.texture_right
        self.width = PLAYER_DRAW_SIZE
        self.height = PLAYER_DRAW_SIZE
        self.sync_hit_box_to_texture()

    def set_attack_animation(self, texture_names):
        self.attack_animation_frames = []
        for texture_name in texture_names:
            self.attack_animation_frames.append(load_player_textures(texture_name))

    def face_towards(self, target_x):
        if target_x < self.center_x:
            self._set_facing_direction(-1)
        elif target_x > self.center_x:
            self._set_facing_direction(1)

    def draw_current_frame(self):
        texture = self._get_current_draw_frame()
        if texture is None:
            return

        arcade.draw_texture_rect(
            texture,
            arcade.XYWH(self.center_x, self.center_y, self.width, self.height),
            color=self.color,
            angle=self._angle,
            pixelated=True,
        )

    def _update_facing_direction(self):
        if self.change_x < 0:
            self._set_facing_direction(-1)
        elif self.change_x > 0:
            self._set_facing_direction(1)

    def _set_facing_direction(self, direction):
        self.facing_direction = direction

    def _get_current_draw_frame(self):
        frame_index = self._get_attack_frame_index()
        if frame_index is not None:
            right_texture, left_texture = self.attack_animation_frames[frame_index]
            if self.facing_direction < 0:
                return left_texture
            return right_texture

        if self.facing_direction < 0:
            return self.texture_left
        return self.texture_right

    def _get_attack_frame_index(self):
        if not self.is_attacking or not self.attack_animation_frames:
            return None

        if self.attack_cooldown <= 0:
            return None

        elapsed = self.attack_cooldown - self.attack_timer
        if elapsed < 0 or elapsed > self.attack_cooldown:
            return None

        progress = min(1.0, max(0.0, elapsed / self.attack_cooldown))
        return min(int(progress * len(self.attack_animation_frames)), len(self.attack_animation_frames) - 1)

    def _tick_attack_timer(self, delta_time):
        if self.attack_timer <= 0:
            return

        self.attack_timer -= delta_time
        if self.attack_timer <= 0:
            self.is_attacking = False

    def _stop_motion(self):
        self.change_x = 0
        self.change_y = 0

    def _stop_action(self):
        self.is_attacking = False
        self._stop_motion()

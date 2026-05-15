import math
from functools import lru_cache
from pathlib import Path

import arcade
from PIL import Image

from core.resources import resource_path
from entities.entity import Entity

PLAYER_TEXTURES_DIR = resource_path("assets", "textures", "player")
PLAYER_TEXTURE_MAX_SIZE = 84
PLAYER_PREVIEW_MAX_SIZE = 160


@lru_cache(maxsize=None)
def resolve_player_texture_path(texture_name):
    texture_path = PLAYER_TEXTURES_DIR / texture_name
    if texture_path.exists():
        return texture_path

    fallback_name = Path(texture_name).name
    matches = sorted(PLAYER_TEXTURES_DIR.rglob(fallback_name))
    if len(matches) == 1:
        return matches[0]

    if not matches:
        raise FileNotFoundError(f"Player texture '{texture_name}' was not found in {PLAYER_TEXTURES_DIR}")

    raise FileNotFoundError(
        f"Player texture '{texture_name}' is ambiguous; matches: "
        + ", ".join(str(match.relative_to(PLAYER_TEXTURES_DIR)) for match in matches)
    )


@lru_cache(maxsize=None)
def load_player_texture_frame_data(texture_name):
    texture_path = resolve_player_texture_path(texture_name)
    with Image.open(texture_path) as image:
        rgba_image = image.convert("RGBA")

    alpha_bbox = rgba_image.getchannel("A").getbbox()
    if alpha_bbox is not None:
        rgba_image = rgba_image.crop(alpha_bbox)

    width, height = rgba_image.size
    body_center_x, body_height = _measure_body_metrics(rgba_image)
    body_delta_x = body_center_x - (width / 2)
    bottom_delta_y = (height - 1) - (height / 2)

    right_image = rgba_image.copy()
    left_image = rgba_image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    return (
        arcade.Texture(right_image),
        arcade.Texture(left_image),
        width,
        height,
        body_delta_x,
        bottom_delta_y,
        body_height,
    )


def load_player_texture_pair(texture_name):
    right_texture, left_texture, *_ = load_player_texture_frame_data(texture_name)
    return right_texture, left_texture


def _measure_body_metrics(rgba_image):
    width, height = rgba_image.size
    alpha = rgba_image.getchannel("A")
    body_top = int(height * 0.2)
    body_bottom = int(height * 0.82)
    column_counts = []
    max_count = 0

    for x in range(width):
        count = 0
        for y in range(body_top, body_bottom):
            if alpha.getpixel((x, y)) > 0:
                count += 1
        column_counts.append(count)
        if count > max_count:
            max_count = count

    if max_count <= 0:
        return width / 2, height

    threshold = max(8, int(max_count * 0.35))
    body_left, body_right = _select_body_column_span(column_counts, threshold, width)
    if body_left is None or body_right is None:
        return width / 2, height

    body_center_x = (body_left + body_right) / 2

    scan_half_width = max(8, int((body_right - body_left) * 0.18))
    scan_left = max(0, int(body_center_x - scan_half_width))
    scan_right = min(width - 1, int(body_center_x + scan_half_width))
    row_counts = []
    max_row_count = 0

    for y in range(height):
        count = 0
        for x in range(scan_left, scan_right + 1):
            if alpha.getpixel((x, y)) > 0:
                count += 1
        row_counts.append(count)
        if count > max_row_count:
            max_row_count = count

    if max_row_count <= 0:
        return body_center_x, height

    row_threshold = max(4, int(max_row_count * 0.22))
    dense_rows = [index for index, count in enumerate(row_counts) if count >= row_threshold]
    if not dense_rows:
        return body_center_x, height

    body_height = dense_rows[-1] - dense_rows[0] + 1
    return body_center_x, body_height


def _select_body_column_span(column_counts, threshold, width):
    best_span = None
    run_start = None
    image_center_x = width / 2

    for index, count in enumerate(column_counts):
        is_dense = count >= threshold
        if is_dense and run_start is None:
            run_start = index

        is_last_column = index == len(column_counts) - 1
        if (not is_dense or is_last_column) and run_start is not None:
            run_end = index if is_dense and is_last_column else index - 1
            span_center_x = (run_start + run_end) / 2
            span_density = sum(column_counts[run_start : run_end + 1])
            center_distance = abs(span_center_x - image_center_x)
            score = span_density - (center_distance * 0.5)
            candidate = (score, run_start, run_end)
            if best_span is None or candidate[0] > best_span[0]:
                best_span = candidate
            run_start = None

    if best_span is None:
        return None, None

    return best_span[1], best_span[2]


class Player(Entity, arcade.Sprite):
    def __init__(self, name="Игрок", stats=None):
        Entity.__init__(self, name, stats)
        arcade.Sprite.__init__(self)
        self.color = arcade.color.WHITE
        self.texture_right = None
        self.texture_left = None
        self.attack_animation_frames = []
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
        self.attack_animation_duration = 0.18
        self.max_short_rest_charges = 2
        self.short_rest_charges = self.max_short_rest_charges
        self.max_long_rest_charges = 1
        self.long_rest_charges = self.max_long_rest_charges
        self.texture_name = None
        self.base_texture_frame_height = 0.0
        self.base_body_delta_x = 0.0
        self.base_bottom_delta_y = 0.0
        self.base_body_height = 0.0
        self.base_body_draw_height = 0.0

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
            pixelated=True,
        )

    def set_class_texture(self, texture_name):
        self.texture_name = texture_name
        (
            self.texture_right,
            self.texture_left,
            texture_width,
            texture_height,
            self.base_body_delta_x,
            self.base_bottom_delta_y,
            self.base_body_height,
        ) = load_player_texture_frame_data(texture_name)
        self.facing_direction = 1
        self.texture = self.texture_right
        self.sync_hit_box_to_texture()
        self.width, self.height = self._get_scaled_dimensions(
            texture_width,
            texture_height,
            PLAYER_TEXTURE_MAX_SIZE,
        )
        self.base_texture_frame_height = texture_height
        texture_scale = self.height / texture_height if texture_height > 0 else 1.0
        self.base_body_draw_height = self.base_body_height * texture_scale

    def set_attack_texture(self, texture_name):
        self.set_attack_animation([texture_name])

    def set_attack_animation(self, texture_names, duration=None):
        self.attack_animation_frames = []
        for frame_config in texture_names:
            body_height_override = None
            scale_adjust = 1.0
            match_base_texture_height = False
            if isinstance(frame_config, str):
                texture_name = frame_config
            else:
                texture_name = frame_config["texture_name"]
                body_height_override = frame_config.get("body_height_override")
                match_base_texture_height = frame_config.get("match_base_texture_height", False)

            (
                right_texture,
                left_texture,
                _width,
                _height,
                body_delta_x,
                bottom_delta_y,
                body_height,
            ) = load_player_texture_frame_data(texture_name)
            if match_base_texture_height and _height > 0 and self.base_texture_frame_height > 0:
                scale_adjust *= self.base_texture_frame_height / _height
            offset_x = self.base_body_delta_x - body_delta_x
            offset_y = self.base_bottom_delta_y - bottom_delta_y
            self.attack_animation_frames.append(
                {
                    "right_texture": right_texture,
                    "left_texture": left_texture,
                    "offset_x": offset_x,
                    "offset_y": offset_y,
                    "body_height": body_height if body_height_override is None else body_height_override,
                    "scale_adjust": scale_adjust,
                }
            )

        if duration is not None:
            self.attack_animation_duration = duration

    def face_towards(self, target_x):
        if target_x < self.center_x:
            self._set_facing_direction(-1)
        elif target_x > self.center_x:
            self._set_facing_direction(1)

    def draw_current_frame(self):
        texture, offset_x, offset_y, body_height, scale_adjust = self._get_current_draw_frame()
        if texture is None:
            return

        if texture.height <= 0:
            return

        if body_height > 0 and self.base_body_draw_height > 0:
            draw_scale = self.base_body_draw_height / body_height
        else:
            draw_scale = self.height / texture.height
        draw_scale *= scale_adjust
        draw_width = texture.width * draw_scale
        draw_height = texture.height * draw_scale
        arcade.draw_texture_rect(
            texture,
            arcade.XYWH(
                self.center_x + (offset_x * draw_scale),
                self.center_y + (offset_y * draw_scale),
                draw_width,
                draw_height,
            ),
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
            frame = self.attack_animation_frames[frame_index]
            if self.facing_direction < 0 and frame["left_texture"] is not None:
                return (
                    frame["left_texture"],
                    -frame["offset_x"],
                    frame["offset_y"],
                    frame["body_height"],
                    frame["scale_adjust"],
                )
            return (
                frame["right_texture"],
                frame["offset_x"],
                frame["offset_y"],
                frame["body_height"],
                frame["scale_adjust"],
            )

        if self.facing_direction < 0 and self.texture_left is not None:
            return self.texture_left, 0.0, 0.0, self.base_body_height, 1.0
        return self.texture_right or self.texture, 0.0, 0.0, self.base_body_height, 1.0

    def _get_attack_frame_index(self):
        if not self.is_attacking or not self.attack_animation_frames:
            return None

        active_duration = min(self.attack_animation_duration, self.attack_cooldown)
        if active_duration <= 0:
            return None

        elapsed = self.attack_cooldown - self.attack_timer
        if elapsed < 0 or elapsed > active_duration:
            return None

        progress = min(1.0, max(0.0, elapsed / active_duration))
        frame_index = min(int(progress * len(self.attack_animation_frames)), len(self.attack_animation_frames) - 1)
        return frame_index

    def _get_scaled_dimensions(self, width, height, max_size):
        largest_side = max(width, height)
        if largest_side <= 0:
            return width, height

        scale = max_size / largest_side
        return width * scale, height * scale

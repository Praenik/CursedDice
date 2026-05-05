import math
import random

import arcade

from core import dices
from entities.entity import Entity


class Enemy(Entity, arcade.Sprite):
    def __init__(self, name="Враг", stats=None):
        Entity.__init__(self, name, stats)
        arcade.Sprite.__init__(self)

        self.base_speed = 0.8
        self.detection_range = 300
        self.current_speed = self.base_speed * 0.5

        self.attack_damage = 6
        self.attack_cooldown = 3.0
        self.attack_timer = 0.0
        self.attack_range = 50

        self.is_dying = False
        self.death_timer = 0.0
        self.death_duration = 1.0

        self.spawn_x = 0
        self.spawn_y = 0
        self.state = "wander"
        self.is_aggroed = False

        self.wander_timer = 0
        self.wander_direction = (0, 0)

    def setup(self, x, y):
        self.spawn_x = x
        self.spawn_y = y
        self.center_x = x
        self.center_y = y

    def update(self, delta_time: float = 1 / 60, player=None, enemies_list=None):
        self.update_combat_feedback(delta_time)

        if player and not player.is_alive():
            self.change_x = 0
            self.change_y = 0
            self.color = arcade.color.GRAY
            return

        if not self.is_alive():
            self.change_x = 0
            self.change_y = 0

            if not self.is_dying:
                self.is_dying = True
                self.death_timer = self.death_duration
                self.color = arcade.color.GRAY

            if self.is_dying:
                self.death_timer -= delta_time
                if self.death_timer <= 0:
                    self.kill()

            super().update()
            return

        self.change_x = 0
        self.change_y = 0

        if self.attack_timer > 0:
            self.attack_timer -= delta_time

        if player and player.is_alive():
            distance = arcade.get_distance_between_sprites(self, player)
            if distance <= self.attack_range and self.attack_timer <= 0:
                self.attack_player(player)

        if player is not None:
            distance_to_player = self._distance_to(player)
            distance_to_spawn = self._distance_to_point(self.spawn_x, self.spawn_y)

            if self.is_aggroed or distance_to_player <= self.detection_range:
                self.state = "chase"
            elif self.state == "chase" and distance_to_player > self.detection_range * 1.2:
                self.state = "return"
            elif self.state == "return" and distance_to_spawn < 10:
                self.state = "wander"

            if self.state == "chase":
                self.current_speed = self.base_speed
                self._move_towards_point(player.center_x, player.center_y)
            elif self.state == "return":
                self.current_speed = self.base_speed * 2.0
                self._move_towards_point(self.spawn_x, self.spawn_y)
            else:
                self.current_speed = self.base_speed * 0.5
                self._wander(delta_time)

        if enemies_list is not None:
            self._apply_separation_from_enemies(enemies_list)

        if player is not None:
            self._apply_separation_from_player(player)

        super().update(delta_time)

    def attack_player(self, player):
        if self.attack_timer <= 0:
            damage = dices.roll_dice(self.attack_damage)
            player.resolve_attack(self.get_attack_modifier(), damage)
            self.attack_timer = self.attack_cooldown

    def take_damage(self, damage):
        previous_hp = self.current_hp
        is_dead = super().take_damage(damage)
        if self.current_hp < previous_hp:
            self._aggro_from_damage()
        return is_dead

    def _aggro_from_damage(self):
        self.is_aggroed = True
        self.state = "chase"

    def get_attack_modifier(self):
        return self.get_modifier("strength")

    def _apply_separation_from_enemies(self, enemies_list):
        for other in enemies_list:
            if other is self:
                continue

            dx = self.center_x - other.center_x
            dy = self.center_y - other.center_y
            distance = math.sqrt(dx ** 2 + dy ** 2)

            min_distance = (self.width / 2 + other.width / 2) + 5
            if 0 < distance < min_distance:
                dx /= distance
                dy /= distance
                strength = (min_distance - distance) * 0.5
                self.change_x += dx * strength
                self.change_y += dy * strength

    def _apply_separation_from_player(self, player):
        dx = self.center_x - player.center_x
        dy = self.center_y - player.center_y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        min_distance = (self.width / 2 + player.width / 2) + 10
        if 0 < distance < min_distance:
            dx /= distance
            dy /= distance
            strength = (min_distance - distance) * 1.5
            self.change_x += dx * strength
            self.change_y += dy * strength

    def _distance_to(self, other):
        dx = other.center_x - self.center_x
        dy = other.center_y - self.center_y
        return math.sqrt(dx ** 2 + dy ** 2)

    def _distance_to_point(self, x, y):
        dx = x - self.center_x
        dy = y - self.center_y
        return math.sqrt(dx ** 2 + dy ** 2)

    def _move_towards_point(self, target_x, target_y):
        dx = target_x - self.center_x
        dy = target_y - self.center_y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance > 0:
            dx /= distance
            dy /= distance
            self.change_x += dx * self.current_speed
            self.change_y += dy * self.current_speed

    def _wander(self, delta_time):
        self.wander_timer -= delta_time

        if self.wander_timer <= 0:
            angle = random.uniform(0, 2 * math.pi)
            self.wander_direction = (math.cos(angle), math.sin(angle))
            self.wander_timer = random.uniform(1.0, 2.0)

        wander_speed = self.base_speed * 0.5
        self.change_x += self.wander_direction[0] * wander_speed
        self.change_y += self.wander_direction[1] * wander_speed

    def draw_health_bar(self):
        if not self.is_alive():
            return

        bar_width = 40
        bar_height = 6
        y_offset = 35

        health_percent = max(0, self.current_hp) / self.max_hp
        current_bar_width = bar_width * health_percent

        arcade.draw_rect_filled(
            arcade.XYWH(self.center_x, self.center_y + y_offset, bar_width, bar_height),
            arcade.color.RED,
        )

        if current_bar_width > 0:
            left_edge = self.center_x - (bar_width / 2)
            green_center_x = left_edge + (current_bar_width / 2)
            arcade.draw_rect_filled(
                arcade.XYWH(green_center_x, self.center_y + y_offset, current_bar_width, bar_height),
                arcade.color.GREEN,
            )

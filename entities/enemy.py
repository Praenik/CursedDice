from entities.entity import Entity
import arcade
import math
import random


class Enemy(Entity, arcade.Sprite):
    """Базовый класс для всех врагов."""

    def __init__(self, name="Враг", stats=None):
        Entity.__init__(self, name, stats)
        arcade.Sprite.__init__(self)

        self.base_speed = 2
        self.detection_range = 300
        self.wander_range = 100
        self.current_speed = self.base_speed * 0.5

        self.spawn_x = 0
        self.spawn_y = 0
        self.state = "wander"

        self.wander_timer = 0
        self.wander_direction = (0, 0)

    def setup(self, x, y):
        self.spawn_x = x
        self.spawn_y = y
        self.center_x = x
        self.center_y = y

    def update(self, delta_time: float = 1 / 60, player=None, enemies_list=None):
        # Сбрасываем скорость
        self.change_x = 0
        self.change_y = 0

        if player is not None:
            distance_to_player = self._distance_to(player)
            distance_to_spawn = self._distance_to_point(self.spawn_x, self.spawn_y)

            # Логика смены состояний
            if distance_to_player <= self.detection_range:
                self.state = "chase"
            elif self.state == "chase" and distance_to_player > self.detection_range * 1.2:
                self.state = "return"
            elif self.state == "return" and distance_to_spawn < 10:
                self.state = "wander"

            # Устанавливаем скорость в зависимости от состояния
            if self.state == "chase":
                self.current_speed = self.base_speed
                self._move_towards_player(player)
            elif self.state == "return":
                self.current_speed = self.base_speed * 2.0
                self._move_towards_point(self.spawn_x, self.spawn_y)
            else:  # wander
                self.current_speed = self.base_speed * 0.5
                self._wander(delta_time)

        # Расталкивание с другими врагами
        if enemies_list is not None:
            self._apply_separation_from_enemies(enemies_list)

        # Расталкивание с игроком (враг отступает, игрока не толкает)
        if player is not None:
            self._apply_separation_from_player(player)

        super().update(delta_time)

    def _apply_separation_from_enemies(self, enemies_list):
        """Враг отталкивается от других врагов."""
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
        """Враг отталкивается от игрока (игрок остаётся на месте)."""
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

    def _distance_to(self, other) -> float:
        dx = other.center_x - self.center_x
        dy = other.center_y - self.center_y
        return math.sqrt(dx ** 2 + dy ** 2)

    def _distance_to_point(self, x, y) -> float:
        dx = x - self.center_x
        dy = y - self.center_y
        return math.sqrt(dx ** 2 + dy ** 2)

    def _move_towards_player(self, player):
        self._move_towards_point(player.center_x, player.center_y)

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
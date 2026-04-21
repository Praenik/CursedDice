from entities.entity import Entity
import arcade
import math
import random


class Enemy(Entity, arcade.Sprite):
    """Базовый класс для всех врагов."""

    def __init__(self, name="Враг", stats=None):
        Entity.__init__(self, name, stats)
        arcade.Sprite.__init__(self)

        self.base_speed = 2  # Базовая скорость (переопределяется в дочерних классах)
        self.detection_range = 300  # Радиус обнаружения игрока
        self.wander_range = 100  # Радиус блуждания от точки спавна

        # Текущая скорость
        self.current_speed = self.base_speed * 0.5  # Начинаем с блуждания

        self.spawn_x = 0
        self.spawn_y = 0

        self.state = "wander"  # "wander", "chase", "return"

        self.wander_timer = 0
        self.wander_direction = (0, 0)

    def setup(self, x, y):
        """Устанавливает точку спавна."""
        self.spawn_x = x
        self.spawn_y = y
        self.center_x = x
        self.center_y = y

    def update(self, delta_time: float = 1 / 60, player=None):
        """Обновление состояния врага."""
        super().update()

        if player is None:
            return

        distance_to_player = self._distance_to(player)
        distance_to_spawn = self._distance_to_point(self.spawn_x, self.spawn_y)

        # Логика смены состояний
        if distance_to_player <= self.detection_range:
            self.state = "chase"
        elif self.state == "chase" and distance_to_player > self.detection_range * 1.2:
            # Потеряли игрока — возвращаемся к точке спавна
            self.state = "return"
        elif self.state == "return" and distance_to_spawn < 10:
            # Вернулись к спавну — снова блуждаем
            self.state = "wander"

        # Устанавливаем скорость в зависимости от состояния
        if self.state == "chase":
            self.current_speed = self.base_speed  # 100%
            self._move_towards_player(player)
        elif self.state == "return":
            self.current_speed = self.base_speed * 2.0  # 200%
            self._move_towards_point(self.spawn_x, self.spawn_y)
        else:  # wander
            self.current_speed = self.base_speed * 0.5  # 50%
            self._wander(delta_time)

    def _distance_to(self, other) -> float:
        """Расстояние до другого спрайта."""
        dx = other.center_x - self.center_x
        dy = other.center_y - self.center_y
        return math.sqrt(dx ** 2 + dy ** 2)

    def _distance_to_point(self, x, y) -> float:
        """Расстояние до точки."""
        dx = x - self.center_x
        dy = y - self.center_y
        return math.sqrt(dx ** 2 + dy ** 2)

    def _move_towards_player(self, player):
        """Движение в сторону игрока."""
        self._move_towards_point(player.center_x, player.center_y)

    def _move_towards_point(self, target_x, target_y):
        """Движение в сторону указанной точки."""
        dx = target_x - self.center_x
        dy = target_y - self.center_y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance > 0:
            dx /= distance
            dy /= distance

            self.change_x = dx * self.current_speed
            self.change_y = dy * self.current_speed
        else:
            self.change_x = 0
            self.change_y = 0

    def _wander(self, delta_time):
        """Блуждание — случайное движение без оглядки на точку спавна."""
        self.wander_timer -= delta_time

        if self.wander_timer <= 0:
            angle = random.uniform(0, 2 * math.pi)
            self.wander_direction = (math.cos(angle), math.sin(angle))
            self.wander_timer = random.uniform(1.0, 2.0)

        wander_speed = self.base_speed * 0.5
        self.change_x = self.wander_direction[0] * wander_speed
        self.change_y = self.wander_direction[1] * wander_speed
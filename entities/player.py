from entities.entity import Entity
import arcade


class Player(Entity, arcade.Sprite):
    """Базовый класс игрока — объединяет Entity и Sprite."""

    def __init__(self, name="Игрок", stats=None):
        Entity.__init__(self, name, stats)
        arcade.Sprite.__init__(self)

        self.class_name = "Авантюрист"
        self.class_description = ""
        self.speed = 3

        # Параметры атаки (переопределяются в дочерних классах)
        self.attack_range = 0
        self.attack_damage = 0
        self.attack_cooldown = 0.5
        self.attack_timer = 0.0
        self.is_attacking = False

    def update(self, delta_time: float = 1 / 60):
        """Обновление состояния."""
        if not self.is_alive():
            self.color = arcade.color.GRAY
            self.change_x = 0
            self.change_y = 0
            return

        super().update()

        # Обновление таймера атаки
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
        """Проверяет, можно ли атаковать."""
        return self.attack_timer <= 0

    def get_attack_damage(self):
        """Рассчитывает урон атаки. Переопределяется в дочерних классах."""
        return 0
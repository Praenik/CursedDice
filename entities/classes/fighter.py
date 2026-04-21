from constants import COLOR_WARRIOR
from entities.player import Player
import arcade
from PIL import Image, ImageDraw


class Fighter(Player):
    """Воин — мастер ближнего боя с высокими HP и AC."""

    def __init__(self, name="Воин"):
        stats = {
            'strength': 16,
            'dexterity': 12,
            'constitution': 16,
            'intelligence': 8,
            'wisdom': 10,
            'charisma': 10
        }
        super().__init__(name, stats)
        self.class_name = "Воин"
        self.class_description = "Мастер клинка и щита. Вынослив и смертоносен в ближнем бою."
        self.color = COLOR_WARRIOR

        self.attack_range = 60  # Радиус атаки в пикселях
        self.attack_damage = 8  # Базовый урон (1d8)
        self.attack_cooldown = 0.5  # Секунд между атаками
        self.attack_timer = 0.0  # Текущий таймер
        self.is_attacking = False  # Флаг для отображения атаки
        self.attack_visual_duration = 0.1  # Длительность визуала атаки

        self.texture = self._create_texture()

    def _create_texture(self):
        """Создаёт текстуру для класса (красный квадрат)."""
        img = Image.new('RGBA', (40, 40), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.rectangle([(0, 0), (39, 39)], fill=self.color, outline=(255, 255, 255), width=2)
        return arcade.Texture(img)

    def update(self, delta_time: float = 1 / 60):
        """Обновление состояния Воина."""
        super().update(delta_time)

        # Дополнительная логика для Воина (если понадобится)
        pass

    def attack(self):
        """Выполнить атаку."""
        if self.attack_timer > 0:
            return False

        self.attack_timer = self.attack_cooldown
        self.is_attacking = True
        return True

    def can_attack(self):
        """Проверяет, можно ли атаковать."""
        return self.attack_timer <= 0

    def get_attack_damage(self):
        """Рассчитывает урон атаки (1d8 + модификатор силы)."""
        import random
        base_damage = random.randint(1, self.attack_damage)
        total_damage = base_damage + self.get_modifier('strength')
        return max(1, total_damage)  # Минимум 1 урон

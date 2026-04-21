from entities.entity import Entity


class Fighter(Entity):

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
        self.class_description = "Мастер клинка и щита. Вынослив и смертоносен в ближнем бою."
        self.class_name = "Воин"
        self.color = (200, 50, 50)


class Ranger(Entity):

    def __init__(self, name="Следопыт"):
        stats = {
            'strength': 12,
            'dexterity': 16,
            'constitution': 14,
            'intelligence': 10,
            'wisdom': 14,
            'charisma': 8
        }
        super().__init__(name, stats)
        self.class_description = "Меткий стрелок и следопыт. Предпочитает дальний бой и скрытность."
        self.class_name = "Следопыт"
        self.color = (50, 200, 50)


class Wizard(Entity):

    def __init__(self, name="Волшебник"):
        stats = {
            'strength': 8,
            'dexterity': 10,
            'constitution': 10,
            'intelligence': 16,
            'wisdom': 12,
            'charisma': 10
        }
        super().__init__(name, stats)
        self.class_description = "Повелитель тайных знаний и магии. Хрупок, но способен уничтожать врагов заклинаниями."
        self.class_name = "Волшебник"
        self.color = (50, 100, 255)

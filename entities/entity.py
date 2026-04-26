class Entity:
    """Base entity with stats and health."""

    def __init__(self, name="Unknown", stats=None):
        self.name = name

        if stats is None:
            self.stats = {
                "strength": 10,
                "dexterity": 10,
                "constitution": 10,
                "intelligence": 10,
                "wisdom": 10,
                "charisma": 10,
            }
        else:
            default_keys = [
                "strength",
                "dexterity",
                "constitution",
                "intelligence",
                "wisdom",
                "charisma",
            ]
            self.stats = {}
            for key in default_keys:
                self.stats[key] = stats.get(key, 10)

        self._calculate_derived_stats()
        self.current_hp = self.max_hp

    def _calculate_derived_stats(self):
        self.modifiers = {
            "str_mod": (self.stats["strength"] - 10) // 2,
            "dex_mod": (self.stats["dexterity"] - 10) // 2,
            "con_mod": (self.stats["constitution"] - 10) // 2,
            "int_mod": (self.stats["intelligence"] - 10) // 2,
            "wis_mod": (self.stats["wisdom"] - 10) // 2,
            "cha_mod": (self.stats["charisma"] - 10) // 2,
        }
        self.base_ac = 10 + self.modifiers["dex_mod"]

        self.base_hp = 10
        self.max_hp = self.base_hp + self.modifiers["con_mod"]
        if self.max_hp < 1:
            self.max_hp = 1

    def update_stat(self, stat_name, value):
        if stat_name in self.stats:
            self.stats[stat_name] = value
            self._calculate_derived_stats()
            self.current_hp = min(self.current_hp, self.max_hp)

    def get_modifier(self, stat_name):
        mod_map = {
            "strength": "str_mod",
            "dexterity": "dex_mod",
            "constitution": "con_mod",
            "intelligence": "int_mod",
            "wisdom": "wis_mod",
            "charisma": "cha_mod",
        }
        mod_key = mod_map.get(stat_name)
        if mod_key:
            return self.modifiers[mod_key]
        return 0

    def take_damage(self, damage):
        self.current_hp -= damage
        return self.current_hp <= 0

    def heal(self, amount):
        self.current_hp = min(self.current_hp + amount, self.max_hp)

    def is_alive(self):
        return self.current_hp > 0

    def __repr__(self):
        return f"Entity(name='{self.name}', hp={self.current_hp}/{self.max_hp}, stats={self.stats})"

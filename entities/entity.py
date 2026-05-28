import arcade

from core import dices

DEFAULT_STATS = {
    "strength": 10,
    "dexterity": 10,
    "constitution": 10,
    "intelligence": 10,
    "wisdom": 10,
    "charisma": 10,
}


class Entity:
    def __init__(self, name="Unknown", stats=None):
        self.name = name
        self.combat_feedback_text = ""
        self.combat_feedback_color = arcade.color.WHITE
        self.combat_feedback_timer = 0.0
        self.combat_feedback_duration = 0.0
        self.combat_feedback_offset = 0.0
        self.stats = DEFAULT_STATS.copy()
        if stats is not None:
            self.stats.update(stats)

        self._calculate_derived_stats()
        self.current_hp = self.max_hp

    def _calculate_derived_stats(self):
        self.base_ac = 10 + self.get_modifier("dexterity")
        self.max_hp = max(1, 10 + self.get_modifier("constitution"))

    def get_modifier(self, stat_name):
        return (self.stats.get(stat_name, 10) - 10) // 2

    def take_damage(self, damage):
        self.current_hp -= damage
        return self.current_hp <= 0

    def get_armor_class(self):
        return self.base_ac

    def is_hit_by(self, attack_bonus, disadvantage=False):
        if disadvantage:
            attack_roll = min(
                dices.roll_d20(attack_bonus),
                dices.roll_d20(attack_bonus),
            )
        else:
            attack_roll = dices.roll_d20(attack_bonus)
        return attack_roll > self.get_armor_class(), attack_roll

    def resolve_attack(self, attack_bonus, damage, attacker=None, disadvantage=False):
        hit, attack_roll = self.is_hit_by(attack_bonus, disadvantage)
        if hit:
            self.take_damage(damage)
            self.show_combat_feedback(f"-{damage}", (255, 120, 120))
            return True
        self.show_combat_feedback(
            f"{attack_roll}/{self.get_armor_class()}",
            (210, 210, 230),
        )
        return False

    def heal(self, amount):
        self.current_hp = min(self.current_hp + amount, self.max_hp)

    def is_alive(self):
        return self.current_hp > 0

    def show_combat_feedback(self, text, color):
        self.combat_feedback_text = text
        self.combat_feedback_color = color
        self.combat_feedback_timer = 0.7
        self.combat_feedback_duration = 0.7
        self.combat_feedback_offset = 0.0

    def update_combat_feedback(self, delta_time):
        if self.combat_feedback_timer <= 0:
            return

        self.combat_feedback_timer = max(0.0, self.combat_feedback_timer - delta_time)
        self.combat_feedback_offset += 30 * delta_time

    def draw_combat_feedback(self):
        if self.combat_feedback_timer <= 0:
            return

        alpha = int(255 * (self.combat_feedback_timer / self.combat_feedback_duration))
        base_color = self.combat_feedback_color[:3]
        text_color = (*base_color, alpha)
        shadow_color = (0, 0, 0, alpha)
        y_offset = max(self.height / 2, 20) + 18 + self.combat_feedback_offset
        text_x = self.center_x
        text_y = self.center_y + y_offset

        arcade.draw_text(
            self.combat_feedback_text,
            text_x + 1,
            text_y - 1,
            shadow_color,
            14,
            anchor_x="center",
            bold=True,
        )
        arcade.draw_text(
            self.combat_feedback_text,
            text_x,
            text_y,
            text_color,
            14,
            anchor_x="center",
            bold=True,
        )

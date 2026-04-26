import arcade

from constants import SCREEN_HEIGHT, SCREEN_WIDTH
from entities.classes import Fighter, Ranger, Wizard


class ClassSelectView(arcade.View):
    def __init__(self):
        super().__init__()

        self.classes = [
            Fighter(),
            Ranger(),
            Wizard(),
        ]

        self.selected_index = -1
        self.column_width = SCREEN_WIDTH // 3
        self.column_centers = [
            self.column_width // 2,
            self.column_width + self.column_width // 2,
            2 * self.column_width + self.column_width // 2,
        ]

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

        arcade.draw_text(
            "Выбери свой путь",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 80,
            arcade.color.GOLD,
            48,
            anchor_x="center",
            bold=True,
        )

        arcade.draw_text(
            "ESC - назад",
            SCREEN_WIDTH // 2,
            30,
            arcade.color.LIGHT_GRAY,
            18,
            anchor_x="center",
        )

        for index, char_class in enumerate(self.classes):
            self.draw_class_card(index, char_class, index == self.selected_index)

    def draw_class_card(self, index, char_class, is_selected):
        center_x = self.column_centers[index]

        if is_selected:
            arcade.draw_lbwh_rectangle_filled(
                center_x - (self.column_width - 20) // 2,
                SCREEN_HEIGHT // 2 - 225,
                self.column_width - 20,
                450,
                (60, 60, 80, 200),
            )
            border_color = arcade.color.GOLD
        else:
            border_color = arcade.color.GRAY

        arcade.draw_lbwh_rectangle_outline(
            center_x - (self.column_width - 20) // 2,
            SCREEN_HEIGHT // 2 - 225,
            self.column_width - 20,
            450,
            border_color,
            3,
        )

        arcade.draw_text(
            char_class.class_name.upper(),
            center_x,
            SCREEN_HEIGHT - 180,
            arcade.color.WHITE,
            28,
            anchor_x="center",
            bold=True,
        )

        char_class.draw_preview(center_x, SCREEN_HEIGHT - 280)

        desc_lines = self.wrap_text(char_class.class_description, 25)
        desc_y = SCREEN_HEIGHT - 380
        for line in desc_lines:
            arcade.draw_text(
                line,
                center_x,
                desc_y,
                arcade.color.LIGHT_GRAY,
                14,
                anchor_x="center",
            )
            desc_y -= 20

        stats_y = SCREEN_HEIGHT - 480
        stats = [
            f"СИЛ: {char_class.stats['strength']:2d}  ({char_class.get_modifier('strength'):+d})",
            f"ЛОВ: {char_class.stats['dexterity']:2d}  ({char_class.get_modifier('dexterity'):+d})",
            f"ТЕЛ: {char_class.stats['constitution']:2d}  ({char_class.get_modifier('constitution'):+d})",
            f"ИНТ: {char_class.stats['intelligence']:2d}  ({char_class.get_modifier('intelligence'):+d})",
            f"МУД: {char_class.stats['wisdom']:2d}  ({char_class.get_modifier('wisdom'):+d})",
            f"ХАР: {char_class.stats['charisma']:2d}  ({char_class.get_modifier('charisma'):+d})",
        ]

        arcade.draw_text(
            "ХАРАКТЕРИСТИКИ",
            center_x,
            stats_y,
            arcade.color.WHITE,
            14,
            anchor_x="center",
            bold=True,
        )
        stats_y -= 25

        for stat in stats:
            arcade.draw_text(
                stat,
                center_x - 50,
                stats_y,
                arcade.color.LIGHT_GRAY,
                12,
                anchor_x="left",
            )
            stats_y -= 18

        info_y = stats_y - 10
        arcade.draw_text(
            f"HP: {char_class.max_hp}  |  AC: {char_class.base_ac}",
            center_x,
            info_y,
            arcade.color.LIME,
            14,
            anchor_x="center",
            bold=True,
        )

    def wrap_text(self, text, max_chars):
        words = text.split()
        lines = []
        current_line = []
        current_len = 0

        for word in words:
            if current_len + len(word) + 1 <= max_chars:
                current_line.append(word)
                current_len += len(word) + 1
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
                current_len = len(word)

        if current_line:
            lines.append(" ".join(current_line))

        return lines

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            from views.menu_view import MenuView

            self.window.show_view(MenuView())

    def on_mouse_motion(self, x, y, dx, dy):
        column = int(x) // self.column_width
        if 0 <= column < len(self.classes):
            self.selected_index = column

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            column = int(x) // self.column_width
            if 0 <= column < len(self.classes):
                self.selected_index = column
                self.select_class()

    def select_class(self):
        if self.selected_index == -1:
            return

        player = self.classes[self.selected_index]

        from views.game_view import GameView

        self.window.show_view(GameView(player))

import arcade

from constants import SCREEN_HEIGHT, SCREEN_WIDTH


class PauseView(arcade.View):
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view
        self.selected_index = 0
        self.menu_items = [
            "Продолжить",
            "Выйти в меню",
        ]

    def on_draw(self):
        self.game_view.draw_game_frame(show_pause_hint=False)

        arcade.draw_lbwh_rectangle_filled(
            0,
            0,
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            (0, 0, 0, 185),
        )

        panel_width = 420
        panel_height = 280
        panel_left = (SCREEN_WIDTH - panel_width) / 2
        panel_bottom = (SCREEN_HEIGHT - panel_height) / 2

        arcade.draw_lbwh_rectangle_filled(
            panel_left,
            panel_bottom,
            panel_width,
            panel_height,
            (22, 26, 38, 245),
        )
        arcade.draw_lbwh_rectangle_outline(
            panel_left,
            panel_bottom,
            panel_width,
            panel_height,
            arcade.color.GOLD,
            3,
        )

        arcade.draw_text(
            "ПАУЗА",
            SCREEN_WIDTH / 2,
            panel_bottom + panel_height - 62,
            arcade.color.GOLD,
            38,
            anchor_x="center",
            bold=True,
        )
        arcade.draw_text(
            "Прохождение остановлено и ждёт продолжения",
            SCREEN_WIDTH / 2,
            panel_bottom + panel_height - 98,
            arcade.color.LIGHT_GRAY,
            16,
            anchor_x="center",
        )

        for index, item in enumerate(self.menu_items):
            item_y = panel_bottom + 128 - (index * 62)
            color = arcade.color.YELLOW if index == self.selected_index else arcade.color.LIGHT_GRAY

            if index == self.selected_index:
                arcade.draw_lbwh_rectangle_filled(
                    (SCREEN_WIDTH / 2) - 170,
                    item_y - 12,
                    340,
                    42,
                    (70, 62, 24, 180),
                )

            arcade.draw_text(
                item,
                SCREEN_WIDTH / 2,
                item_y,
                color,
                28,
                anchor_x="center",
            )

        arcade.draw_text(
            "ESC - продолжить",
            SCREEN_WIDTH / 2,
            panel_bottom + 26,
            arcade.color.LIGHT_GRAY,
            16,
            anchor_x="center",
        )

    def _get_menu_item_bounds(self, index):
        panel_height = 280
        panel_bottom = (SCREEN_HEIGHT - panel_height) / 2
        item_y = panel_bottom + 128 - (index * 62)
        return SCREEN_WIDTH / 2, item_y + 8, 170, 21

    def _return_to_game(self):
        self.window.show_view(self.game_view)

    def _return_to_menu(self):
        from views.menu_view import MenuView

        self.window.show_view(MenuView())

    def _select_option(self):
        if self.selected_index == 0:
            self._return_to_game()
        elif self.selected_index == 1:
            self._return_to_menu()

    def on_mouse_motion(self, x, y, dx, dy):
        self.selected_index = -1
        for index, _item in enumerate(self.menu_items):
            item_x, item_y, half_width, half_height = self._get_menu_item_bounds(index)
            if abs(x - item_x) < half_width and abs(y - item_y) < half_height:
                self.selected_index = index
                break

    def on_mouse_press(self, x, y, button, modifiers):
        if button != arcade.MOUSE_BUTTON_LEFT:
            return

        for index, _item in enumerate(self.menu_items):
            item_x, item_y, half_width, half_height = self._get_menu_item_bounds(index)
            if abs(x - item_x) < half_width and abs(y - item_y) < half_height:
                self.selected_index = index
                self._select_option()
                break

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self._return_to_game()
        elif key == arcade.key.UP or key == arcade.key.W:
            self.selected_index = (self.selected_index - 1) % len(self.menu_items)
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.selected_index = (self.selected_index + 1) % len(self.menu_items)
        elif key == arcade.key.ENTER or key == arcade.key.SPACE:
            self._select_option()

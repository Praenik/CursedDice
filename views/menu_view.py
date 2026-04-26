import arcade

from constants import SCREEN_HEIGHT, SCREEN_WIDTH


class MenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.selected_index = -1
        self.menu_items = ["Начать игру", "Выход"]

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

        arcade.draw_text(
            "CURSED DICE",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 150,
            arcade.color.GOLD,
            64,
            anchor_x="center",
            font_name="Arial",
            bold=True,
        )

        for index, item in enumerate(self.menu_items):
            y = SCREEN_HEIGHT // 2 - index * 60

            if index == self.selected_index:
                color = arcade.color.YELLOW
                arcade.draw_text(
                    ">",
                    SCREEN_WIDTH // 2 - 150,
                    y,
                    color,
                    36,
                    anchor_x="center",
                )
            else:
                color = arcade.color.LIGHT_GRAY

            arcade.draw_text(
                item,
                SCREEN_WIDTH // 2,
                y,
                color,
                36,
                anchor_x="center",
            )

    def on_mouse_motion(self, x, y, dx, dy):
        for index, _item in enumerate(self.menu_items):
            item_y = SCREEN_HEIGHT // 2 - index * 60
            if abs(y - item_y) < 30:
                self.selected_index = index
                break

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            for index, _item in enumerate(self.menu_items):
                item_y = SCREEN_HEIGHT // 2 - index * 60
                item_x = SCREEN_WIDTH // 2
                if abs(x - item_x) < 150 and abs(y - item_y) < 30:
                    self.selected_index = index
                    self.select_option()

    def select_option(self):
        if self.selected_index == 0:
            from views.class_select_view import ClassSelectView

            self.window.show_view(ClassSelectView())
        elif self.selected_index == 1:
            arcade.close_window()

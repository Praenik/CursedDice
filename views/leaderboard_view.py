import arcade

from constants import SCREEN_HEIGHT, SCREEN_WIDTH
from core.leaderboard import format_time, load_leaderboard_entries
from entities.player import load_player_textures

TABLE_WIDTH = 940
ROW_HEIGHT = 58
MAX_ROWS = 10
PREVIEW_SIZE = 40


class LeaderboardView(arcade.View):
    def __init__(self):
        super().__init__()
        self.entries = []
        self.refresh_entries()

    def refresh_entries(self):
        self.entries = load_leaderboard_entries()[:MAX_ROWS]

    def on_show_view(self):
        self.refresh_entries()

    def on_draw(self):
        self.clear()
        arcade.set_background_color((18, 20, 28))

        arcade.draw_text(
            "ТАБЛИЦА РЕКОРДОВ",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 90,
            arcade.color.GOLD,
            42,
            anchor_x="center",
            bold=True,
        )
        arcade.draw_text(
            "Сначала выше волна, а при равенстве лучше меньшее время.",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 128,
            arcade.color.LIGHT_GRAY,
            16,
            anchor_x="center",
        )

        self._draw_table()

        arcade.draw_text(
            "ESC - назад в меню",
            SCREEN_WIDTH // 2,
            32,
            arcade.color.LIGHT_GRAY,
            18,
            anchor_x="center",
        )

    def _draw_table(self):
        table_left = (SCREEN_WIDTH - TABLE_WIDTH) / 2
        header_center_y = SCREEN_HEIGHT - 180

        arcade.draw_rect_filled(
            arcade.XYWH(SCREEN_WIDTH / 2, header_center_y, TABLE_WIDTH, 46),
            (44, 48, 62),
        )

        rank_x = table_left + 42
        class_texture_x = table_left + 122
        class_text_x = table_left + 162
        wave_x = table_left + 700
        time_x = table_left + 835

        arcade.draw_text("№", rank_x, header_center_y - 8, arcade.color.WHITE, 18, anchor_x="center", bold=True)
        arcade.draw_text("Класс", class_text_x, header_center_y - 8, arcade.color.WHITE, 18, bold=True)
        arcade.draw_text("Волна", wave_x, header_center_y - 8, arcade.color.WHITE, 18, anchor_x="center", bold=True)
        arcade.draw_text("Время", time_x, header_center_y - 8, arcade.color.WHITE, 18, anchor_x="center", bold=True)

        if not self.entries:
            arcade.draw_text(
                "Пока нет результатов. Сыграйте первый забег.",
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2,
                arcade.color.WHITE,
                24,
                anchor_x="center",
            )
            return

        start_y = header_center_y - 60
        for index, entry in enumerate(self.entries):
            center_y = start_y - (index * ROW_HEIGHT)
            row_color = (33, 36, 48) if index % 2 == 0 else (27, 30, 40)

            arcade.draw_rect_filled(
                arcade.XYWH(SCREEN_WIDTH / 2, center_y, TABLE_WIDTH, ROW_HEIGHT - 6),
                row_color,
            )

            arcade.draw_text(
                str(index + 1),
                rank_x,
                center_y - 10,
                arcade.color.WHITE,
                20,
                anchor_x="center",
                bold=True,
            )

            texture = self._try_load_texture(entry["texture_name"])
            if texture is not None:
                arcade.draw_texture_rect(
                    texture,
                    arcade.XYWH(class_texture_x, center_y, PREVIEW_SIZE, PREVIEW_SIZE),
                )

            arcade.draw_text(
                entry["class_name"],
                class_text_x,
                center_y - 10,
                arcade.color.WHITE,
                20,
                bold=True,
            )
            arcade.draw_text(
                str(entry["wave_reached"]),
                wave_x,
                center_y - 10,
                arcade.color.WHITE,
                20,
                anchor_x="center",
            )
            arcade.draw_text(
                format_time(entry["time_seconds"]),
                time_x,
                center_y - 10,
                arcade.color.WHITE,
                20,
                anchor_x="center",
            )

    def _try_load_texture(self, texture_name):
        try:
            return load_player_textures(texture_name)[0]
        except FileNotFoundError:
            return None

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self._return_to_menu()

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT and y <= 60:
            self._return_to_menu()

    def _return_to_menu(self):
        from views.menu_view import MenuView

        self.window.show_view(MenuView())

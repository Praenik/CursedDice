import arcade

from constants import SCREEN_HEIGHT, SCREEN_WIDTH

MENU_BACKGROUND_TEXTURE = "assets/textures/backgrounds/menu_background.png"
MENU_LOGO_TEXTURE = "assets/textures/ui/menu_logo.png"
MENU_PANEL_WIDTH = 520
MENU_PANEL_HEIGHT = 286
MENU_ITEM_STEP = 60


class MenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.selected_index = -1
        self.menu_items = [
            "Начать игру",
            "Правила",
            "Таблица рекордов",
            "Выход",
        ]
        self.rules_modal_open = False
        self.close_button_hovered = False
        self.background_texture = arcade.load_texture(MENU_BACKGROUND_TEXTURE)
        self.logo_texture = arcade.load_texture(MENU_LOGO_TEXTURE)
        self.rules_sections = [
            [
                (
                    "Об игре",
                    [
                        "Cursed Dice - аркадный survival в духе настольных RPG.",
                        "Выберите класс, переживите волны врагов и разыграйте сильные стороны героя.",
                    ],
                ),
                (
                    "Цель",
                    [
                        "Дойти до конца всех волн и сделать это как можно быстрее.",
                        "После победы или поражения результат попадёт в таблицу рекордов.",
                    ],
                ),
                (
                    "Управление",
                    [
                        "WASD или стрелки - движение.",
                        "ЛКМ - атака в сторону курсора.",
                        "Q - короткий отдых: восстанавливает примерно половину HP, зарядов 2.",
                        "E - длинный отдых: полностью лечит, заряд 1.",
                        "ESC - пауза во время забега и возврат назад в меню.",
                    ],
                ),
            ],
            [
                (
                    "Противники",
                    [
                        "Гоблин - базовый враг, который давит количеством.",
                        "Ворг - быстрый хищник: укус может оглушить при провале спасброска силы.",
                        "Нильбог - трикстер: очаровывает атакующего, один раз превращает урон в лечение и навешивает помеху на следующую атаку.",
                        "Хобгоблин - дисциплинированный боец: бьёт сильнее, если рядом есть союзник.",
                        "Багбир - крепкий громила ближнего боя, который периодически швыряет валун с дистанции.",
                    ],
                )
            ],
        ]

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.BLACK)
        self._draw_background()
        self._draw_menu_overlay()
        self._draw_logo()

        for index, item in enumerate(self.menu_items):
            y = SCREEN_HEIGHT // 2 - index * MENU_ITEM_STEP

            if index == self.selected_index and not self.rules_modal_open:
                color = arcade.color.YELLOW
                arcade.draw_text(
                    ">",
                    SCREEN_WIDTH // 2 - 180,
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

        if self.rules_modal_open:
            self._draw_rules_modal()

    def _draw_background(self):
        if self.background_texture is None:
            return

        texture_width = self.background_texture.width
        texture_height = self.background_texture.height
        if texture_width <= 0 or texture_height <= 0:
            return

        texture_aspect = texture_width / texture_height
        screen_aspect = SCREEN_WIDTH / SCREEN_HEIGHT

        if texture_aspect >= screen_aspect:
            draw_height = SCREEN_HEIGHT
            draw_width = draw_height * texture_aspect
        else:
            draw_width = SCREEN_WIDTH
            draw_height = draw_width / texture_aspect

        arcade.draw_texture_rect(
            self.background_texture,
            arcade.XYWH(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, draw_width, draw_height),
            pixelated=True,
        )

    def _draw_menu_overlay(self):
        arcade.draw_lbwh_rectangle_filled(
            0,
            0,
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            (8, 6, 8, 118),
        )
        arcade.draw_lbwh_rectangle_filled(
            int((SCREEN_WIDTH - MENU_PANEL_WIDTH) / 2),
            148,
            MENU_PANEL_WIDTH,
            MENU_PANEL_HEIGHT,
            (14, 10, 12, 158),
        )
        arcade.draw_lbwh_rectangle_outline(
            int((SCREEN_WIDTH - MENU_PANEL_WIDTH) / 2),
            148,
            MENU_PANEL_WIDTH,
            MENU_PANEL_HEIGHT,
            (173, 132, 69, 175),
            2,
        )

    def _draw_logo(self):
        if self.logo_texture is None:
            return

        max_width = 860
        max_height = 240
        texture_width = self.logo_texture.width
        texture_height = self.logo_texture.height
        if texture_width <= 0 or texture_height <= 0:
            return

        scale = min(max_width / texture_width, max_height / texture_height)
        draw_width = texture_width * scale
        draw_height = texture_height * scale
        arcade.draw_texture_rect(
            self.logo_texture,
            arcade.XYWH(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 158, draw_width, draw_height),
        )

    def _draw_rules_modal(self):
        modal_left, modal_bottom, modal_width, modal_height = self._get_modal_bounds()
        modal_top = modal_bottom + modal_height
        modal_center_x = modal_left + (modal_width / 2)

        arcade.draw_lbwh_rectangle_filled(
            0,
            0,
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            (0, 0, 0, 170),
        )
        arcade.draw_lbwh_rectangle_filled(
            modal_left,
            modal_bottom,
            modal_width,
            modal_height,
            (23, 27, 38, 245),
        )
        arcade.draw_lbwh_rectangle_outline(
            modal_left,
            modal_bottom,
            modal_width,
            modal_height,
            arcade.color.GOLD,
            3,
        )

        arcade.draw_text(
            "ПРАВИЛА",
            modal_center_x,
            modal_top - 55,
            arcade.color.GOLD,
            34,
            anchor_x="center",
            bold=True,
        )
        arcade.draw_text(
            "Короткая памятка перед забегом",
            modal_center_x,
            modal_top - 88,
            arcade.color.LIGHT_GRAY,
            16,
            anchor_x="center",
        )

        close_left, close_bottom, close_width, close_height = self._get_close_button_bounds()
        close_color = (110, 95, 35) if self.close_button_hovered else (54, 60, 74)
        arcade.draw_lbwh_rectangle_filled(
            close_left,
            close_bottom,
            close_width,
            close_height,
            close_color,
        )
        arcade.draw_lbwh_rectangle_outline(
            close_left,
            close_bottom,
            close_width,
            close_height,
            arcade.color.GOLD,
            2,
        )
        arcade.draw_text(
            "Закрыть",
            close_left + (close_width / 2),
            close_bottom + 12,
            arcade.color.WHITE,
            16,
            anchor_x="center",
            bold=True,
        )

        column_gap = 48
        column_width = (modal_width - 120 - column_gap) / 2
        left_column_x = modal_left + 44
        right_column_x = left_column_x + column_width + column_gap
        section_top = modal_top - 130
        max_chars = max(28, int(column_width / 10))

        self._draw_rules_column(self.rules_sections[0], left_column_x, section_top, max_chars)
        self._draw_rules_column(self.rules_sections[1], right_column_x, section_top, max_chars)

        arcade.draw_text(
            "ESC или клик вне окна - закрыть правила",
            modal_center_x,
            modal_bottom + 20,
            arcade.color.LIGHT_GRAY,
            15,
            anchor_x="center",
        )

    def _draw_rules_column(self, sections, start_x, start_y, max_chars):
        current_y = start_y
        for title, items in sections:
            arcade.draw_text(
                title,
                start_x,
                current_y,
                arcade.color.GOLD,
                21,
                bold=True,
            )
            current_y -= 32

            for item in items:
                for line in self._wrap_bullet_text(item, max_chars):
                    arcade.draw_text(
                        line,
                        start_x,
                        current_y,
                        arcade.color.LIGHT_GRAY,
                        15,
                    )
                    current_y -= 22
                current_y -= 6

            current_y -= 12

    def _wrap_bullet_text(self, text, max_chars):
        wrapped_lines = self._wrap_text(text, max_chars - 2)
        if not wrapped_lines:
            return ["-"]

        lines = [f"- {wrapped_lines[0]}"]
        for line in wrapped_lines[1:]:
            lines.append(f"  {line}")
        return lines

    def _wrap_text(self, text, max_chars):
        words = text.split()
        if not words:
            return []

        lines = []
        current_line = words[0]

        for word in words[1:]:
            if len(current_line) + len(word) + 1 <= max_chars:
                current_line = f"{current_line} {word}"
            else:
                lines.append(current_line)
                current_line = word

        lines.append(current_line)
        return lines

    def _get_modal_bounds(self):
        width = 1080
        height = 560
        left = (SCREEN_WIDTH - width) / 2
        bottom = (SCREEN_HEIGHT - height) / 2
        return left, bottom, width, height

    def _get_close_button_bounds(self):
        modal_left, modal_bottom, modal_width, modal_height = self._get_modal_bounds()
        width = 120
        height = 40
        left = modal_left + modal_width - width - 26
        bottom = modal_bottom + modal_height - height - 22
        return left, bottom, width, height

    def _get_menu_item_bounds(self, index):
        item_y = SCREEN_HEIGHT // 2 - index * MENU_ITEM_STEP
        return SCREEN_WIDTH // 2, item_y, 180, 30

    def _is_point_inside_box(self, x, y, bounds):
        left, bottom, width, height = bounds
        return left <= x <= left + width and bottom <= y <= bottom + height

    def on_mouse_motion(self, x, y, dx, dy):
        if self.rules_modal_open:
            self.selected_index = -1
            self.close_button_hovered = self._is_point_inside_box(x, y, self._get_close_button_bounds())
            return

        self.close_button_hovered = False
        self.selected_index = -1
        for index, _item in enumerate(self.menu_items):
            item_x, item_y, half_width, half_height = self._get_menu_item_bounds(index)
            if abs(x - item_x) < half_width and abs(y - item_y) < half_height:
                self.selected_index = index
                break

    def on_mouse_press(self, x, y, button, modifiers):
        if button != arcade.MOUSE_BUTTON_LEFT:
            return

        if self.rules_modal_open:
            if self._is_point_inside_box(x, y, self._get_close_button_bounds()):
                self._close_rules_modal()
            elif not self._is_point_inside_box(x, y, self._get_modal_bounds()):
                self._close_rules_modal()
            return

        for index, _item in enumerate(self.menu_items):
            item_x, item_y, half_width, half_height = self._get_menu_item_bounds(index)
            if abs(x - item_x) < half_width and abs(y - item_y) < half_height:
                self.selected_index = index
                self.select_option()
                break

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE and self.rules_modal_open:
            self._close_rules_modal()

    def _close_rules_modal(self):
        self.rules_modal_open = False
        self.close_button_hovered = False
        self.selected_index = -1

    def select_option(self):
        if self.selected_index == 0:
            from views.class_select_view import ClassSelectView

            self.window.show_view(ClassSelectView())
        elif self.selected_index == 1:
            self.rules_modal_open = True
            self.close_button_hovered = False
        elif self.selected_index == 2:
            from views.leaderboard_view import LeaderboardView

            self.window.show_view(LeaderboardView())
        elif self.selected_index == 3:
            arcade.close_window()

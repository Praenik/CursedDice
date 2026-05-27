import arcade

from constants import SCREEN_HEIGHT, SCREEN_WIDTH
from core.resources import resource_path
from entities.classes import Fighter, Ranger, Wizard

CLASS_SELECT_BACKGROUND_TEXTURE = resource_path("assets", "textures", "backgrounds", "menu_background.png")
CLASS_SELECT_TITLE_TEXTURE = resource_path("assets", "textures", "ui", "class_select_title.png")
PLAYER_PREVIEW_TEXTURE_DIR = resource_path("assets", "textures", "player")
PLAYER_PREVIEW_SIZE = 160


class ClassSelectView(arcade.View):
    def __init__(self):
        super().__init__()

        self.classes = [Fighter, Ranger, Wizard]
        self.preview_textures = {
            player_class.PREVIEW_TEXTURE_NAME: arcade.load_texture(
                PLAYER_PREVIEW_TEXTURE_DIR / player_class.PREVIEW_TEXTURE_NAME
            )
            for player_class in self.classes
        }
        self.selected_index = -1
        self.column_width = SCREEN_WIDTH // 3
        self.column_centers = [
            self.column_width // 2,
            self.column_width + self.column_width // 2,
            2 * self.column_width + self.column_width // 2,
        ]
        self.background_texture = arcade.load_texture(CLASS_SELECT_BACKGROUND_TEXTURE)
        self.title_texture = arcade.load_texture(CLASS_SELECT_TITLE_TEXTURE)

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.BLACK)
        self._draw_background()
        self._draw_screen_overlay()
        self._draw_title_banner()

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

    def _draw_screen_overlay(self):
        arcade.draw_lbwh_rectangle_filled(
            0,
            0,
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            (8, 7, 10, 138),
        )

    def _draw_title_banner(self):
        if self.title_texture is None:
            return

        texture_width = self.title_texture.width
        texture_height = self.title_texture.height
        if texture_width <= 0 or texture_height <= 0:
            return

        scale = min(980 / texture_width, 190 / texture_height)
        draw_width = texture_width * scale
        draw_height = texture_height * scale
        arcade.draw_texture_rect(
            self.title_texture,
            arcade.XYWH(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 108, draw_width, draw_height),
            pixelated=True,
        )

    def draw_class_card(self, index, char_class, is_selected):
        center_x = self.column_centers[index]
        card_left = center_x - (self.column_width - 20) // 2
        card_bottom = SCREEN_HEIGHT // 2 - 225
        card_width = self.column_width - 20
        card_height = 450

        if is_selected:
            arcade.draw_lbwh_rectangle_filled(
                card_left,
                card_bottom,
                card_width,
                card_height,
                (58, 36, 22, 210),
            )
            border_color = arcade.color.GOLD
        else:
            arcade.draw_lbwh_rectangle_filled(
                card_left,
                card_bottom,
                card_width,
                card_height,
                (18, 14, 18, 168),
            )
            border_color = (133, 116, 92)

        arcade.draw_lbwh_rectangle_outline(
            card_left,
            card_bottom,
            card_width,
            card_height,
            border_color,
            3,
        )

        arcade.draw_text(
            char_class.CLASS_NAME.upper(),
            center_x,
            SCREEN_HEIGHT - 180,
            arcade.color.WHITE,
            28,
            anchor_x="center",
            bold=True,
        )

        self._draw_class_preview(char_class, center_x, SCREEN_HEIGHT - 280)

        desc_lines = self.wrap_text(char_class.CLASS_DESCRIPTION, 25)
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
        class_stats = char_class.DEFAULT_STATS
        stats = [
            f"СИЛ: {class_stats['strength']:2d}  ({self.get_modifier(char_class, 'strength'):+d})",
            f"ЛОВ: {class_stats['dexterity']:2d}  ({self.get_modifier(char_class, 'dexterity'):+d})",
            f"ТЕЛ: {class_stats['constitution']:2d}  ({self.get_modifier(char_class, 'constitution'):+d})",
            f"ИНТ: {class_stats['intelligence']:2d}  ({self.get_modifier(char_class, 'intelligence'):+d})",
            f"МУД: {class_stats['wisdom']:2d}  ({self.get_modifier(char_class, 'wisdom'):+d})",
            f"ХАР: {class_stats['charisma']:2d}  ({self.get_modifier(char_class, 'charisma'):+d})",
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
        max_hp = max(1, 10 + self.get_modifier(char_class, "constitution"))
        base_ac = 10 + self.get_modifier(char_class, "dexterity")
        arcade.draw_text(
            f"HP: {max_hp}  |  AC: {base_ac}",
            center_x,
            info_y,
            arcade.color.LIME,
            14,
            anchor_x="center",
            bold=True,
        )

    def _draw_class_preview(self, char_class, center_x, center_y):
        preview_texture = self.preview_textures.get(char_class.PREVIEW_TEXTURE_NAME)
        if preview_texture is None:
            return

        arcade.draw_texture_rect(
            preview_texture,
            arcade.XYWH(center_x, center_y, PLAYER_PREVIEW_SIZE, PLAYER_PREVIEW_SIZE),
            pixelated=True,
        )

    def wrap_text(self, text, max_chars):
        words = text.split()
        lines = []
        current_line = []
        current_len = 0

        for word in words:
            extra_space = 1 if current_line else 0
            if current_len + len(word) + extra_space <= max_chars:
                current_line.append(word)
                current_len += len(word) + extra_space
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
                current_len = len(word)

        if current_line:
            lines.append(" ".join(current_line))

        return lines

    def get_modifier(self, player_class, stat_name):
        return (player_class.DEFAULT_STATS[stat_name] - 10) // 2

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

        player = self.classes[self.selected_index]()

        from views.game_view import GameView

        self.window.show_view(GameView(player))

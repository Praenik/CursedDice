from dataclasses import dataclass

import arcade

from constants import SCREEN_HEIGHT, SCREEN_WIDTH
from core.resources import resource_path
from entities.classes import Fighter, Ranger, Wizard

CLASS_SELECT_BACKGROUND_TEXTURE = resource_path("assets", "textures", "backgrounds", "menu_background.png")
CLASS_SELECT_TITLE_TEXTURE = resource_path("assets", "textures", "ui", "class_select_title.png")
PLAYER_PREVIEW_TEXTURE_DIR = resource_path("assets", "textures", "player")
PLAYER_PREVIEW_MAX_SIZE = 160


@dataclass(frozen=True)
class ClassOption:
    factory: type
    class_name: str
    class_description: str
    stats: dict
    preview_texture_name: str

    def get_modifier(self, stat_name):
        return (self.stats[stat_name] - 10) // 2

    @property
    def max_hp(self):
        return max(1, 10 + self.get_modifier("constitution"))

    @property
    def base_ac(self):
        return 10 + self.get_modifier("dexterity")


class ClassSelectView(arcade.View):
    def __init__(self):
        super().__init__()

        self.classes = [
            self._create_class_option(Fighter),
            self._create_class_option(Ranger),
            self._create_class_option(Wizard),
        ]
        self.preview_textures = {
            char_class.preview_texture_name: arcade.load_texture(PLAYER_PREVIEW_TEXTURE_DIR / char_class.preview_texture_name)
            for char_class in self.classes
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

    def _create_class_option(self, player_class):
        return ClassOption(
            factory=player_class,
            class_name=player_class.CLASS_NAME,
            class_description=player_class.CLASS_DESCRIPTION,
            stats=dict(player_class.DEFAULT_STATS),
            preview_texture_name=player_class.PREVIEW_TEXTURE_NAME,
        )

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.BLACK)
        self._draw_background()
        self._draw_screen_overlay()
        self._draw_title_banner()

        arcade.draw_text(
            "ESC - \u043d\u0430\u0437\u0430\u0434",
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
            char_class.class_name.upper(),
            center_x,
            SCREEN_HEIGHT - 180,
            arcade.color.WHITE,
            28,
            anchor_x="center",
            bold=True,
        )

        self._draw_class_preview(char_class, center_x, SCREEN_HEIGHT - 280)

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
            f"\u0421\u0418\u041b: {char_class.stats['strength']:2d}  ({char_class.get_modifier('strength'):+d})",
            f"\u041b\u041e\u0412: {char_class.stats['dexterity']:2d}  ({char_class.get_modifier('dexterity'):+d})",
            f"\u0422\u0415\u041b: {char_class.stats['constitution']:2d}  ({char_class.get_modifier('constitution'):+d})",
            f"\u0418\u041d\u0422: {char_class.stats['intelligence']:2d}  ({char_class.get_modifier('intelligence'):+d})",
            f"\u041c\u0423\u0414: {char_class.stats['wisdom']:2d}  ({char_class.get_modifier('wisdom'):+d})",
            f"\u0425\u0410\u0420: {char_class.stats['charisma']:2d}  ({char_class.get_modifier('charisma'):+d})",
        ]

        arcade.draw_text(
            "\u0425\u0410\u0420\u0410\u041a\u0422\u0415\u0420\u0418\u0421\u0422\u0418\u041a\u0418",
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

    def _draw_class_preview(self, char_class, center_x, center_y):
        preview_texture = self.preview_textures.get(char_class.preview_texture_name)
        if preview_texture is None:
            return

        largest_side = max(preview_texture.width, preview_texture.height)
        if largest_side <= 0:
            return

        scale = PLAYER_PREVIEW_MAX_SIZE / largest_side
        preview_width = preview_texture.width * scale
        preview_height = preview_texture.height * scale
        arcade.draw_texture_rect(
            preview_texture,
            arcade.XYWH(center_x, center_y, preview_width, preview_height),
            pixelated=True,
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

        player = self.classes[self.selected_index].factory()

        from views.game_view import GameView

        self.window.show_view(GameView(player))

import arcade

from constants import SCREEN_HEIGHT, SCREEN_TITLE, SCREEN_WIDTH
from views.menu_view import MenuView


def create_window():
    return arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)


def main():
    window = create_window()
    window.show_view(MenuView())
    arcade.run()


if __name__ == "__main__":
    main()

import random
import arcade
from constants import *
from entities.enemies.goblin import Goblin
from entities.player import Player


class GameView(arcade.View):
    """Основной игровой вид."""

    def __init__(self, player: Player):
        super().__init__()

        self.player = player

        self.player.center_x = SCREEN_WIDTH // 2
        self.player.center_y = SCREEN_HEIGHT // 2

        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player)

        self.enemies_list = arcade.SpriteList()
        self._spawn_enemies()

        self.up = False
        self.down = False
        self.left = False
        self.right = False

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.BLACK)

        self.enemies_list.draw()
        self.player_list.draw()

        if self.player.is_attacking and hasattr(self.player, 'attack_range'):
            arcade.draw_circle_outline(
                self.player.center_x,
                self.player.center_y,
                self.player.attack_range,
                arcade.color.WHITE,
                2
            )

        arcade.draw_text(
            f"{self.player.class_name} | HP: {self.player.current_hp}/{self.player.max_hp}",
            10,
            SCREEN_HEIGHT - 30,
            arcade.color.WHITE,
            16
        )

        arcade.draw_text(
            f"Врагов: {len(self.enemies_list)}",
            10,
            SCREEN_HEIGHT - 60,
            arcade.color.WHITE,
            16
        )

    def on_update(self, delta_time):
        self.player.update(delta_time)

        self.player.change_x = 0
        self.player.change_y = 0

        if self.up:
            self.player.change_y = self.player.speed
        if self.down:
            self.player.change_y = -self.player.speed
        if self.left:
            self.player.change_x = -self.player.speed
        if self.right:
            self.player.change_x = self.player.speed

        self.player_list.update()

        for enemy in self.enemies_list:
            enemy.update(delta_time, self.player)

        self.enemies_list.update()

        if self.player.left < 0:
            self.player.left = 0
        elif self.player.right > SCREEN_WIDTH:
            self.player.right = SCREEN_WIDTH

        if self.player.bottom < 0:
            self.player.bottom = 0
        elif self.player.top > SCREEN_HEIGHT:
            self.player.top = SCREEN_HEIGHT

        for enemy in self.enemies_list:
            if enemy.left < 0:
                enemy.left = 0
            elif enemy.right > SCREEN_WIDTH:
                enemy.right = SCREEN_WIDTH

            if enemy.bottom < 0:
                enemy.bottom = 0
            elif enemy.top > SCREEN_HEIGHT:
                enemy.top = SCREEN_HEIGHT

    def on_key_press(self, key, modifiers):
        if key == arcade.key.W or key == arcade.key.UP:
            self.up = True
        elif key == arcade.key.S or key == arcade.key.DOWN:
            self.down = True
        elif key == arcade.key.A or key == arcade.key.LEFT:
            self.left = True
        elif key == arcade.key.D or key == arcade.key.RIGHT:
            self.right = True
        elif key == arcade.key.SPACE:
            if self.player.can_attack():
                self.player.attack()
                print(f"Атака! Урон: {self.player.get_attack_damage()}")
        elif key == arcade.key.ESCAPE:
            from views.menu_view import MenuView
            self.window.show_view(MenuView())

    def on_key_release(self, key, modifiers):
        if key == arcade.key.W or key == arcade.key.UP:
            self.up = False
        elif key == arcade.key.S or key == arcade.key.DOWN:
            self.down = False
        elif key == arcade.key.A or key == arcade.key.LEFT:
            self.left = False
        elif key == arcade.key.D or key == arcade.key.RIGHT:
            self.right = False

    def _spawn_enemies(self):
        """Создаёт врагов на карте."""
        for _ in range(3):
            goblin = Goblin()
            while True:
                spawn_x = random.randint(50, SCREEN_WIDTH - 50)
                spawn_y = random.randint(50, SCREEN_HEIGHT - 50)

                dx = spawn_x - self.player.center_x
                dy = spawn_y - self.player.center_y
                distance = (dx ** 2 + dy ** 2) ** 0.5

                if distance > 150:
                    break

            goblin.setup(spawn_x, spawn_y)
            self.enemies_list.append(goblin)

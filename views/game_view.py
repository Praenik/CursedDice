import random

import arcade

from constants import SCREEN_HEIGHT, SCREEN_WIDTH
from entities.enemies.goblin import Goblin
from entities.player import Player


class GameView(arcade.View):
    def __init__(self, player: Player):
        super().__init__()

        self.player = player
        self.game_over = False
        self.player.center_x = SCREEN_WIDTH // 2
        self.player.center_y = SCREEN_HEIGHT // 2

        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player)

        self.enemies_list = arcade.SpriteList()
        self.player_projectiles = arcade.SpriteList()
        self._spawn_enemies()
        self.player_physics = arcade.PhysicsEngineSimple(self.player, self.enemies_list)

        self.up = False
        self.down = False
        self.left = False
        self.right = False
        self.mouse_x = self.player.center_x + self.player.attack_range
        self.mouse_y = self.player.center_y
        self.attack_dir_x = None
        self.attack_dir_y = None

    def _spawn_enemies(self):
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

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.BLACK)

        self.enemies_list.draw()
        for enemy in self.enemies_list:
            enemy.draw_health_bar()
            enemy.draw_combat_feedback()

        self.player_projectiles.draw()
        self.player_list.draw()
        self.player.draw_combat_feedback()

        if self.game_over:
            arcade.draw_text(
                "ИГРА ОКОНЧЕНА",
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2,
                arcade.color.RED,
                font_size=50,
                anchor_x="center",
                font_name="Kenney Future",
            )
            arcade.draw_text(
                "Нажмите ESC для выхода в меню",
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2 - 60,
                arcade.color.WHITE,
                font_size=20,
                anchor_x="center",
            )

        if self.player.is_attacking:
            aim_x, aim_y = self._get_attack_aim()
            self.player.draw_attack_indicator(aim_x, aim_y)

        arcade.draw_text(
            f"{self.player.class_name} | HP: {self.player.current_hp}/{self.player.max_hp}",
            10,
            SCREEN_HEIGHT - 30,
            arcade.color.WHITE,
            16,
        )

        arcade.draw_text(
            f"Врагов: {len(self.enemies_list)}",
            10,
            SCREEN_HEIGHT - 60,
            arcade.color.WHITE,
            16,
        )

    def on_update(self, delta_time):
        self.player.change_x = 0
        self.player.change_y = 0

        if not self.game_over:
            if self.up:
                self.player.change_y += self.player.speed
            if self.down:
                self.player.change_y -= self.player.speed
            if self.left:
                self.player.change_x -= self.player.speed
            if self.right:
                self.player.change_x += self.player.speed

        self.player.update(delta_time)
        self.player_physics.update()

        if not self.player.is_attacking:
            self.attack_dir_x = None
            self.attack_dir_y = None

        for enemy in self.enemies_list:
            enemy.update(
                delta_time=delta_time,
                player=self.player,
                enemies_list=self.enemies_list,
            )

        for projectile in list(self.player_projectiles):
            projectile.update(delta_time, self.enemies_list)

        if not self.player.is_alive():
            self.game_over = True

        self._clamp_to_bounds(self.player)
        for enemy in self.enemies_list:
            self._clamp_to_bounds(enemy)

    def _clamp_to_bounds(self, sprite):
        if sprite.left < 0:
            sprite.left = 0
        elif sprite.right > SCREEN_WIDTH:
            sprite.right = SCREEN_WIDTH

        if sprite.bottom < 0:
            sprite.bottom = 0
        elif sprite.top > SCREEN_HEIGHT:
            sprite.top = SCREEN_HEIGHT

    def on_key_press(self, key, modifiers):
        if self.game_over:
            if key == arcade.key.ESCAPE:
                from views.menu_view import MenuView

                self.window.show_view(MenuView())
            return

        if key == arcade.key.W or key == arcade.key.UP:
            self.up = True
        elif key == arcade.key.S or key == arcade.key.DOWN:
            self.down = True
        elif key == arcade.key.A or key == arcade.key.LEFT:
            self.left = True
        elif key == arcade.key.D or key == arcade.key.RIGHT:
            self.right = True
        elif key == arcade.key.SPACE:
            if self.player.attack():
                self._lock_attack_direction()
                aim_x, aim_y = self._get_attack_aim()
                self.player.execute_attack(self, aim_x, aim_y)
        elif key == arcade.key.ESCAPE:
            from views.menu_view import MenuView

            self.window.show_view(MenuView())

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_x = x
        self.mouse_y = y

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.mouse_x = x
        self.mouse_y = y

    def _get_attack_aim(self):
        if self.attack_dir_x is not None and self.attack_dir_y is not None:
            aim_distance = max(self.player.attack_range, 100)
            return (
                self.player.center_x + self.attack_dir_x * aim_distance,
                self.player.center_y + self.attack_dir_y * aim_distance,
            )
        return self.mouse_x, self.mouse_y

    def _lock_attack_direction(self):
        dx = self.mouse_x - self.player.center_x
        dy = self.mouse_y - self.player.center_y
        distance = (dx ** 2 + dy ** 2) ** 0.5

        if distance == 0:
            self.attack_dir_x = 1.0
            self.attack_dir_y = 0.0
            return

        self.attack_dir_x = dx / distance
        self.attack_dir_y = dy / distance

    def on_key_release(self, key, modifiers):
        if key == arcade.key.W or key == arcade.key.UP:
            self.up = False
        elif key == arcade.key.S or key == arcade.key.DOWN:
            self.down = False
        elif key == arcade.key.A or key == arcade.key.LEFT:
            self.left = False
        elif key == arcade.key.D or key == arcade.key.RIGHT:
            self.right = False

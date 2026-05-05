import random

import arcade

from constants import SCREEN_HEIGHT, SCREEN_WIDTH
from entities.enemies import Bugbear, Goblin, Hobgoblin, Nilbog, Worg
from entities.player import Player


class GameView(arcade.View):
    def __init__(self, player: Player):
        super().__init__()

        self.player = player
        self.game_over = False
        self.game_completed = False
        self.elapsed_time = 0.0
        self.completed_time = 0.0
        self.wave_spawn_delay = 5.0
        self.wave_spawn_timer = 0.0
        self.waiting_for_next_wave = False
        self.current_wave_index = -1
        self.waves = [
            [Goblin, Goblin, Goblin],
            [Goblin, Goblin, Worg, Worg],
            [Goblin, Goblin, Worg, Nilbog],
            [Goblin, Goblin, Worg, Worg, Nilbog, Hobgoblin, Hobgoblin],
            [Bugbear],
        ]
        self.player.center_x = SCREEN_WIDTH // 2
        self.player.center_y = SCREEN_HEIGHT // 2

        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player)

        self.enemies_list = arcade.SpriteList()
        self.player_projectiles = arcade.SpriteList()
        self.enemy_projectiles = arcade.SpriteList()
        self._spawn_next_wave()
        self.player_physics = arcade.PhysicsEngineSimple(self.player, self.enemies_list)

        self.up = False
        self.down = False
        self.left = False
        self.right = False
        self.mouse_x = self.player.center_x + self.player.attack_range
        self.mouse_y = self.player.center_y
        self.attack_dir_x = None
        self.attack_dir_y = None

    def _spawn_next_wave(self):
        next_wave_index = self.current_wave_index + 1
        if next_wave_index >= len(self.waves):
            self._complete_game()
            return

        self.current_wave_index = next_wave_index
        self.waiting_for_next_wave = False
        self.wave_spawn_timer = 0.0
        self._spawn_wave(self.waves[self.current_wave_index])

    def _spawn_wave(self, enemy_classes):
        for enemy_class in enemy_classes:
            self._spawn_enemy(enemy_class)

    def _spawn_enemy(self, enemy_class):
        enemy = enemy_class()
        spawn_x, spawn_y = self._get_spawn_position()
        enemy.setup(spawn_x, spawn_y)
        self.enemies_list.append(enemy)

    def _get_spawn_position(self):
        while True:
            spawn_x = random.randint(50, SCREEN_WIDTH - 50)
            spawn_y = random.randint(50, SCREEN_HEIGHT - 50)

            dx = spawn_x - self.player.center_x
            dy = spawn_y - self.player.center_y
            distance = (dx ** 2 + dy ** 2) ** 0.5

            if distance > 150:
                return spawn_x, spawn_y

    def _update_wave_state(self, delta_time):
        if self.waiting_for_next_wave:
            self.wave_spawn_timer = max(0.0, self.wave_spawn_timer - delta_time)
            if self.wave_spawn_timer <= 0:
                self._spawn_next_wave()
            return

        if self._get_alive_enemy_count() > 0:
            return

        if self.current_wave_index >= len(self.waves) - 1:
            self._complete_game()
            return

        self.waiting_for_next_wave = True
        self.wave_spawn_timer = self.wave_spawn_delay

    def _complete_game(self):
        if self.game_completed:
            return

        self.game_completed = True
        self.completed_time = self.elapsed_time
        self.up = False
        self.down = False
        self.left = False
        self.right = False
        self.enemy_projectiles = arcade.SpriteList()

    def _get_alive_enemy_count(self):
        return sum(1 for enemy in self.enemies_list if enemy.is_alive())

    def _format_time(self, seconds):
        minutes = int(seconds // 60)
        remaining_seconds = seconds - (minutes * 60)
        return f"{minutes:02d}:{remaining_seconds:04.1f}"

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.BLACK)

        self.enemies_list.draw()
        for enemy in self.enemies_list:
            enemy.draw_health_bar()
            enemy.draw_combat_feedback()

        self.player_projectiles.draw()
        self.enemy_projectiles.draw()
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
        elif self.game_completed:
            arcade.draw_text(
                "ИГРА ПРОЙДЕНА",
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2,
                arcade.color.GREEN,
                font_size=50,
                anchor_x="center",
                font_name="Kenney Future",
            )
            arcade.draw_text(
                f"Время прохождения: {self._format_time(self.completed_time)}",
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2 - 60,
                arcade.color.WHITE,
                font_size=20,
                anchor_x="center",
            )
            arcade.draw_text(
                "Нажмите ESC для выхода в меню",
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2 - 95,
                arcade.color.WHITE,
                font_size=20,
                anchor_x="center",
            )

        if self.player.is_attacking and not self.game_over and not self.game_completed:
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
            f"Врагов: {self._get_alive_enemy_count()}",
            10,
            SCREEN_HEIGHT - 60,
            arcade.color.WHITE,
            16,
        )

        arcade.draw_text(
            f"Волна: {self.current_wave_index + 1}/{len(self.waves)}",
            10,
            SCREEN_HEIGHT - 90,
            arcade.color.WHITE,
            16,
        )

        arcade.draw_text(
            f"Время: {self._format_time(self.elapsed_time)}",
            10,
            SCREEN_HEIGHT - 120,
            arcade.color.WHITE,
            16,
        )

        if self.waiting_for_next_wave:
            arcade.draw_text(
                f"Следующая волна через: {self.wave_spawn_timer:.1f}",
                10,
                SCREEN_HEIGHT - 150,
                arcade.color.YELLOW,
                16,
            )

        if self.player.is_stunned():
            arcade.draw_text(
                f"Оглушение: {self.player.stun_timer:.1f}",
                10,
                SCREEN_HEIGHT - 180,
                arcade.color.YELLOW,
                16,
            )

        if self.player.is_charmed():
            arcade.draw_text(
                f"Очарование: {self.player.charm_timer:.1f}",
                10,
                SCREEN_HEIGHT - 210,
                arcade.color.YELLOW,
                16,
            )

        if self.player.next_attack_disadvantage:
            arcade.draw_text(
                "Следующая атака: помеха",
                10,
                SCREEN_HEIGHT - 240,
                arcade.color.YELLOW,
                16,
            )

    def on_update(self, delta_time):
        self.player.change_x = 0
        self.player.change_y = 0

        is_playing = not self.game_over and not self.game_completed

        if is_playing:
            self.elapsed_time += delta_time

            if self.up and not self.player.is_stunned() and not self.player.is_charmed():
                self.player.change_y += self.player.speed
            if self.down and not self.player.is_stunned() and not self.player.is_charmed():
                self.player.change_y -= self.player.speed
            if self.left and not self.player.is_stunned() and not self.player.is_charmed():
                self.player.change_x -= self.player.speed
            if self.right and not self.player.is_stunned() and not self.player.is_charmed():
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
            if hasattr(enemy, "update_ranged_attack"):
                enemy.update_ranged_attack(delta_time, self.player, self.enemy_projectiles)

        for projectile in list(self.player_projectiles):
            projectile.update(delta_time, self.enemies_list)

        if is_playing:
            for projectile in list(self.enemy_projectiles):
                projectile.update(delta_time, self.player)

        if not self.player.is_alive():
            self.game_over = True
        elif is_playing:
            self._update_wave_state(delta_time)

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
        if self.game_over or self.game_completed:
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

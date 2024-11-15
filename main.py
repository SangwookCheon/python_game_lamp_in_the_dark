"""
AUTHOR: Sangwook Cheon
GAME: A Lantern in the Dark
Duke CS190FS
December 14, 2022
"""
import math
import random
from pathlib import Path
from pyglet.math import Vec2
import arcade
from arcade.experimental import Shadertoy
import os

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
GAME_NAME = "A Lantern in the Dark"
NUM_LEVELS = 5

SPRITE_SCALING = 0.3
ENEMY_SCALING = 0.3
WORLD_VIBRATE = 2

NUM_LIVES = 3

SOUND = arcade.load_sound('background.wav')

PLAYER_MOVEMENT_SPEED = 5
LIGHT_RADIUS = 250
CHANGE_LIGHT_RADIUS = 6
LIGHT_THRESHOLD = 440

GRAVITY = 1400

DEFAULT_DAMPING = 1.0
PLAYER_DAMPING = 0.4

PLAYER_FRICTION = 1.0
WALL_FRICTION = 0.7
DYNAMIC_ITEM_FRICTION = 0.6

PLAYER_MASS = 2.0
ENEMY_MASS = 0.3
ENEMY_RADIUS = 150

PLAYER_MAX_HORIZONTAL_SPEED = 250
PLAYER_MAX_VERTICAL_SPEED = 1000
ENEMY_MAX_VERTICAL_SPEED = 250

PLAYER_MOVE_FORCE_ON_GROUND = 5000
PLAYER_MOVE_FORCE_IN_AIR = 900
PLAYER_JUMP_IMPULSE = 800

class Level:
    """
    Loads a level given a path to a directory with images and a text file listing enemies
    """
    def __init__(self, dir_path):
        self.dir_path = dir_path
        self.world_list = arcade.SpriteList()
        self.background_list = arcade.SpriteList()
        self.text = arcade.Sprite()
        self.enemy_list = []

        # Load the individual pieces of a level
        for file in os.listdir(self.dir_path):
            name = os.path.join(self.dir_path, file)

            if 'txt' not in name and 'text' not in name:
                self.world_sprite = arcade.Sprite(name, hit_box_algorithm="Detailed")
                self.world_sprite.center_x = SCREEN_WIDTH // 2
                self.world_sprite.center_y = SCREEN_HEIGHT // 2

                # If 'bg' is in the name, add it to the background list.
                if 'bg' not in name:
                    self.world_list.append(self.world_sprite)
                elif 'bg' in name:
                    self.background_list.append(self.world_sprite)

            if 'text' in name:
                self.text = arcade.Sprite(name)
                self.text.center_x = SCREEN_WIDTH // 2
                self.text.center_y = SCREEN_HEIGHT // 2

            # Enemy list.
            elif 'txt' in name:
                with open(name) as file2:
                    for line in file2:
                        items = line.split(',')
                        self.enemy_list.append(items)


class Enemy(arcade.Sprite):
    """
    Represents a single enemy of one of two types.
    """
    def __init__(self, enemy_type, x, y):
        self.enemy_type = enemy_type

        if self.enemy_type == 'fall':
            super().__init__('fall.png', ENEMY_SCALING)
        elif self.enemy_type == 'follow':
            super().__init__('follow.png', ENEMY_SCALING)

        self.center_x = x
        self.center_y = y

    def move(self, player_x_pos, player_y_pos, light_radius, jumping):
        # A method that governs how 'following' enemies move.

        if self.enemy_type == 'follow' and not jumping:
            if arcade.get_distance(player_x_pos, player_y_pos, self.center_x, self.center_y) < ENEMY_RADIUS:

                # speed depends on light_radius
                speed = light_radius * 0.001
                x_dif = player_x_pos - self.center_x + 1
                y_dif = player_y_pos - self.center_y + 1

                angle = math.atan(y_dif / x_dif)
                abs_angle = math.atan(abs(y_dif) / abs(x_dif))

                self.angle = math.degrees(angle)
                self.change_x = x_dif / abs(x_dif) * speed * math.cos(abs_angle)
                self.change_y = y_dif / abs(y_dif) * speed * math.sin(abs_angle)
            else:
                self.change_x = 0
                self.change_y = 0



class GameWindow(arcade.Window):
    """
    Where all the game happens
    """

    def __init__(self, width, height, name):
        super().__init__(width, height, name)

        # Variables for the shading effect
        self.shadertoy = None
        self.channel0 = None
        self.channel1 = None
        self.load_shader()
        self.jumping = False

        self.player_sprite = None
        self.player_list = arcade.SpriteList()
        self.physics_engine = None

        self.light_radius = LIGHT_RADIUS
        self.change_light_radius = 0
        self.world_list = arcade.SpriteList() # use_spatial_hashing=True
        self.background_list = arcade.SpriteList()

        self.enemy_list = []

        self.world_vibrate = WORLD_VIBRATE
        self.level = 0

        # temporary timer used for vibrating world effect
        self.timer = 0

        self.game_timer = 0
        self.lives = NUM_LIVES

        # self.create_world(Level1)
        # self.create_player(100, 250)
        #
        # arcade.set_background_color(arcade.color.YELLOW)

        self.left_pressed = False
        self.right_pressed = False

        self.game_over = False
        self.game_start = False

        arcade.play_sound(SOUND, 1, -1, True)

    def reset(self):

        self.player_sprite = None
        self.player_list = arcade.SpriteList()
        self.physics_engine = None
        self.enemy_list = []

        self.world_list = arcade.SpriteList()
        self.background_list = arcade.SpriteList()

        # Game Variables
        self.light_radius = LIGHT_RADIUS
        self.change_light_radius = 0
        self.game_over = False
        self.game_start = True
        self.level = 0
        self.timer = 0
        self.game_timer = 0
        self.lives = NUM_LIVES

        # Yellow background - lighting effect
        arcade.set_background_color(arcade.color.YELLOW)
        self.create_world(Levels[0])
        self.create_player(100, 450)


    def load_shader(self):

        shader_path = Path("shader.glsl")
        window_size = [SCREEN_WIDTH * 2, SCREEN_HEIGHT * 2]

        self.shadertoy = Shadertoy.create_from_file(window_size, shader_path)

        self.channel0 = self.shadertoy.ctx.framebuffer(
            color_attachments=[self.shadertoy.ctx.texture(window_size, components=4)]
        )
        self.channel1 = self.shadertoy.ctx.framebuffer(
            color_attachments=[self.shadertoy.ctx.texture(window_size, components=4)]
        )

        self.shadertoy.channel_0 = self.channel0.color_attachments[0]
        self.shadertoy.channel_1 = self.channel1.color_attachments[0]

    def create_player(self, x, y):
        """
        Creates player and adds it to the physics engine.
        """
        # Create the player
        self.player_list = arcade.SpriteList()
        self.player_sprite = arcade.Sprite("player.png",
                                           scale=SPRITE_SCALING)
        self.player_sprite.center_x = x
        self.player_sprite.center_y = y
        self.player_list.append(self.player_sprite)

        # Add the player
        self.physics_engine.add_sprite(self.player_sprite,
                                       friction=PLAYER_FRICTION,
                                       mass=PLAYER_MASS,
                                       moment=arcade.PymunkPhysicsEngine.MOMENT_INF,
                                       collision_type="player",
                                       max_horizontal_velocity=PLAYER_MAX_HORIZONTAL_SPEED,
                                       max_vertical_velocity=PLAYER_MAX_VERTICAL_SPEED)

    def create_world(self, level):
        """
        Creates the physics engine and adds the world onto it. The world is loaded from a provided level object.
        """
        self.world_list = arcade.SpriteList()
        self.world_list = level.world_list
        self.background_list = level.background_list
        self.enemy_list = []

        # Physics Engine
        self.physics_engine = arcade.PymunkPhysicsEngine(damping=DEFAULT_DAMPING,
                                                         gravity=(0, -GRAVITY))

        self.physics_engine.add_sprite_list(self.world_list,
                                            friction=WALL_FRICTION,
                                            collision_type="wall",
                                            body_type=arcade.PymunkPhysicsEngine.STATIC)

        # Create all enemies
        for item in level.enemy_list:
            self.create_enemy(item[0], int(item[1]), int(item[2]))

    def create_enemy(self, type, x, y):
        """
        Creates an enemy object based on its type and x,y position.
        """
        if type == 'follow':
            enemy = Enemy('follow', x, y)
            self.enemy_list.append(enemy)

        if type == 'fall':
            enemy = Enemy('fall', x, y)
            self.enemy_list.append(enemy)

            self.physics_engine.add_sprite(enemy,
                                           friction=PLAYER_FRICTION,
                                           mass=ENEMY_MASS,
                                           moment=arcade.PymunkPhysicsEngine.MOMENT_INF,
                                           collision_type="player",
                                           max_horizontal_velocity=PLAYER_MAX_HORIZONTAL_SPEED,
                                           max_vertical_velocity=ENEMY_MAX_VERTICAL_SPEED)


    def on_update(self, dt):
        """ Movement and game logic
        Updates:
        - Timers
        - Light Radius
        - Movement of the player with physics engine
        - Enemies' movement/creation
        - World vibrate effect
        - Switch between levels
        - Check game_over conditions (collision with enemy, falling into a hole)
        """

        if self.game_start and not self.game_over:

            # Update the game timer - used to display score.
            if self.level > 0:
                self.game_timer += dt

            self.timer += dt

            # Update light radius
            if self.light_radius + self.change_light_radius > 0:
                self.light_radius += self.change_light_radius

            is_on_ground = self.physics_engine.is_on_ground(self.player_sprite)
            # Update player forces based on keys pressed
            if self.left_pressed and not self.right_pressed:
                # Create a force to the left. Apply it.
                if is_on_ground:
                    force = (-PLAYER_MOVE_FORCE_ON_GROUND, 0)
                else:
                    force = (-PLAYER_MOVE_FORCE_IN_AIR, 0)
                self.physics_engine.apply_force(self.player_sprite, force)

                # friction is 0.5 while the player is moving.
                self.physics_engine.set_friction(self.player_sprite, 0.5)

            elif self.right_pressed and not self.left_pressed:
                if is_on_ground:
                    force = (PLAYER_MOVE_FORCE_ON_GROUND, 0)
                else:
                    force = (PLAYER_MOVE_FORCE_IN_AIR, 0)
                self.physics_engine.apply_force(self.player_sprite, force)
                # Set friction to zero for the player while moving
                self.physics_engine.set_friction(self.player_sprite, 0.5)

            else:
                # Friction is 1 when the player is not moving.
                self.physics_engine.set_friction(self.player_sprite, 1.0)

            # Move items in the physics engine
            self.physics_engine.step(1 / 60)

            # Add vibrating world effect if light radius is above the threshold. Also create falling enemies.
            if self.light_radius > LIGHT_THRESHOLD:
                if self.timer > random.uniform(0.03, 0.1):
                    self.world_list.move(self.world_vibrate, 0)
                    self.player_list.move(self.world_vibrate, 0)
                    self.world_vibrate *= -1
                    self.timer = 0

                    # Add falling enemies
                    if random.randint(0, 20) == 1:
                        self.create_enemy('fall', self.player_sprite.center_x, SCREEN_HEIGHT)

            # To allow player to jump without the 'following' enemy instantly changing direction - too difficult otherwise.
            if self.physics_engine.is_on_ground(self.player_sprite):
                self.jumping = False

            # Update the 'following' enemies.
            for enemy in self.enemy_list:
                enemy.move(self.player_sprite.center_x, self.player_sprite.center_y, self.light_radius, self.jumping)
                enemy.update()

                # Game Over condition 1
                if arcade.check_for_collision(self.player_sprite, enemy) and self.light_radius > 50:
                    if enemy.enemy_type == 'follow':
                        self.game_over = True

            # Game Over condition 2
            if self.player_sprite.center_y <= 0:
                self.game_over = True

            # Switching between levels!
            if self.player_sprite.center_x > SCREEN_WIDTH:
                if self.level < NUM_LEVELS:
                    self.level += 1
                    self.create_world(Levels[self.level])
                    self.create_player(5, self.player_sprite.center_y)
                elif self.level == NUM_LEVELS:
                    self.level += 1
            elif self.player_sprite.center_x < 0 and self.level > 0:
                self.level -= 1
                self.create_world(Levels[self.level])
                self.create_player(SCREEN_WIDTH - 5, self.player_sprite.center_y)

    def on_draw(self):
        """
        Draws objects depending on game_start and game_over.
        """
        if not self.game_start:
            arcade.set_background_color(arcade.color.BLACK)
            self.clear()
            arcade.draw_text(GAME_NAME, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                             arcade.color.RED, font_name='Times', font_size=60, anchor_x='center')

            # Drawing back story - there is also text within the game.
            with open('start_text.txt', 'r') as file:
                lines = file.readlines()
                margin = 30
                for i, line in enumerate(lines):
                    arcade.draw_text(str(line), SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50 - margin * i,
                                     arcade.color.RED, font_name='Times', font_size=20, anchor_x='center')


            # arcade.draw_text('Press ENTER to begin.', SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50,
            #                  arcade.color.RED, font_name='Times', font_size=30, anchor_x='center')

            with open('best_score.txt', 'r') as file:
                score = file.readline()
                arcade.draw_text('Best Time: {}s'.format(round(float(score), 1)), SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 250,
                                 arcade.color.RED, font_name='Times', font_size=20, anchor_x='center')


        elif self.game_start and not self.game_over:
            self.channel0.use()
            self.channel0.clear()
            self.world_list.draw()
            self.background_list.draw()

            for enemy in self.enemy_list:
                if enemy.enemy_type == 'follow':
                    enemy.draw()

            self.channel1.use()
            self.channel1.clear()

            # Custom level text that is revealed with light
            if self.level <= NUM_LEVELS:
                Levels[self.level].text.draw()

            # Selecting this window
            self.use()
            self.clear()
            self.shadertoy.program['lightPosition'] = [self.player_sprite.center_x * 2, self.player_sprite.center_y * 2]
            self.shadertoy.program['lightSize'] = self.light_radius
            self.shadertoy.render()

            self.world_list.draw()
            self.background_list.draw()
            self.player_list.draw()
            for enemy in self.enemy_list:
                enemy.draw()

            # Draw hitbox for debugging
            # self.world_list.draw_hit_boxes(arcade.color.RED, line_thickness=2)

            arcade.draw_text('Level {}'.format(self.level), 30, SCREEN_HEIGHT - 50,
                             arcade.color.RED, font_name='Times', font_size=30, anchor_x='left')
            arcade.draw_text('Time: {}s'.format(round(self.game_timer, 1)), 30, SCREEN_HEIGHT - 80,
                             arcade.color.WHITE, font_name='Times', font_size=20, anchor_x='left')

        elif self.level == NUM_LEVELS + 1:
            # Keeping track of top scores
            with open('best_score.txt', 'r') as file:
                current_score = file.readline()

                if self.game_timer < float(current_score):
                    with open('best_score.txt', 'w') as file:
                        file.write(str(self.game_timer))

            arcade.set_background_color(arcade.color.BLACK)
            self.clear()
            arcade.draw_text('You did it!', SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                             arcade.color.RED, font_name='Times', font_size=60, anchor_x='center')
            arcade.draw_text('Time: {}s'.format(str(round(self.game_timer, 1))), SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50,
                             arcade.color.RED, font_name='Times', font_size=30, anchor_x='center')

        elif self.game_over:

            arcade.set_background_color(arcade.color.BLACK)
            self.clear()
            arcade.draw_text('Game Over.', SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                             arcade.color.RED, font_name='Times', font_size=60, anchor_x='center')
            arcade.draw_text('Press ENTER to start again.', SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50,
                             arcade.color.RED, font_name='Times', font_size=30, anchor_x='center')



    def on_key_press(self, key, modifiers):
        """
        Actions based on key press - player movement, changing light radius.
        """
        if key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True
        elif key == arcade.key.UP:
            if self.physics_engine.is_on_ground(self.player_sprite) and self.light_radius < LIGHT_THRESHOLD:
                impulse = (0, PLAYER_JUMP_IMPULSE)
                self.physics_engine.apply_impulse(self.player_sprite, impulse)

                self.jumping = True

        elif key == arcade.key.X:
            self.change_light_radius = CHANGE_LIGHT_RADIUS
        elif key == arcade.key.Z:
            self.change_light_radius = -CHANGE_LIGHT_RADIUS
        elif key == arcade.key.ENTER:
            self.reset()

        """
        For testing the game - jump to level 4 or 5!
        """
        # Jump to level for debugging
        # if key == arcade.key.P:
        #     # Jump to level 4
        #     self.create_world(Levels[4])
        #     self.create_player(5, 500)
        #     self.level = 4
        # if key == arcade.key.O:
        #     # Jump to level 5
        #     self.create_world(Levels[5])
        #     self.create_player(5, 500)
        #     self.level = 5


    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False

        elif key == arcade.key.X:
            self.change_light_radius = 0
        elif key == arcade.key.Z:
            self.change_light_radius = 0


Levels = []

for i in range(NUM_LEVELS + 1):
    level = Level('level{}'.format(i))
    Levels.append(level)

GameWindow(SCREEN_WIDTH, SCREEN_HEIGHT, GAME_NAME)
arcade.run()
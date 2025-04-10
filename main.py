import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"  # Suppress pygame support prompt
os.environ["SDL_AUDIODRIVER"] = "dsp"  # Use DSP audio driver for better performance

import warnings

with warnings.catch_warnings():
    warnings.simplefilter("ignore", category=RuntimeWarning)
    import pygame

import random
from dataclasses import dataclass


@dataclass
class Settings:
    FPS: int = 60
    WINDOW_WIDTH: int = 800
    WINDOW_HEIGHT: int = 800
    BACKGROUND_COLOR: tuple[int, int, int] = (30, 150, 30)
    COLLECTIBLE_SPAWN_RATE: int = 500
    ENEMY_SPAWN_RATE: int = 4000
    ENEMY_SPEED: float = 2.0
    COLLECTIBLE_SCORE: int = 1
    ENEMY_PENALTY: int = 5
    WINNING_SCORE: int = 30
    LOSING_SCORE: int = 0


# Initialize pygame and set up the window
pygame.init()
width, height = Settings.WINDOW_WIDTH, Settings.WINDOW_HEIGHT
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Applin Sprite Game")
clock = pygame.time.Clock()


# Define the Player sprite that follows the mouse cursor
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        try:
            self.image = pygame.image.load("Applin40.png").convert_alpha()
        except FileNotFoundError:
            self.image = pygame.Surface((40, 40))
            self.image.fill((0, 255, 0))  # Green square
        self.rect = self.image.get_rect()

    def update(self):
        # Update the player's position to follow the mouse
        self.rect.center = pygame.mouse.get_pos()


# Define the Collectible sprite that will disappear when collected
class Collectible(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        try:
            self.image = pygame.image.load("Fluffruit20.png").convert_alpha()
        except FileNotFoundError:
            self.image = pygame.Surface((20, 20))
            self.image.fill((255, 0, 0))  # Red square
        self.rect = self.image.get_rect(center=pos)


# Define the Enemy sprite that will lower the player's score when touched
class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        try:
            self.image = pygame.image.load("Koffing20.png").convert_alpha()
        except FileNotFoundError:
            self.image = pygame.Surface((20, 20))
            self.image.fill((0, 0, 255))  # Blue square
        self.rect = self.image.get_rect(center=pos)
        self.speed = Settings.ENEMY_SPEED  # Default speed of the enemy

    def update(self):
        # Move the enemy toward the player's position
        player_pos = player.rect.center
        direction_x = player_pos[0] - self.rect.centerx
        direction_y = player_pos[1] - self.rect.centery
        distance = (direction_x**2 + direction_y**2) ** 0.5

        # Adjust speed based on distance
        if distance > 240:
            self.speed = 2 * Settings.ENEMY_SPEED  # Move quickly when far away
        elif distance < 100:
            self.speed = 0.75 * Settings.ENEMY_SPEED  # Move slower when close
        else:
            self.speed = Settings.ENEMY_SPEED  # Default speed

        if distance != 0:  # Avoid division by zero
            direction_x /= distance
            direction_y /= distance

        # Add random motion
        random_offset_x = random.uniform(-1, 1)
        random_offset_y = random.uniform(-1, 1)
        direction_x += random_offset_x
        direction_y += random_offset_y

        # Normalize the direction again after adding randomness
        distance = (direction_x**2 + direction_y**2) ** 0.5
        if distance != 0:
            direction_x /= distance
            direction_y /= distance

        # Move the enemy in the direction of the player
        self.rect.x += int(direction_x * self.speed)
        self.rect.y += int(direction_y * self.speed)


# Create sprite groups for easy management
all_sprites: pygame.sprite.Group = pygame.sprite.Group()
collectibles: pygame.sprite.Group = pygame.sprite.Group()
enemies: pygame.sprite.Group = pygame.sprite.Group()

# Create the player and add it to the group
player = Player()
all_sprites.add(player)

# Create several collectibles at random positions
for _ in range(10):
    pos = (random.randint(20, width - 20), random.randint(20, height - 20))
    collectible = Collectible(pos)
    all_sprites.add(collectible)
    collectibles.add(collectible)

# Create several enemies at random positions
for _ in range(5):
    pos = (random.randint(20, width - 20), random.randint(20, height - 20))
    enemy = Enemy(pos)
    all_sprites.add(enemy)
    enemies.add(enemy)

score = 0

# Load font for displaying score
font = pygame.font.SysFont(None, 36)

# Set a timer event to add a new collectible every 0.5 seconds (500 milliseconds)
NEW_COLLECTIBLE_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(NEW_COLLECTIBLE_EVENT, Settings.COLLECTIBLE_SPAWN_RATE)

# Set a timer event to add a new enemy every 4 seconds (4000 milliseconds)
NEW_ENEMY_EVENT = pygame.USEREVENT + 2
pygame.time.set_timer(NEW_ENEMY_EVENT, Settings.ENEMY_SPAWN_RATE)

pygame.mouse.set_visible(False)

# Main game loop
running = True
while running:
    clock.tick(Settings.FPS)  # Limit the frame rate to 60 FPS

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == NEW_COLLECTIBLE_EVENT:
            # When the timer event fires, add a new collectible at a random position
            pos = (random.randint(20, width - 20), random.randint(20, height - 20))
            collectible = Collectible(pos)
            all_sprites.add(collectible)
            collectibles.add(collectible)
        elif event.type == NEW_ENEMY_EVENT:
            # When the timer event fires, add a new enemy at a random position
            pos = (random.randint(20, width - 20), random.randint(20, height - 20))
            enemy = Enemy(pos)
            all_sprites.add(enemy)
            enemies.add(enemy)

    # Update all sprites (player follows the mouse)
    all_sprites.update()

    # Check for collisions between the player and collectibles
    hits = pygame.sprite.spritecollide(player, collectibles, True)
    if hits:
        score += (
            len(hits) * Settings.COLLECTIBLE_SCORE
        )  # Increase score for each collectible hit

    # Check for collisions between the player and enemies
    enemy_hits = pygame.sprite.spritecollide(player, enemies, True)
    if enemy_hits:
        score -= (
            len(enemy_hits) * Settings.ENEMY_PENALTY
        )  # Decrease score for each enemy hit

    # Draw everything on the screen
    screen.fill(Settings.BACKGROUND_COLOR)  # Background color
    all_sprites.draw(screen)
    if score > Settings.WINNING_SCORE:
        score_text = font.render("YOU WIN", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
    elif score < Settings.LOSING_SCORE:
        score_text = font.render("YOU LOSE", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
    else:
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
    pygame.display.flip()

pygame.quit()

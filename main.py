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
    """Game settings and constants."""

    FPS: int = 60
    WINDOW_WIDTH: int = 800
    WINDOW_HEIGHT: int = 800
    BACKGROUND_COLOR: tuple[int, int, int] = (30, 150, 30)
    COLLECTIBLE_SPAWN_RATE: int = 500
    ENEMY_SPAWN_RATE: int = 4000
    ENEMY_SPEED: float = 2.0
    ENEMY_RANDOMNESS: float = 0.5
    ENEMY_FAST_DISTANCE: int = 240
    ENEMY_SLOW_DISTANCE: int = 100
    COMPETITOR_SPEED: float = 3.0
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


class Player(pygame.sprite.Sprite):
    """Player sprite that follows the mouse cursor."""

    def __init__(self):
        super().__init__()
        try:
            self.image = pygame.image.load("Applin40.png").convert_alpha()
        except FileNotFoundError:
            self.image = pygame.Surface((40, 40))
            self.image.fill((0, 255, 0))  # Green square
        self.rect = self.image.get_rect()

    def update(self) -> None:
        # Update the player's position to follow the mouse
        self.rect.center = pygame.mouse.get_pos()

    def evolve(self) -> None:
        """Evolve the player by changing its image."""

        try:
            self.image = pygame.image.load("Flapple80.png").convert_alpha()
        except FileNotFoundError:
            self.image = pygame.Surface((80, 80))
            self.image.fill((255, 255, 0))  # Yellow square
        self.rect = self.image.get_rect(center=self.rect.center)


class Collectible(pygame.sprite.Sprite):
    """Collectible sprite that increases the player's score when collected."""

    def __init__(self, pos: tuple[int, int]):
        super().__init__()
        try:
            self.image = pygame.image.load("Fluffruit20.png").convert_alpha()
        except FileNotFoundError:
            self.image = pygame.Surface((20, 20))
            self.image.fill((255, 0, 0))  # Red square
        self.rect = self.image.get_rect(center=pos)


class Enemy(pygame.sprite.Sprite):
    """Enemy sprite that decreases the player's score when touched."""

    def __init__(self, pos: tuple[int, int]):
        super().__init__()
        try:
            self.image = pygame.image.load("Koffing20.png").convert_alpha()
        except FileNotFoundError:
            self.image = pygame.Surface((20, 20))
            self.image.fill((0, 0, 255))  # Blue square
        self.rect = self.image.get_rect(center=pos)
        self.speed = Settings.ENEMY_SPEED  # Default speed of the enemy

    def update(self) -> None:
        # Move the enemy toward the player's position
        player_pos = player.rect.center
        direction_x = player_pos[0] - self.rect.centerx
        direction_y = player_pos[1] - self.rect.centery
        distance = (direction_x**2 + direction_y**2) ** 0.5

        # Adjust speed based on distance
        if distance > Settings.ENEMY_FAST_DISTANCE:
            self.speed = 2 * Settings.ENEMY_SPEED  # Move quickly when far away
        elif distance < Settings.ENEMY_SLOW_DISTANCE:
            self.speed = 0.75 * Settings.ENEMY_SPEED  # Move slower when close
        else:
            self.speed = Settings.ENEMY_SPEED  # Default speed

        if distance != 0:  # Avoid division by zero
            direction_x /= distance
            direction_y /= distance

        # Add random motion
        random_offset_x = random.uniform(
            -Settings.ENEMY_RANDOMNESS, Settings.ENEMY_RANDOMNESS
        )
        random_offset_y = random.uniform(
            -Settings.ENEMY_RANDOMNESS, Settings.ENEMY_RANDOMNESS
        )
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


class Competitor(pygame.sprite.Sprite):
    """Competitor sprite that moves towards the nearest collectible."""

    def __init__(self, pos: tuple[int, int]):
        super().__init__()
        try:
            self.image = pygame.image.load("Applin4.png").convert_alpha()
        except FileNotFoundError:
            self.image = pygame.Surface((40, 40))
            self.image.fill((255, 165, 0))  # Orange square
        self.rect = self.image.get_rect(center=pos)
        self.speed = Settings.COMPETITOR_SPEED

    def update(self, collectibles: pygame.sprite.Group | None = None) -> None:
        if collectibles:
            # Find the nearest collectible
            nearest_collectible = min(
                collectibles,
                key=lambda c: self.rect.centerx
                - c.rect.centerx
                + self.rect.centery
                - c.rect.centery,
            )
            direction_x = nearest_collectible.rect.centerx - self.rect.centerx
            direction_y = nearest_collectible.rect.centery - self.rect.centery
            distance = (direction_x**2 + direction_y**2) ** 0.5

            if distance != 0:  # Avoid division by zero
                direction_x /= distance
                direction_y /= distance

            # Move the competitor towards the collectible
            self.rect.x += int(direction_x * self.speed)
            self.rect.y += int(direction_y * self.speed)

            # Check for collision with the collectible
            if self.rect.colliderect(nearest_collectible.rect):
                nearest_collectible.kill()  # Remove the collectible on collision


# Create sprite groups for easy management
all_sprites: pygame.sprite.Group = pygame.sprite.Group()
collectibles: pygame.sprite.Group = pygame.sprite.Group()
enemies: pygame.sprite.Group = pygame.sprite.Group()
competitors: pygame.sprite.Group = pygame.sprite.Group()

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

# Create a competitor and add it to the group
competitor = Competitor(
    ((random.randint(20, width - 20), random.randint(20, height - 20)))
)
all_sprites.add(competitor)
competitors.add(competitor)

score = 0

# Load font for displaying score
font = pygame.font.SysFont(None, 36)

# Set a timer event to add a new collectible every 0.5 seconds (500 milliseconds)
NEW_COLLECTIBLE_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(NEW_COLLECTIBLE_EVENT, Settings.COLLECTIBLE_SPAWN_RATE)

# Set a timer event to add a new enemy every 4 seconds (4000 milliseconds)
NEW_ENEMY_EVENT = pygame.USEREVENT + 2
pygame.time.set_timer(NEW_ENEMY_EVENT, Settings.ENEMY_SPAWN_RATE)

# Hide the mouse cursor in the game window
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

    # Update competitors
    for competitor in competitors:
        competitor.update(collectibles)

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
        player.evolve()  # Evolve the player sprite
    elif score < Settings.LOSING_SCORE:
        score_text = font.render("YOU LOSE", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
    else:
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
    pygame.display.flip()

pygame.quit()

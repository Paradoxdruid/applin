import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"  # Hide the pygame welcome message
import pygame
import random

# Initialize pygame and set up the window
pygame.init()
width, height = 800, 800
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Mouse Sprite Game")
clock = pygame.time.Clock()


# Define the Player sprite that follows the mouse cursor
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # self.image = pygame.Surface((40, 40))
        # self.image.fill((0, 255, 0))  # Green square
        self.image = pygame.image.load("Applin40.png").convert_alpha()
        self.rect = self.image.get_rect()

    def update(self):
        # Update the player's position to follow the mouse
        self.rect.center = pygame.mouse.get_pos()

    def enlarge(self, scale_factor=1.0):
        # Define the scaling factor (1% larger means a factor of 1.01)

        # Determine new dimensions based on the current image size
        new_width = int(self.image.get_width() * scale_factor)
        new_height = int(self.image.get_height() * scale_factor)
        # Scale the image to the new dimensions
        self.image = pygame.transform.scale(self.image, (new_width, new_height))
        # Update the rect. Using center=self.rect.center maintains the sprite's center.
        self.rect = self.image.get_rect(center=self.rect.center)


# Define the Collectible sprite that will disappear when collected
class Collectible(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        # self.image = pygame.Surface((20, 20))
        # self.image.fill((255, 0, 0))  # Red square
        self.image = pygame.image.load("Fluffruit20.png").convert_alpha()
        self.rect = self.image.get_rect(center=pos)


# Define the Enemy sprite that will lower the player's score when touched
class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        # self.image = pygame.Surface((20, 20))
        # self.image.fill((255, 0, 0))  # Red square
        self.image = pygame.image.load("Koffing20.png").convert_alpha()
        self.rect = self.image.get_rect(center=pos)


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
font = pygame.font.SysFont(None, 36)

# Set a timer event to add a new collectible every 2 seconds (2000 milliseconds)
NEW_COLLECTIBLE_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(NEW_COLLECTIBLE_EVENT, 500)

# Set a timer event to add a new enemy every 4 seconds (4000 milliseconds)
NEW_ENEMY_EVENT = pygame.USEREVENT + 2
pygame.time.set_timer(NEW_ENEMY_EVENT, 4000)

pygame.mouse.set_visible(False)

# Main game loop
running = True
while running:
    clock.tick(60)  # Limit the frame rate to 60 FPS

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
            # When the timer event fires, add a new collectible at a random position
            pos = (random.randint(20, width - 20), random.randint(20, height - 20))
            enemy = Enemy(pos)
            all_sprites.add(enemy)
            enemies.add(enemy)

    # Update all sprites (player follows the mouse)
    all_sprites.update()

    # Check for collisions between the player and collectibles
    hits = pygame.sprite.spritecollide(player, collectibles, True)
    if hits:
        player.enlarge()
        score += len(hits)  # Increase score for each collectible hit

    # Check for collisions between the player and enemies
    enemy_hits = pygame.sprite.spritecollide(player, enemies, True)
    if enemy_hits:
        score -= 5 * len(enemy_hits)  # Decrease score for each enemy hit

    # Draw everything on the screen
    screen.fill((30, 150, 30))  # Background color
    all_sprites.draw(screen)
    if score > 25:
        score_text = font.render("YOU WIN", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
    else:
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
    pygame.display.flip()

pygame.quit()

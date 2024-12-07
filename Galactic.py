import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Initialize the mixer for sound effects
pygame.mixer.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Galactic Shooter")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Level system variables
level = 1
score_for_next_level = 150

# Clock
clock = pygame.time.Clock()
FPS = 60

# Load assets
ship_img = pygame.image.load("spaceship.png")
ship_img = pygame.transform.scale(ship_img, (50, 50))
bullet_img = pygame.image.load("bullet.png")
bullet_img = pygame.transform.scale(bullet_img, (20, 20))

# Load enemy bullet image
enemy_bullet_img = pygame.image.load("enemy_bullet.png")
enemy_bullet_img = pygame.transform.scale(enemy_bullet_img, (20, 20))  # Adjust size of enemy bullet image

# Load different enemy images for each type
enemy_images = [
    pygame.image.load("enemy1.png"),
    pygame.image.load("enemy2.png"),
    pygame.image.load("enemy3.png"),
]
enemy_images = [pygame.transform.scale(img, (50, 50)) for img in enemy_images]

# Load sound effects
shot_sound = pygame.mixer.Sound("shot_sound.wav")
enemy_hit_sound = pygame.mixer.Sound("enemy_hit_sound.wav")
player_hit_sound = pygame.mixer.Sound("player_hit_sound.wav")
game_over_sound = pygame.mixer.Sound("game_over_sound.wav")
power_up_sounds = pygame.mixer.Sound("power_up_sound.wav")

# Load heart image for health representation
heart_img = pygame.image.load("spaceship.png")  # Load your heart image
heart_img = pygame.transform.scale(heart_img, (30, 30))  # Adjust size

# Player variables
player_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT - 70]
player_size = 50
player_speed = 5
player_health = 3  # Initial health is 3

# Bullet variables
bullets = []
bullet_speed = -10

# Enemy variables
enemies = []
enemy_speed_y = 3  # Vertical speed
enemy_speed_x = 2  # Horizontal speed
spawn_timer = 30  # Spawn a new enemy every 30 frames

# Enemy bullets
enemy_bullets = []
enemy_bullet_speed = 5

# Score
score = 0
font = pygame.font.SysFont("ROBOT", 30)

# Larger font for GAME OVER
game_over_font = pygame.font.SysFont("ROBOT", 100)
retry_font = pygame.font.SysFont("ROBOT", 50)

# Star positions (updated globally for smooth movement)
stars = [[random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)] for _ in range(100)]

# Blink variables
blink_duration = 15  # Number of frames the blink lasts
blink_timer = 0  # Timer for tracking blink duration
is_blinking = False  # Flag to check if blinking is active

# Load asteroid image
asteroid_img = pygame.image.load("asteroid1.png")
asteroid_img = pygame.transform.scale(asteroid_img, (70, 70))  # Adjust size

# Asteroid positions (we'll generate random positions and move them down)
asteroids = [[random.randint(0, SCREEN_WIDTH - 50), random.randint(-SCREEN_HEIGHT, 0)] for _ in range(5)]  # 5 asteroids to start with

# Function to display level
def draw_level():
    level_text = font.render(f"Level: {level}", True, GREEN)
    screen.blit(level_text, (10, 50))  # Display level at (10, 50) position

# Function to draw and move asteroids
def draw_asteroids():
    for asteroid in asteroids:
        screen.blit(asteroid_img, (asteroid[0], asteroid[1]))  # Draw the asteroid
        asteroid[1] += 1  # Move asteroid downwards (adjust the speed if necessary)

        # Reset asteroid to the top if it goes off-screen
        if asteroid[1] > SCREEN_HEIGHT:
            asteroid[1] = random.randint(-SCREEN_HEIGHT, 0)  # Reset to a random top position
            asteroid[0] = random.randint(0, SCREEN_WIDTH - 50)  # Randomize x-position

# Function to draw stars
def draw_stars():
    for star in stars:
        pygame.draw.circle(screen, WHITE, (star[0], star[1]), 2)
        star[1] += 1  # Slow down star movement (adjusted for smooth effect)
        if star[1] > SCREEN_HEIGHT:
            star[1] = 0  # Reset star to top
            star[0] = random.randint(0, SCREEN_WIDTH)  # Randomize x-position

# Function to display score
def draw_score():
    score_text = font.render(f"Score: {score}", True, GREEN)
    screen.blit(score_text, (10, 10))

# Function to display health bars at the top-right corner
def draw_health_bars():
    for i in range(player_health):
        screen.blit(heart_img, (SCREEN_WIDTH - 40 * (i + 1), 10))  # Draw health bars

# Function to check for collision between player and enemy
def check_collision(player_pos, enemy_pos, player_size, enemy_size):
    player_rect = pygame.Rect(player_pos[0], player_pos[1], player_size, player_size)
    enemy_rect = pygame.Rect(enemy_pos[0], enemy_pos[1], enemy_size, enemy_size)
    return player_rect.colliderect(enemy_rect)

# Function to check for collision between player and enemy bullets
def check_bullet_collision(player_pos, enemy_bullet, player_size):
    bullet_rect = pygame.Rect(enemy_bullet[0], enemy_bullet[1], 10, 20)  # Size of the enemy bullet image
    player_rect = pygame.Rect(player_pos[0], player_pos[1], player_size, player_size)
    return player_rect.colliderect(bullet_rect)

# Function to spawn enemies with random horizontal movement direction
def spawn_enemy():
    direction = random.choice([0, 1, -1])  # 0 = vertical, 1 = left to right, -1 = right to left
    enemy_image = random.choice(enemy_images)  # Randomly select an enemy image
    return [random.randint(0, SCREEN_WIDTH - 50), 0, direction, enemy_image]  # Return enemy with image

# Function to spawn enemy bullets
def spawn_enemy_bullet(enemy_pos):
    bullet_x = enemy_pos[0] + 25  # Position the bullet slightly towards the center of the enemy
    bullet_y = enemy_pos[1] + 50  # Spawn the bullet just below the enemy
    return [bullet_x, bullet_y]  # Return bullet position

# Function to update bullets
def update_bullets(bullets):
    new_bullets = []
    for bullet in bullets:
        bullet[1] += bullet_speed  # Move the bullet upward
        if bullet[1] > 0:  # Keep bullets on screen
            new_bullets.append(bullet)
    return new_bullets

# Function to update enemy bullets
def update_enemy_bullets(enemy_bullets):
    new_enemy_bullets = []
    for bullet in enemy_bullets:
        bullet[1] += enemy_bullet_speed  # Move the enemy bullet downwards
        if bullet[1] < SCREEN_HEIGHT:  # Keep bullets on screen
            new_enemy_bullets.append(bullet)
    return new_enemy_bullets

# Function to draw bullets
def draw_bullets(bullets):
    for bullet in bullets:
        screen.blit(bullet_img, (bullet[0], bullet[1]))  # Draw the bullet

# Function to draw enemy bullets
def draw_enemy_bullets(enemy_bullets):
    for bullet in enemy_bullets:
        screen.blit(enemy_bullet_img, (bullet[0], bullet[1]))  # Draw enemy bullets using the enemy_bullet.png image

# Game loop
running = True
frame_count = 0

# Continuous bullet firing interval (in frames)
bullet_interval = 20
bullet_timer = bullet_interval  # Timer to manage continuous bullet firing

# Function to check for collision between player and enemy
def check_player_enemy_collision(player_pos, enemy_pos, player_size, enemy_size):
    player_rect = pygame.Rect(player_pos[0], player_pos[1], player_size, player_size)
    enemy_rect = pygame.Rect(enemy_pos[0], enemy_pos[1], enemy_size, enemy_size)
    return player_rect.colliderect(enemy_rect)

# Load power-up images
health_powerup_img = pygame.image.load("health_power_up.png")
health_powerup_img = pygame.transform.scale(health_powerup_img, (80, 50))  # Adjust size

# Power-Up Variables
power_ups = []  # List to hold active power-ups
power_up_speed = 3  # Power-up falling speed


# Power-Up Classes
class PowerUp:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type  # 'health'
        self.image = health_powerup_img 
        self.rect = pygame.Rect(self.x, self.y, 30, 30)

    def move(self):
        self.y += power_up_speed  # Move the power-up downwards
        self.rect.y = self.y  # Update rect for collision

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

# Function to spawn a random power-up
def spawn_power_up():
    x = random.randint(0, SCREEN_WIDTH - 30)
    type = random.choice(['health'])  # Randomly select type
    return PowerUp(x, 0, type)

# Function to check collision between player and power-up
def check_power_up_collision(player_pos, player_size, power_up):
    player_rect = pygame.Rect(player_pos[0], player_pos[1], player_size, player_size)
    return player_rect.colliderect(power_up.rect)

# Function to handle level progression
def handle_level_progression():
    global level, enemy_speed_y, enemy_speed_x, spawn_timer, score_for_next_level

    if score >= score_for_next_level:
        level += 1  # Level up
        score_for_next_level += 150  # Increase the score needed for the next level

        # Increase difficulty
        enemy_speed_y += 0  # Faster vertical movement for enemies
        enemy_speed_x += 1  # Faster horizontal movement for enemies
        spawn_timer = max(15, spawn_timer - 5)  # Faster spawn rate (with a minimum cap)

# Power-up management
power_up_timer = 0
bullet_speed_timer = 0
bullet_speed_active = False

# Function to reset the game state
def reset_game():
    global level, score, player_health, player_pos, bullets, enemies, enemy_bullets, power_ups
    global frame_count, spawn_timer, score_for_next_level, is_blinking, blink_timer, power_up_timer

    level = 1
    score = 0
    player_health = 3
    player_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT - 70]
    bullets = []
    enemies = []
    enemy_bullets = []
    power_ups = []
    frame_count = 0
    spawn_timer = 30
    score_for_next_level = 150
    is_blinking = False
    blink_timer = 0
    power_up_timer = 0

# Game loop (with updated collision handling)
while running:
    screen.fill(BLACK)  # Fill the background with black

    # Draw stars
    draw_stars()

    # Draw asteroids in the background
    draw_asteroids()

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_pos[0] > 0:
        player_pos[0] -= player_speed
    if keys[pygame.K_RIGHT] and player_pos[0] < SCREEN_WIDTH - player_size:
        player_pos[0] += player_speed
    if keys[pygame.K_UP] and player_pos[1] > 0:
        player_pos[1] -= player_speed
    if keys[pygame.K_DOWN] and player_pos[1] < SCREEN_HEIGHT - player_size:
        player_pos[1] += player_speed

    # Handle bullet firing every `bullet_interval` frames
    bullet_timer -= 1
    if bullet_timer <= 0:
        bullets.append([player_pos[0] + player_size // 2 - 5, player_pos[1]])  # Add bullet at player's position
        bullet_timer = bullet_interval  # Reset the bullet timer
        shot_sound.play()  # Play shot sound when bullet is fired

    # Update bullets
    bullets = update_bullets(bullets)

    # Spawn enemies
    frame_count += 1
    if frame_count % spawn_timer == 0:
        enemies.append(spawn_enemy())

    # Update enemies and handle collisions
    new_enemies = []
    for enemy in enemies:
        enemy[1] += enemy_speed_y  # Move the enemy vertically

        # Move horizontally if necessary
        if enemy[2] != 0:  # If the direction is not 0 (vertical), move horizontally
            enemy[0] += enemy[2] * enemy_speed_x  # Move left or right
        
        # Keep enemy within screen boundaries
        if enemy[0] < 0:  
            enemy[0] = 0  # Keep it on the left
        elif enemy[0] > SCREEN_WIDTH - 50:
            enemy[0] = SCREEN_WIDTH - 50  # Keep it on the right
        
        # Enemy bullet firing logic
        if random.randint(1, 100) < 2:  # 2% chance of firing
            enemy_bullets.append(spawn_enemy_bullet(enemy))

        # Check for collisions with the player
        if check_player_enemy_collision(player_pos, enemy, player_size, 50):  # 50 is enemy size
            if not is_blinking:  # Only trigger blinking if not already blinking
                player_health -= 1
                is_blinking = True
                blink_timer = blink_duration  # Set blink duration
                player_hit_sound.play() 

        # Check for collisions with bullets
        collision = False
        for bullet in bullets:
            if (
                bullet[0] > enemy[0]
                and bullet[0] < enemy[0] + 50
                and bullet[1] > enemy[1]
                and bullet[1] < enemy[1] + 50
            ):
                enemy_hit_sound.play()
                score += 10
                collision = True
                break

        if not collision:
            new_enemies.append(enemy)  # Add the enemy if no collision occurred # Update the list of enemies
    enemies = new_enemies

    # Handle level progression
    handle_level_progression()

    # Update power-ups
    if power_up_timer <= 0:
        power_ups.append(spawn_power_up())  # Spawn a new power-up
        power_up_timer = random.randint(150, 300)  # Random time between power-up spawns

    power_up_timer -= 1  # Decrease the timer for the next spawn

    # Move and draw power-ups
    for power_up in power_ups:
        power_up.move()
        power_up.draw()
    
        # Check for collision with player
        if check_power_up_collision(player_pos, player_size, power_up):
            if power_up.type == 'health' and player_health < 3:
                player_health += 1  # Increase player health
                power_ups.remove(power_up)
                power_up_sounds.play()

    # Update enemy bullets
    enemy_bullets = update_enemy_bullets(enemy_bullets)

    # Check for collisions with player from enemy bullets
    for enemy_bullet in enemy_bullets:
        if check_bullet_collision(player_pos, enemy_bullet, player_size):
            if not is_blinking:  # Only trigger blinking if not already blinking
                player_health -= 1
                is_blinking = True
                blink_timer = blink_duration  # Set blink duration
                player_hit_sound.play()

    # Check if player health is below 1
    if player_health <= 0:
        game_over_sound.play()
        game_over_text = game_over_font.render("GAME OVER", True, RED)
        retry_text = retry_font.render("Press R to Retry", True, RED)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 50)) 
        screen.blit(retry_text, (SCREEN_WIDTH // 2 - 105, SCREEN_HEIGHT // 2 + 40))
        pygame.display.update()
        pygame.time.delay(4000)  # Wait for 4 seconds before showing retry option

        # Retry logic
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:  # If 'R' is pressed, reset the game
                        reset_game()
                        break
            else:
                continue  # Only break the outer loop if the inner loop was broken
            break  # Break the outer loop if the game is reset

    # Player blinking logic
    if is_blinking:
        blink_timer -= 1
        if blink_timer <= 0:
            is_blinking = False  # Stop blinking after the duration

    # Draw player ship (skip drawing if blinking)
    if not is_blinking:
        screen.blit(ship_img, (player_pos[0], player_pos[1]))

    # Draw enemies
    for enemy in enemies:
        screen.blit(enemy[3], (enemy[0], enemy[1]))  # Draw enemy using its image

    # Draw bullets and enemies
    draw_bullets(bullets)
    draw_enemy_bullets(enemy_bullets)

    # Draw health and score
    draw_health_bars()
    draw_score()

    # Draw level
    draw_level()

    # Update screen
    pygame.display.update()

    # Set the game frame rate
    clock.tick(FPS)


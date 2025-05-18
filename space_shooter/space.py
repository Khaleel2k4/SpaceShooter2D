import pygame
import random
import sys

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (70, 130, 180)
YELLOW = (255, 255, 0)

# Fonts
font_small = pygame.font.SysFont("Arial", 24)
font_medium = pygame.font.SysFont("Arial", 36)
font_large = pygame.font.SysFont("Arial", 50)

# Game variables
FPS = 60
clock = pygame.time.Clock()

# Create simple graphics
def create_ship_image(color, points):
    img = pygame.Surface((50, 40), pygame.SRCALPHA)
    pygame.draw.polygon(img, color, points)
    return img

player_img = create_ship_image(BLUE, [(25, 0), (0, 40), (50, 40)])
enemy_img = create_ship_image(RED, [(25, 40), (0, 0), (50, 0)])
bullet_img = pygame.Surface((8, 20))
bullet_img.fill(GREEN)

# Create silent sounds
def create_silent_sound():
    sound = pygame.mixer.Sound(buffer=bytes([128]*8000))  # Silent sound
    return sound

shoot_sound = create_silent_sound()
explosion_sound = create_silent_sound()


# Sprite classes
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect(center=(WIDTH//2, HEIGHT-50))
        self.speed = 8
        self.health = 100
        self.shoot_delay = 250  # milliseconds
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += self.speed
            
        # Keep player on screen
        self.rect.x = max(0, min(self.rect.x, WIDTH - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, HEIGHT - self.rect.height))

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullet = Bullet(self.rect.centerx, self.rect.top)
            all_sprites.add(bullet)
            bullets.add(bullet)
            shoot_sound.play()

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect(
            x=random.randint(0, WIDTH - 50),
            y=random.randint(-100, -40))
        self.speed = random.randint(1, 4)
        self.health = 30

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.y = random.randint(-100, -40)
            self.rect.x = random.randint(0, WIDTH - 50)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = bullet_img
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 10

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()

# UI Functions
def draw_text(text, font, color, x, y, center=False):
    text_surface = font.render(text, True, color)
    if center:
        text_rect = text_surface.get_rect(center=(x, y))
        screen.blit(text_surface, text_rect)
    else:
        screen.blit(text_surface, (x, y))

def draw_health_bar(surface, x, y, health, max_health=100):
    BAR_LENGTH = 200
    BAR_HEIGHT = 20
    fill = (health / max_health) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surface, GREEN, fill_rect)
    pygame.draw.rect(surface, WHITE, outline_rect, 2)

def draw_button(rect, text, color, hover_color):
    mouse_pos = pygame.mouse.get_pos()
    current_color = hover_color if rect.collidepoint(mouse_pos) else color
    
    pygame.draw.rect(screen, current_color, rect, border_radius=5)
    pygame.draw.rect(screen, WHITE, rect, 2, border_radius=5)
    draw_text(text, font_medium, WHITE, rect.centerx, rect.centery, center=True)
    
    return rect.collidepoint(mouse_pos)

# Game States
def main_menu():
    while True:
        screen.fill(BLACK)
        
        # Title
        draw_text("SPACE SHOOTER", font_large, YELLOW, WIDTH//2, 100, center=True)
        
        # Buttons
        start_button = pygame.Rect(WIDTH//2 - 100, 250, 200, 50)
        quit_button = pygame.Rect(WIDTH//2 - 100, 350, 200, 50)
        
        start_hover = draw_button(start_button, "START", BLUE, (100, 100, 255))
        quit_hover = draw_button(quit_button, "QUIT", RED, (255, 100, 100))
        
        # Controls info
        draw_text("Controls: Arrow Keys/WASD to move, SPACE to shoot", 
                 font_small, WHITE, WIDTH//2, 500, center=True)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_hover:
                    return "game"
                if quit_hover:
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_RETURN:
                    return "game"
        
        pygame.display.flip()
        clock.tick(FPS)

def game_over_screen(score):
    while True:
        screen.fill(BLACK)
        
        draw_text("GAME OVER", font_large, RED, WIDTH//2, 100, center=True)
        draw_text(f"Final Score: {score}", font_medium, WHITE, WIDTH//2, 180, center=True)
        
        retry_button = pygame.Rect(WIDTH//2 - 100, 250, 200, 50)
        menu_button = pygame.Rect(WIDTH//2 - 100, 350, 200, 50)
        
        retry_hover = draw_button(retry_button, "RETRY", BLUE, (100, 100, 255))
        menu_hover = draw_button(menu_button, "MENU", GREEN, (100, 255, 100))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if retry_hover:
                    return "game"
                if menu_hover:
                    return "menu"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return "game"
                if event.key == pygame.K_ESCAPE:
                    return "menu"
        
        pygame.display.flip()
        clock.tick(FPS)

def game_loop():
    global all_sprites, bullets, enemies
    
    # Sprite groups
    all_sprites = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    
    # Create player
    player = Player()
    all_sprites.add(player)
    
    # Create initial enemies
    for _ in range(8):
        enemy = Enemy()
        all_sprites.add(enemy)
        enemies.add(enemy)
    
    score = 0
    running = True
    
    while running:
        # Keep loop running at the right speed
        clock.tick(FPS)
        
        # Process input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_SPACE:
                    player.shoot()
        
        # Update
        all_sprites.update()
        
        # Check for bullet-enemy collisions
        hits = pygame.sprite.groupcollide(bullets, enemies, True, True)
        for hit in hits:
            score += 10
            explosion_sound.play()
            # Spawn new enemy
            enemy = Enemy()
            all_sprites.add(enemy)
            enemies.add(enemy)
        
        # Check for player-enemy collisions
        hits = pygame.sprite.spritecollide(player, enemies, False)
        if hits:
            player.health -= 0.5  # Gradual damage
            if player.health <= 0:
                running = False
        
        # Render
        screen.fill(BLACK)
        
        # Draw all sprites
        all_sprites.draw(screen)
        
        # Draw UI
        draw_text(f"SCORE: {score}", font_small, WHITE, 10, 10)
        draw_health_bar(screen, 10, 40, player.health)
        
        pygame.display.flip()
    
    return "game_over", score

# Main game loop
def main():
    game_state = "menu"
    
    while True:
        if game_state == "menu":
            game_state = main_menu()
        elif game_state == "game":
            game_state, score = game_loop()
        elif game_state == "game_over":
            game_state = game_over_screen(score)

if __name__ == "__main__":
    main()
    pygame.quit()
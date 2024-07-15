
import pygame
import random
import sys

pygame.init()

# Set the window size to match the background image resolution
WIDTH, HEIGHT = 1920, 1080
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Quati Iguaçu")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (192, 192, 192)
PURPLE = (128, 0, 128)
PINK = (255, 192, 203)

# Game Constants
FPS = 60
FONT = pygame.font.SysFont('Arial', 24)

# Assets
PENNY_IMG = pygame.image.load('penny.png')
CLIENT_IMG = pygame.image.load('client.png')
TABLE_IMG = pygame.image.load('table.png')
RESTING_POINT_IMG = pygame.image.load('restingPoint.png')
BACKGROUND_IMG = pygame.image.load('background.png')

# Classes
class Button:
    def __init__(self, x, y, w, h, text, color):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        screen.blit(FONT.render(self.text, True, BLACK), (self.rect.x + 10, self.rect.y + 10))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class Client(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((50, 50))  # Use a Surface to draw colors
        self.image.fill(GRAY)  # Default color
        self.rect = self.image.get_rect(topleft=(x, y))
        self.wait_time = 600  # 10 seconds * 60 FPS
        self.state = 'waiting'  # waiting, selected, moving, sitting, served, waiting_for_food, eating
        self.table = None
        self.target_pos = None
        self.speed = 5  # Speed of the clients
        self.order_time = None
        self.order = None
        self.order_active = False

    def update(self):
        if self.state == 'waiting':
            self.wait_time -= 1
            if self.wait_time <= 0:
                self.kill()
        elif self.state == 'moving':
            self.move()
        elif self.state == 'sitting' and not self.order_active:
            if self.order_time is None:
                self.order_time = pygame.time.get_ticks()
            elif pygame.time.get_ticks() - self.order_time >= 10000:  # 10 seconds
                self.order = random.randint(1, 5)
                self.order_active = True
                print(f"Client at {self.rect.topleft} ordered {self.order}")

    def move(self):
        if self.target_pos:
            target_x, target_y = self.target_pos
            if self.rect.x < target_x:
                self.rect.x += self.speed
            elif self.rect.x > target_x:
                self.rect.x -= self.speed
            if self.rect.y < target_y:
                self.rect.y += self.speed
            elif self.rect.y > target_y:
                self.rect.y -= self.speed
            if abs(self.rect.x - target_x) < self.speed and abs(self.rect.y - target_y) < self.speed:
                self.target_pos = None
                self.state = 'sitting'

    def draw(self, screen):
        color = GREEN if self.state == 'selected' else BLUE if self.state in ['sitting', 'waiting_for_food'] else GRAY
        self.image.fill(color)
        screen.blit(self.image, self.rect.topleft)
        if self.order_active:
            order_text = FONT.render(str(self.order), True, BLACK)
            pygame.draw.circle(screen, WHITE, (self.rect.centerx, self.rect.top - 20), 20)
            screen.blit(order_text, (self.rect.centerx - order_text.get_width() // 2, self.rect.top - 30))

class Table(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill(PURPLE)  # Purple color for debugging
        self.rect = self.image.get_rect(topleft=(x, y))
        self.client = None

class Penny(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = PENNY_IMG
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = 10  # Increased speed
        self.target_pos = None
        self.memory = []  # Orders in Penny's memory
        self.order_circle = None

    def move(self):
        if self.target_pos:
            target_x, target_y = self.target_pos
            if self.rect.x < target_x:
                self.rect.x += self.speed
            elif self.rect.x > target_x:
                self.rect.x -= self.speed
            if self.rect.y < target_y:
                self.rect.y += self.speed
            elif self.rect.y > target_y:
                self.rect.y -= self.speed
            if abs(self.rect.x - target_x) < self.speed and abs(self.rect.y - target_y) < self.speed:
                self.target_pos = None

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)
        if self.order_circle:
            order_text = FONT.render(str(self.order_circle), True, BLACK)
            pygame.draw.circle(screen, PINK, (self.rect.centerx, self.rect.top - 20), 20)
            screen.blit(order_text, (self.rect.centerx - order_text.get_width() // 2, self.rect.top - 30))

# Functions
def draw_menu():
    SCREEN.fill(WHITE)
    title = FONT.render("Quati Iguaçu", True, BLACK)
    SCREEN.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 4))
    start_button.draw(SCREEN)
    quit_button.draw(SCREEN)
    pygame.display.update()

def draw_game():
    SCREEN.blit(BACKGROUND_IMG, (0, 0))
    all_sprites.draw(SCREEN)
    SCREEN.blit(RESTING_POINT_IMG, (resting_point.rect.x, resting_point.rect.y))
    for client in clients:
        client.draw(SCREEN)
    quit_button.draw(SCREEN)
    penny.draw(SCREEN)
    pygame.display.update()

def game_loop():
    clock = pygame.time.Clock()
    running = True

    selected_client = None
    preparing_order = None
    preparing_start_time = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos

                if quit_button.is_clicked(pos):
                    running = False

                if selected_client:
                    for i, table in enumerate(tables):
                        if table.rect.collidepoint(pos) and not table.client:
                            table.client = selected_client
                            selected_client.state = 'moving'
                            chair_positions = [(205, 452), (963, 606), (1110, 444), (905, 785), (606, 935)]
                            selected_client.target_pos = chair_positions[i]
                            selected_client.table = table
                            print(f"Client seated at table at position: {chair_positions[i]}")
                            selected_client = None
                            break
                    else:
                        if resting_point.rect.collidepoint(pos):
                            penny.target_pos = resting_point.rect.topleft
                            print("Quati moving to resting point.")
                        selected_client.state = 'waiting'
                        selected_client = None
                else:
                    for client in clients:
                        if client.rect.collidepoint(pos) and client.state == 'waiting':
                            client.state = 'selected'
                            selected_client = client
                            print("Client selected.")
                            break
                    if not selected_client:
                        for table in tables:
                            if table.rect.collidepoint(pos):
                                penny.target_pos = table.rect.topleft
                                print("Quati moving to table.")
                                break
                        else:
                            if resting_point.rect.collidepoint(pos):
                                penny.target_pos = resting_point.rect.topleft
                                print("Quati moving to resting point.")

        penny.move()

        for client in clients:
            client.update()

        for table in tables:
            if table.client and table.client.order_active:
                if penny.target_pos is None and penny.rect.colliderect(table.rect):
                    penny.memory.append((table.client, table.client.order))
                    table.client.order_active = False
                    table.client.state = 'waiting_for_food'
                    print(f"Quati picked up order {table.client.order} from client at {table.client.rect.topleft}")

        if penny.target_pos is None and penny.rect.colliderect(resting_point.rect):
            if penny.memory and not preparing_order:
                preparing_order = penny.memory.pop(0)
                preparing_start_time = pygame.time.get_ticks()

        if preparing_order:
            if pygame.time.get_ticks() - preparing_start_time >= 10000:  # 10 seconds
                penny.order_circle = preparing_order[1]
                preparing_order = None
                print(f"Order {penny.order_circle} is ready.")

        if penny.order_circle:
            for table in tables:
                if table.client and table.client.state == 'waiting_for_food' and penny.rect.colliderect(table.rect):
                    table.client.state = 'eating'
                    table.client.order_active = False
                    table.client.order = None
                    penny.order_circle = None
                    print(f"Quati delivered order to client at {table.client.rect.topleft}")

        draw_game()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

# Initialize objects
start_button = Button(WIDTH // 2 - 50, HEIGHT // 2, 100, 50, "Start", GREEN)
quit_button = Button(WIDTH - 110, 10, 100, 50, "Quit", WHITE)

penny = Penny(400, 400)
resting_point = Table(1500, 800, 150, 150)  # Resting point as a table
tables = pygame.sprite.Group()
clients = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()

table_positions = [
    (317, 400, 150, 150),   # Table 1
    (700, 500, 150, 150),   # Table 2
    (1222, 383, 150, 150),   # Table 3
    (330, 900, 150, 150),  # Table 4
    (1025, 700, 150, 150)   # Table 5
]

for pos in table_positions:
    table = Table(*pos)
    tables.add(table)
    all_sprites.add(table)

client_positions = [(45 + i * 100, 705) for i in range(4)]
for pos in client_positions:
    client = Client(pos[0], pos[1])
    clients.add(client)
    all_sprites.add(client)

all_sprites.add(penny)

menu_running = True
while menu_running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if start_button.is_clicked(event.pos):
                menu_running = False
            elif quit_button.is_clicked(event.pos):
                pygame.quit()
                sys.exit()

    draw_menu()

game_loop()

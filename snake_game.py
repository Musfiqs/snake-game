import pygame
import random
import sys
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
DARK_GREEN = (0, 128, 0)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class Snake:
    def __init__(self):
        self.body = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = Direction.RIGHT
        self.grow_pending = False
        
    def move(self):
        head_x, head_y = self.body[0]
        dx, dy = self.direction.value
        new_head = (head_x + dx, head_y + dy)
        
        self.body.insert(0, new_head)
        
        if not self.grow_pending:
            self.body.pop()
        else:
            self.grow_pending = False
    
    def grow(self):
        self.grow_pending = True
    
    def check_collision(self):
        head_x, head_y = self.body[0]
        
        # Check wall collision
        if head_x < 0 or head_x >= GRID_WIDTH or head_y < 0 or head_y >= GRID_HEIGHT:
            return True
        
        # Check self collision
        if self.body[0] in self.body[1:]:
            return True
        
        return False
    
    def change_direction(self, new_direction):
        # Prevent reversing into itself
        if new_direction.value[0] != -self.direction.value[0] or new_direction.value[1] != -self.direction.value[1]:
            self.direction = new_direction

class Food:
    def __init__(self, snake_body):
        self.position = self.generate_position(snake_body)
    
    def generate_position(self, snake_body):
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if (x, y) not in snake_body:
                return (x, y)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        
        self.reset_game()
    
    def reset_game(self):
        self.snake = Snake()
        self.food = Food(self.snake.body)
        self.score = 0
        self.game_over = False
        self.paused = False
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_q:
                        return False
                else:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.snake.change_direction(Direction.UP)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.snake.change_direction(Direction.DOWN)
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.snake.change_direction(Direction.LEFT)
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.snake.change_direction(Direction.RIGHT)
                    elif event.key == pygame.K_SPACE:
                        self.paused = not self.paused
        
        return True
    
    def update(self):
        if not self.game_over and not self.paused:
            self.snake.move()
            
            # Check food collision
            if self.snake.body[0] == self.food.position:
                self.snake.grow()
                self.score += 10
                self.food = Food(self.snake.body)
            
            # Check game over
            if self.snake.check_collision():
                self.game_over = True
    
    def draw(self):
        self.screen.fill(BLACK)
        
        if not self.game_over:
            # Draw snake
            for i, segment in enumerate(self.snake.body):
                x, y = segment
                color = DARK_GREEN if i == 0 else GREEN
                rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, WHITE, rect, 1)
            
            # Draw food
            food_x, food_y = self.food.position
            food_rect = pygame.Rect(food_x * GRID_SIZE, food_y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(self.screen, RED, food_rect)
            pygame.draw.rect(self.screen, WHITE, food_rect, 1)
            
            # Draw score
            score_text = self.font.render(f"Score: {self.score}", True, WHITE)
            self.screen.blit(score_text, (10, 10))
            
            # Draw pause indicator
            if self.paused:
                pause_text = self.big_font.render("PAUSED", True, YELLOW)
                text_rect = pause_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
                self.screen.blit(pause_text, text_rect)
                
                resume_text = self.font.render("Press SPACE to resume", True, WHITE)
                resume_rect = resume_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
                self.screen.blit(resume_text, resume_rect)
        
        else:
            # Game over screen
            game_over_text = self.big_font.render("GAME OVER", True, RED)
            text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
            self.screen.blit(game_over_text, text_rect)
            
            final_score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
            score_rect = final_score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.screen.blit(final_score_text, score_rect)
            
            restart_text = self.font.render("Press R to restart or Q to quit", True, WHITE)
            restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
            self.screen.blit(restart_text, restart_rect)
        
        # Draw controls
        if not self.game_over:
            controls_text = self.font.render("Controls: WASD/Arrow Keys, SPACE to pause", True, GRAY)
            self.screen.blit(controls_text, (10, WINDOW_HEIGHT - 30))
        
        pygame.display.flip()
    
    def run(self):
        running = True
        
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            
            # Control game speed
            self.clock.tick(10)  # 10 FPS for classic snake feel
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run() 
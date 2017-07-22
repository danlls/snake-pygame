import pygame
import random

# Constants
FRAMERATE = 20

# Color RGB values
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
DARK_GREEN = (0, 200, 0)
DARK_RED = (200, 0, 0)

# Size of each snake segments
SEGMENT_WIDTH = 20
SEGMENT_HEIGHT = 20
SEGMENT_MARGIN = 5

WALL_THICKNESS = 25

SOUND_DIR = 'sound/'


class Snake(pygame.sprite.Group):

    def __init__(self, start_x, start_y, length=3):
        super().__init__()
        self.start_x = start_x
        self.start_y = start_y
        self.length = length
        self.snake_segments = []
        self.segment_width = SEGMENT_WIDTH
        self.segment_height = SEGMENT_HEIGHT
        self.segment_margin = SEGMENT_MARGIN
        self.last_removed = None

        # Segment width and height are equal
        # Hence, size of segment in both dimension
        # are equal (includes margin)
        self.segment_size = self.segment_width + self.segment_margin

        # Initialize snakes with segments
        for i in range(self.length):
            x = self.start_x - (self.segment_size) * i
            y = self.start_y
            self.add_segment(x, y)

        # Set initial velocity
        self.x_vel = 1 * self.segment_size
        self.y_vel = 0

    def add_segment(self, x, y, index=None):
        if index is None:
            index = self.length
        segment = SnakeSegment(x, y, self.segment_width, self.segment_height)
        self.snake_segments.insert(index, segment)
        self.add(segment)
        self.length += 1

    def pop(self):
        last_segment = self.snake_segments.pop()
        self.last_removed = last_segment
        self.remove(last_segment)
        self.length -= 1

    def head(self):
        return self.snake_segments[0]

    def tail(self):
        return self.snake_segments[1:]

    def on_horizontal(self):
        return self.y_vel == 0

    def on_vertical(self):
        return self.x_vel == 0

    def go_left(self):
        self.x_vel = -1 * (self.segment_size)
        self.y_vel = 0

    def go_right(self):
        self.x_vel = 1 * (self.segment_size)
        self.y_vel = 0

    def go_up(self):
        self.x_vel = 0
        self.y_vel = -1 * (self.segment_size)

    def go_down(self):
        self.x_vel = 0
        self.y_vel = 1 * (self.segment_size)

    def move(self):
        # Simulate movement by removing last segment, and adding new segment
        # infront of head based on current velocity
        self.pop()

        # New segment 
        x = self.head().x + self.x_vel
        y = self.head().y + self.y_vel
        self.add_segment(x, y, 0)

    def collides(self, sprite1):
        # Only head will be colliding with other sprite
        return self.head().check_collision(sprite1)

    def collides_any(self, group):
        for sprite in group:
            if self.collides(sprite):
                return True
        return False

    def grow(self):
        self.add_segment(self.last_removed.rect.x, self.last_removed.rect.y)


class SnakeSegment(pygame.sprite.Sprite):

    def __init__(self, x, y, width, height):
        super().__init__()

        self.x = x
        self.y = y

        self.image = pygame.Surface([width, height])
        self.image.fill(WHITE)

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def check_collision(self, sprite1):
        return pygame.sprite.collide_rect(self, sprite1)


class Wall(pygame.sprite.Sprite):

    def __init__(self, color, startpoint, endpoint, thickness):
        super().__init__()
        width = abs(endpoint[0]-startpoint[0])
        height = abs(endpoint[1]-startpoint[1])
        if width == 0:
            width = thickness
        if height == 0:
            height = thickness

        self.image = pygame.Surface([width, height])
        self.image.fill(color)

        self.rect = self.image.get_rect()
        self.rect.x = startpoint[0]
        self.rect.y = startpoint[1]


class Food(pygame.sprite.Sprite):

    def __init__(self, x_bound, y_bound):
        super().__init__()

        # Uses same size as snake segment
        self.image = pygame.Surface([SEGMENT_WIDTH, SEGMENT_HEIGHT])
        self.image.fill(GREEN)

        self.rect = self.image.get_rect()
        self.x_bound = x_bound
        self.y_bound = y_bound

    def spawn(self):
        # Scale the bounds to segment size
        segmentx_size = SEGMENT_WIDTH + SEGMENT_MARGIN
        segmenty_size = SEGMENT_HEIGHT + SEGMENT_MARGIN
        randx = random.randint(self.x_bound[0] // segmentx_size, self.x_bound[1] // segmentx_size - 1)
        randy = random.randint(self.y_bound[0] // segmenty_size, self.y_bound[1] // segmenty_size - 1)
        self.rect.x = (randx - 1) * segmentx_size + SEGMENT_MARGIN + WALL_THICKNESS
        self.rect.y = (randy - 1) * segmenty_size + SEGMENT_MARGIN + WALL_THICKNESS

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class App:

    def __init__(self, width=800, height=600):  
        pygame.mixer.init()
        pygame.init()
        pygame.font.init()
        self.screen_width = width
        self.screen_height = height
        self.screen = pygame.display.set_mode([self.screen_width, self.screen_height])
        pygame.display.set_caption('Snake')
        self.font = pygame.font.Font(None, 100)
        self.eat_sound = pygame.mixer.Sound(SOUND_DIR + '8biteat.wav')

        self.clock = pygame.time.Clock()
        
        
    def game_init(self):
        self.score = 0
        self.running = True

        # Scoreboard
        self.score_board = pygame.Surface((self.screen_width, 100))
        self.score_text = self.font.render("Score: " + str(self.score), True, RED)
        self.score_text_pos = self.score_text.get_rect()
        self.score_text_pos.centerx = self.score_board.get_rect().centerx
        self.score_text_pos.centery = self.score_board.get_rect().centery

        # Spaces belongs to game
        self.game_bound = {
            'min_x': 0,
            'max_x': self.screen_width,
            'min_y': 100,
            'max_y': self.screen_height,
        }

        # Build walls
        wall_color = BLUE
        wall_list = [
            Wall(wall_color, (self.game_bound['min_x'],self.game_bound['min_y']),
                            (self.game_bound['max_x'], self.game_bound['min_y']), WALL_THICKNESS),
            Wall(wall_color, (self.game_bound['max_x']-WALL_THICKNESS, self.game_bound['min_y']),
                            (self.game_bound['max_x']-WALL_THICKNESS, self.game_bound['max_y']), WALL_THICKNESS),
            Wall(wall_color, (self.game_bound['min_x'], self.game_bound['max_y']-WALL_THICKNESS),
                            (self.game_bound['max_x']-WALL_THICKNESS, self.game_bound['max_y']-WALL_THICKNESS), WALL_THICKNESS),
            Wall(wall_color, (self.game_bound['min_x'],self.game_bound['min_y']),
                            (self.game_bound['min_x'],self.game_bound['max_y']), WALL_THICKNESS)
        ]
        self.walls = pygame.sprite.Group()
        self.walls.add(wall_list)

        # Build food
        self.food = Food((self.game_bound['min_x'] + WALL_THICKNESS, self.game_bound['max_x']-WALL_THICKNESS),
                        (self.game_bound['min_y'] + WALL_THICKNESS, self.game_bound['max_y']-WALL_THICKNESS))
        self.food.spawn()

        # Puts snake starting point at top left of screen
        self.snake = Snake(self.game_bound['min_x']+WALL_THICKNESS+SEGMENT_MARGIN, self.game_bound['min_y']+WALL_THICKNESS+SEGMENT_MARGIN)
    

    def run(self):
        self.game_init()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                if event.type == pygame.KEYDOWN:
                    # Only allow left or right movement when snake is moving 
                    # in vertical direction
                    if self.snake.on_vertical():
                        if event.key == pygame.K_LEFT:
                            self.snake.go_left()
                        elif event.key == pygame.K_RIGHT:
                            self.snake.go_right()
                    # Only allow up or down movement when snake is moving 
                    # in horizontal direction
                    elif self.snake.on_horizontal():
                        if event.key == pygame.K_UP:
                            self.snake.go_up()
                        elif event.key == pygame.K_DOWN:
                            self.snake.go_down()

            # Fill background to delete previous drawn sprites
            self.screen.fill(BLACK)
            self.score_board.fill(BLACK)

            # Get score
            self.score_text = self.font.render("Score: " + str(self.score), True, RED)
            
            # Update
            self.snake.move() 
            self.walls.draw(self.screen)
            self.food.draw(self.screen)
            self.snake.draw(self.screen)
            self.score_board.blit(self.score_text, self.score_text_pos)
            
            # Collision detection
            if self.snake.collides_any(self.walls) or self.snake.collides_any(self.snake.tail()):
                self.running = False
                self.game_end()
            if self.snake.collides(self.food):
                self.eat_sound.play()
                self.score += 1
                self.snake.grow()
                self.food.spawn()

            self.screen.blit(self.score_board, (0,0))
            pygame.display.update()
            self.clock.tick(FRAMERATE)

    def game_end(self):
        end = True
        while end:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()

            self.screen.fill(WHITE)

            # Draw endgame text
            self.endgame_text = self.font.render("Game Over! Score is {}".format(self.score), True, BLACK)
            self.endgame_text_pos = self.endgame_text.get_rect()
            self.endgame_text_pos.center = ((self.screen_width/2),(self.screen_height/4))
            self.screen.blit(self.endgame_text, self.endgame_text_pos)

            # Draw buttons
            button_padx = 50
            button_pady = 25
            try_again_text = self.font.render("Try Again", True, BLACK)
            try_again_pos = try_again_text.get_rect()
            try_again_pos.center = ((self.endgame_text_pos.centerx), (self.endgame_text_pos.centery+200))

            quit_text = self.font.render("Quit", True, BLACK)
            quit_pos = quit_text.get_rect()
            quit_pos.center = ((self.endgame_text_pos.centerx), (self.endgame_text_pos.centery+350))

            try_again_button_rect = try_again_pos.inflate(button_padx, button_pady)
            quit_button_rect = quit_pos.inflate(button_padx, button_pady)

            mouse_pos = pygame.mouse.get_pos()
            mouse_click = pygame.mouse.get_pressed()

            # Draw buttons
            button_color = DARK_GREEN
            if try_again_button_rect.collidepoint(mouse_pos):
                button_color = GREEN
                if mouse_click[0]: self.run()
            pygame.draw.rect(self.screen, button_color, try_again_button_rect)

            button_color = DARK_RED
            if quit_button_rect.collidepoint(mouse_pos):
                button_color = RED
                if mouse_click[0]: self.quit()
            pygame.draw.rect(self.screen, button_color, quit_button_rect)

            # Draw text
            self.screen.blit(try_again_text, try_again_pos)
            self.screen.blit(quit_text, quit_pos)

            pygame.display.update()
            self.clock.tick(FRAMERATE)

    def quit(self):
        pygame.quit()
        quit()


if __name__ == "__main__":
    snake_app = App()
    snake_app.run()
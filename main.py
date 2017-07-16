import pygame
import random

# Constants
FRAMERATE = 20

# Color RGB values
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Size of each snake segments
SEGMENT_WIDTH = 20
SEGMENT_HEIGHT = 20
SEGMENT_MARGIN = 5

WALL_THICKNESS = 25


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
        pygame.init()
        self.screen_width = width
        self.screen_height = height
        self.screen = pygame.display.set_mode([self.screen_width, self.screen_height])
        pygame.display.set_caption('Snake')

        self.clock = pygame.time.Clock()
        self.running = True

        # Build walls
        wall_color = BLUE
        wall_list = [
            Wall(wall_color, (0,0), (self.screen_width, 0), WALL_THICKNESS),
            Wall(wall_color, (self.screen_width-WALL_THICKNESS, 0), (self.screen_width-WALL_THICKNESS, self.screen_height), WALL_THICKNESS),
            Wall(wall_color, (0, self.screen_height-WALL_THICKNESS), (self.screen_width-WALL_THICKNESS, self.screen_height-WALL_THICKNESS), WALL_THICKNESS),
            Wall(wall_color, (0,0), (0,self.screen_height), WALL_THICKNESS)
        ]
        self.walls = pygame.sprite.Group()
        self.walls.add(wall_list)

        # Build food
        self.food = Food((WALL_THICKNESS, self.screen_width-WALL_THICKNESS), (WALL_THICKNESS, self.screen_height-WALL_THICKNESS))
        self.food.spawn()

        # Puts snake starting point at top left of screen
        self.snake = Snake(WALL_THICKNESS+SEGMENT_MARGIN, WALL_THICKNESS+SEGMENT_MARGIN)

        self.score = 0

    def run(self):
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

            # Update
            self.snake.move() 
            self.walls.draw(self.screen)
            self.food.draw(self.screen)
            self.snake.draw(self.screen)
            
            if self.snake.collides_any(self.walls) or self.snake.collides_any(self.snake.tail()):
                self.quit()

            if self.snake.collides(self.food):
                self.score += 1
                self.snake.grow()
                self.food.spawn()

            pygame.display.update()
            self.clock.tick(FRAMERATE)

    def quit(self):
        self.running = False
        pygame.quit()
        quit()


if __name__ == "__main__":
    snake_app = App()
    snake_app.run()
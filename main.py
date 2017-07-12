import pygame


class App:

    def __init__(self, width=600, height=400):  
        pygame.init()
        self.screen_width = width
        self.screen_height = height
        self.screen = pygame.display.set_mode([self.screen_width, self.screen_height])
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()
        self.running = True

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()

            pygame.display.update()
            self.clock.tick(60)

    def quit(self):
        self.running = False
        pygame.quit()
        quit()


if __name__ == "__main__":
    snake_app = App()
    snake_app.run()
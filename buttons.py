import pygame

class Button:

    def __init__(self, screen, font, text, text_color, color, centerx, centery):
        self.font = font
        self.text_color = text_color
        self.text = text
        self.button_text = self.font.render(self.text, True, self.text_color)
        self.button_text_pos = self.button_text.get_rect()
        self.button_text_pos.center = (centerx, centery)
        self.screen = screen
        self.button_color = color
        self.color = color
        self.clicked = False

    def add_paddings(self, padx=0, pady=0):
        self.button_rect = self.button_text_pos.inflate(padx, pady)

    def draw(self):
        pygame.draw.rect(self.screen, self.button_color, self.button_rect)
        self.screen.blit(self.button_text, self.button_text_pos)
        self.clicked = False

    def mouse_handler(self, mouse_pos, mouse_state, hover=False, hover_color=None, on_click=None):
        self.clicked = False
        if self.button_rect.collidepoint(mouse_pos):
            if hover:
                self.button_color = hover_color
            if on_click and any(mouse_state):
                self.clicked = True
                on_click()
        else:
            self.button_color = self.color


class ToggleButton(Button):

    def __init__(self, default=True, *args, **kwargs):
        self.status = default
        self.toggle_text = False
        super().__init__(*args, **kwargs)

    def set_toggle_text(self, true_text, false_text, state=True):
        self.toggle_text = state
        self.true_text = true_text
        self.false_text = false_text

    def draw(self):
        if self.toggle_text:
            if self.status:
                self.button_text = self.font.render(self.true_text, True, self.text_color)
            else:
                self.button_text = self.font.render(self.false_text, True, self.text_color)
        super().draw()

    def mouse_handler(self, *args, **kwargs):
        super().mouse_handler(*args, **kwargs)
        if self.clicked:
            self.status = not self.status


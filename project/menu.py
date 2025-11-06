import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1480
WINDOW_HEIGHT = 812
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (34, 197, 94)
DARK_GREEN = (22, 163, 74)
CYAN = (6, 182, 212)
YELLOW = (234, 179, 8)
PURPLE = (168, 85, 247)
ORANGE = (249, 115, 22)
BLUE = (59, 130, 246)
EMERALD = (16, 185, 129)
RED = (239, 68, 68)
GRAY = (55, 65, 81)
LIGHT_GRAY = (75, 85, 99)
DARK_BLUE = (30, 41, 59)
DARKER_BLUE = (15, 23, 42)

# Game colors for the logo
GAME_COLORS = [CYAN, YELLOW, PURPLE, ORANGE, BLUE, EMERALD, RED]

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        
    def draw(self, screen, font):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class RadioButton:
    def __init__(self, x, y, width, height, label, description, selected=False, label_color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.label = label
        self.description = description
        self.selected = selected
        self.label_color = label_color
        self.is_hovered = False
        
    def draw(self, screen, font, desc_font):
        # Background
        bg_color = LIGHT_GRAY if self.is_hovered else GRAY
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=8)
        
        # Radio circle
        circle_x = self.rect.x + 20
        circle_y = self.rect.centery
        pygame.draw.circle(screen, WHITE, (circle_x, circle_y), 8, 2)
        if self.selected:
            pygame.draw.circle(screen, CYAN, (circle_x, circle_y), 5)
        
        # Label
        label_surface = font.render(self.label, True, self.label_color)
        screen.blit(label_surface, (circle_x + 25, self.rect.y + 12))
        
        # Description
        desc_surface = desc_font.render(self.description, True, (156, 163, 175))
        screen.blit(desc_surface, (circle_x + 25, self.rect.y + 36))
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class TetriMindMenu:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("TetriMind")
        self.clock = pygame.time.Clock()
        
        # Fonts
        self.title_font = pygame.font.Font(None, 96)
        self.button_font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.label_font = pygame.font.Font(None, 28)
        self.desc_font = pygame.font.Font(None, 20)
        
        # Game state
        self.show_setup = False
        self.game_mode = "player"  # player or ai
        self.ai_difficulty = "medium"  # low, medium, hard, expert
        
        # Main menu button
        self.start_button = Button(
            WINDOW_WIDTH // 2 - 175,
            WINDOW_HEIGHT // 2 + 50,
            350,
            50,
            "START GAME",
            GREEN,
            DARK_GREEN
        )
        
        self.setup_buttons()
        
    def setup_buttons(self):
        pass
        
    def create_mode_buttons(self, dialog_x, dialog_y):
        return [
            RadioButton(
                dialog_x + 20,
                dialog_y + 125,
                360,
                60,
                "Player Only",
                "Classic single player mode",
                selected=(self.game_mode == "player"),
                label_color=CYAN
            ),
            RadioButton(
                dialog_x + 20,
                dialog_y + 195,
                360,
                60,
                "Player vs AI",
                "Compete against AI",
                selected=(self.game_mode == "ai"),
                label_color=PURPLE
            )
        ]
    
    def create_difficulty_buttons(self, dialog_x, dialog_y):
        difficulties = ["low", "medium", "hard", "expert"]
        colors = [CYAN, YELLOW, ORANGE, RED]
        labels = ["Low", "Medium", "Hard", "Expert"]
        descriptions = ["Beginner AI", "Intermediate AI", "Advanced AI", "Master AI"]
        
        buttons = []
        for i in range(4):
            buttons.append(RadioButton(
                dialog_x + 20,
                dialog_y + 310 + (i * 60),
                360,
                50,
                labels[i],
                descriptions[i],
                selected=(self.ai_difficulty == difficulties[i]),
                label_color=colors[i]
            ))
        return buttons
        
    def draw_main_menu(self):
        self.screen.fill(BLACK)
        
        # Title 
        title_text = self.title_font.render("TetriMind", True, WHITE)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100))
        self.screen.blit(title_text, title_rect)
        
        # Colorful underline
        underline_width = 150
        underline_x = WINDOW_WIDTH // 2 - underline_width // 2
        underline_y = WINDOW_HEIGHT // 2 - 50
        
        # Gradient underline effect
        pygame.draw.rect(self.screen, CYAN, (underline_x, underline_y, 50, 4))
        pygame.draw.rect(self.screen, PURPLE, (underline_x + 50, underline_y, 50, 4))
        pygame.draw.rect(self.screen, RED, (underline_x + 100, underline_y, 50, 4))
        
        # Color blocks
        block_size = 20
        blocks_y = WINDOW_HEIGHT // 2 - 20
        start_x = WINDOW_WIDTH // 2 - (len(GAME_COLORS) * block_size) // 2
        
        for i, color in enumerate(GAME_COLORS):
            pygame.draw.rect(self.screen, color, 
                           (start_x + i * block_size, blocks_y, block_size - 2, block_size - 2))
        
        # Start button
        self.start_button.draw(self.screen, self.button_font)
        
        # Instructions
        instructions = [
            "Use z x or arrow keys to move & rotate",
            "Press SPACE for hard drop"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, (100, 100, 100))
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 140 + i * 30))
            self.screen.blit(text, text_rect)
        
    def draw_setup_dialog(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Dialog box - adjust height based on game mode
        dialog_width = 400
        dialog_height = 360 if self.game_mode == "player" else 620
        dialog_x = (WINDOW_WIDTH - dialog_width) // 2
        dialog_y = (WINDOW_HEIGHT - dialog_height) // 2
        
        pygame.draw.rect(self.screen, DARK_BLUE, 
                        (dialog_x, dialog_y, dialog_width, dialog_height), 
                        border_radius=12)
        
        # Close button
        close_x = dialog_x + dialog_width - 35
        close_y = dialog_y + 15
        pygame.draw.line(self.screen, WHITE, (close_x, close_y), (close_x + 15, close_y + 15), 2)
        pygame.draw.line(self.screen, WHITE, (close_x + 15, close_y), (close_x, close_y + 15), 2)
        
        # Title
        title = self.button_font.render("GAME SETUP", True, WHITE)
        self.screen.blit(title, (dialog_x + 20, dialog_y + 20))
        
        subtitle_text = "Choose your game mode and difficulty" if self.game_mode == "ai" else "Choose your game mode"
        subtitle = self.small_font.render(subtitle_text, True, (156, 163, 175))
        self.screen.blit(subtitle, (dialog_x + 20, dialog_y + 55))
        
        # Section: Game Mode
        mode_label = self.label_font.render("Game Mode", True, WHITE)
        self.screen.blit(mode_label, (dialog_x + 20, dialog_y + 90))
        
        # Create and draw mode buttons
        self.mode_buttons = self.create_mode_buttons(dialog_x, dialog_y)
        for button in self.mode_buttons:
            button.draw(self.screen, self.label_font, self.desc_font)
        
        # AI Difficulty 
        if self.game_mode == "ai":
            diff_label = self.label_font.render("AI Difficulty", True, WHITE)
            self.screen.blit(diff_label, (dialog_x + 20, dialog_y + 275))
            
            self.difficulty_buttons = self.create_difficulty_buttons(dialog_x, dialog_y)
            for button in self.difficulty_buttons:
                button.draw(self.screen, self.label_font, self.desc_font)
        
        # Action buttons 
        button_y = dialog_y + dialog_height - 60
        reset_button = Button(
            dialog_x + 20,
            button_y,
            160,
            40,
            "Reset to Defaults",
            GRAY,
            LIGHT_GRAY
        )
        play_button = Button(
            dialog_x + dialog_width - 180,
            button_y,
            160,
            40,
            "Start Game",
            GREEN,
            DARK_GREEN
        )
        
        reset_button.check_hover(pygame.mouse.get_pos())
        play_button.check_hover(pygame.mouse.get_pos())
        reset_button.draw(self.screen, self.small_font)
        play_button.draw(self.screen, self.small_font)
        
        # Store buttons for click detection
        self.reset_button = reset_button
        self.play_button = play_button
        
    def handle_setup_click(self, pos):
        dialog_width = 400
        dialog_height = 360 if self.game_mode == "player" else 620
        dialog_x = (WINDOW_WIDTH - dialog_width) // 2
        dialog_y = (WINDOW_HEIGHT - dialog_height) // 2
        close_rect = pygame.Rect(dialog_x + dialog_width - 35, dialog_y + 15, 15, 15)
        
        if close_rect.collidepoint(pos):
            self.show_setup = False
            return
        
        # Check game mode buttons
        for i, button in enumerate(self.mode_buttons):
            if button.is_clicked(pos):
                self.game_mode = "player" if i == 0 else "ai"
                return
        
        # Check difficulty buttons 
        if self.game_mode == "ai" and hasattr(self, 'difficulty_buttons'):
            for i, button in enumerate(self.difficulty_buttons):
                if button.is_clicked(pos):
                    difficulties = ["low", "medium", "hard", "expert"]
                    self.ai_difficulty = difficulties[i]
                    return
        
        # Check action buttons
        if self.reset_button.is_clicked(pos):
            self.game_mode = "player"
            self.ai_difficulty = "medium"
            return
        
        if self.play_button.is_clicked(pos):
            print(f"Starting game - Mode: {self.game_mode}, Difficulty: {self.ai_difficulty}")
            self.show_setup = False
            return
        
    def run(self):
        running = True
        
        while running:
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                if event.type == pygame.MOUSEMOTION:
                    if not self.show_setup:
                        self.start_button.check_hover(mouse_pos)
                    else:
                        if hasattr(self, 'mode_buttons'):
                            for button in self.mode_buttons:
                                button.check_hover(mouse_pos)
                        if self.game_mode == "ai" and hasattr(self, 'difficulty_buttons'):
                            for button in self.difficulty_buttons:
                                button.check_hover(mouse_pos)
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if not self.show_setup:
                        if self.start_button.is_clicked(mouse_pos):
                            self.show_setup = True
                    else:
                        self.handle_setup_click(mouse_pos)
            
            # Draw
            self.draw_main_menu()
            
            if self.show_setup:
                self.draw_setup_dialog()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    menu = TetriMindMenu()
    menu.run()
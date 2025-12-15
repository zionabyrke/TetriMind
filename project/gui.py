from settings import *
import time
import random

pygame.init()

font_title = pygame.font.SysFont("consolas", APPNAME_SIZE)
font_header = pygame.font.SysFont("consolas", 18)
font_style_ai = pygame.font.SysFont("consolas", 14)
font_style = pygame.font.SysFont("consolas", 12)

# surfaces 
playfield_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
preview_surface = pygame.Surface((RIGHTBAR_WIDTH, GAME_HEIGHT*PREVIEW_HEIGHT_FRACTION - PADDING))
score_surface = pygame.Surface((RIGHTBAR_WIDTH, GAME_HEIGHT*SCORE_HEIGHT_FRACTION))
controls_surface = pygame.Surface((LEFTBAR_WIDTH, CONTROLS_HEIGHT))
scoring_surface = pygame.Surface((LEFTBAR_WIDTH, SCORING_HEIGHT))
ghost_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)

playfield_surface_ai = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
preview_surface_ai = pygame.Surface((RIGHTBAR_WIDTH, GAME_HEIGHT * PREVIEW_HEIGHT_FRACTION - PADDING))
score_surface_ai = pygame.Surface((RIGHTBAR_WIDTH, GAME_HEIGHT * SCORE_HEIGHT_FRACTION))
sidebar_surface = pygame.Surface((RIGHTBAR_WIDTH, GAME_HEIGHT))

#buttons
pause_rect = pygame.Rect((WINDOW_WIDTH_vs-GAME_WIDTH)//2, GAME_HEIGHT+APPNAME_SIZE+PADDING*2,
                GAME_WIDTH//3, 30 ) #30 height
reset_rect = pygame.Rect(pause_rect.x + GAME_WIDTH//3, GAME_HEIGHT+APPNAME_SIZE+PADDING*2,
                GAME_WIDTH//3, 30 ) #30 height
menu_rect = pygame.Rect(pause_rect.x + (GAME_WIDTH//3)*2, GAME_HEIGHT+APPNAME_SIZE+PADDING*2,
                GAME_WIDTH//3, 30 ) #30 height

# vs mode layouting
H_SPACING = 40 #space between the fields
total_content_w = 2 * GAME_WIDTH + H_SPACING + 2 * RIGHTBAR_WIDTH
left_margin = (WINDOW_WIDTH_vs - total_content_w) // 2
player_rightbar_x = left_margin + GAME_WIDTH + PADDING
#x position
ai_x = player_rightbar_x + RIGHTBAR_WIDTH + H_SPACING
ai_rightbar_x = ai_x + GAME_WIDTH + PADDING
# top vertical alignment
top_y = PADDING + APPNAME_SIZE + 7


class RendererSolo:
    def __init__(self, screen):
        self.screen = screen
        self.screen.fill(GRAY)
        self.clock = pygame.time.Clock()
        self.color_matrix = [[BLACK for _ in range(COLUMNS)] for _ in range(ROWS)]
        self.running = True
        self.paused = False
        self.is_reset = False
        self.pause_label = "Pause"
        self.is_menu = False

        self.held_keys = []
        self.hold_delay = 0

    def run(self, game):
        while self.running:
            dt = self.clock.tick(FRAMEPERSEC)
            self.get_input(game)

            if self.is_menu:
                return True

            ### GAME LOGIC SECTION
            if self.is_reset or game.game_over:
                game.reset(random.randint(0, 2**63-1))
                self.__init__(self.screen)
            if not self.paused: #update only if not paused
                game.update(dt, self.color_matrix)
                game.update_clock(dt)
                self.pause_label = "Pause"
            else: 
                self.pause_label = "Resume"

            self.display_section(game)

            pygame.display.update()

        return False # user wants quit

    def get_input(self, game):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            # pause , reset button
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if pause_rect.collidepoint(event.pos):
                    self.paused = not self.paused
                if reset_rect.collidepoint(event.pos):
                    self.is_reset = True
                if menu_rect.collidepoint(event.pos):
                    self.is_menu = True
                    return
            elif self.paused == True:
                continue # no moving actions till resumed
            elif event.type == pygame.KEYDOWN:
                # Left, right, and down keys can be held down, rotation and hard drop can't be held
                if event.key == pygame.K_LEFT:
                    self.held_keys.append(MOVE_LEFT)
                elif event.key == pygame.K_RIGHT:
                    self.held_keys.append(MOVE_RIGHT)
                elif event.key == pygame.K_DOWN:
                    self.held_keys.append(MOVE_DOWN)
                # Move variables are mapped to their corresponding pygame.key in settings.py
                # So this will move tetromino based on pressed key
                game.move_tetromino(event.key, self.color_matrix)
            elif event.type == pygame.KEYUP and self.held_keys:
                self.hold_delay = 0
                if event.key == pygame.K_LEFT:
                    self.held_keys.remove(MOVE_LEFT)
                elif event.key == pygame.K_RIGHT:
                    self.held_keys.remove(MOVE_RIGHT)
                elif event.key == pygame.K_DOWN:
                    self.held_keys.remove(MOVE_DOWN)

        # Move based on held key
        if self.held_keys:
            self.hold_delay += 1
            # Delay for 10 frames before player can fully hold, so it doesn't go too fast
            if self.hold_delay > 10:
                game.move_tetromino(self.held_keys[-1], self.color_matrix)

    def display_section(self, game):
        ### DISPLAY SECTION
        self.screen.fill(GRAY)
        playfield_surface.fill(BLACK)
        preview_surface.fill(BLACK)
        score_surface.fill(BLACK)
        controls_surface.fill(BLACK)
        scoring_surface.fill(BLACK)

        # Title text
        title_text = font_title.render("TETRIMIND", True, LINE_COLOR)
        self.screen.blit(title_text, ((WINDOW_WIDTH_vs-GAME_WIDTH)//2 + (GAME_WIDTH-title_text.get_width())/2, PADDING*2))

        self.playfield(game, playfield_surface, preview_surface, self.color_matrix)
        self.screen.blit(playfield_surface, ((WINDOW_WIDTH_vs-GAME_WIDTH)//2, 2*PADDING+APPNAME_SIZE))
        self.panels(game)
        self.buttons()

    def playfield(self, game, surface, prev, color_matrix):
        surface.fill(BLACK) 

        # playfield blocks
        for y, row in enumerate(color_matrix):
            for x, color in enumerate(row):
                if color != BLACK:
                    pygame.draw.rect(surface, color,
                                        (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        # should be here so that
        # gridlines overshows the blocks
        # current tetromino shape
        if game.current_piece:
            shape = game.current_piece.get_shape_array()
            # tetromino piece
            for dx, dy in shape:
                pygame.draw.rect(surface, game.current_piece.color,
                                ((game.current_piece.coord[0] + dx) * CELL_SIZE,
                                (game.current_piece.coord[1] + dy) * CELL_SIZE,
                                CELL_SIZE, CELL_SIZE))

            # ghost piece
            ghost_coords = game.ghost_piece()
            ghost_color = pygame.Color(game.current_piece.color)
            ghost_color.a = 64 #25% x 255 = 64 adjust
            ghost_surface.fill(ghost_color)
            for gx, gy in ghost_coords:
                surface.blit(ghost_surface, (gx*CELL_SIZE, gy*CELL_SIZE))

        # next tetromino piece
        if game.next_piece:
            shape = game.next_piece.get_shape_array()
            for x, y in shape:
                pygame.draw.rect(prev, game.next_piece.color,
                                ((x*CELL_SIZE)+(45), PADDING+(y*CELL_SIZE)+30,
                                CELL_SIZE, CELL_SIZE))
        # draw gridlines
        for col in range(1, COLUMNS):
            x = col * CELL_SIZE
            pygame.draw.line(surface, GRAY, (x, 0), (x, GAME_HEIGHT), 1)
        for row in range(1, ROWS):
            y = row * CELL_SIZE
            pygame.draw.line(surface, GRAY, (0, y), (GAME_WIDTH, y), 1)
    
    def panels(self, game):
        # texts
        score_text = font_header.render("     SCORE:", True, LINE_COLOR)
        score_amount = font_header.render(f"       {game.player_score}", True, LINE_COLOR)
        level_text = font_header.render(f"     LEVEL: {game.game_level}", True, LINE_COLOR)
        time_text = font_header.render(f"     TIME: %02d:%02d" % ((game.elapsed_time//1000)//60, (game.elapsed_time//1000)%60), True, LINE_COLOR)
        preview_text = font_header.render("     NEXT", True, LINE_COLOR)
        # draw control and surface text line by line
        for x, text in enumerate(CONTROLS_TEXT):
            controls_text = font_style.render(text, True, LINE_COLOR)
            controls_surface.blit(controls_text, (PADDING, PADDING+(x*20)))

        for x, text in enumerate(SCORING_TEXT):
            scoring_text = font_style.render(text, True, LINE_COLOR)
            scoring_surface.blit(scoring_text, (PADDING, PADDING+(x*20)))

        score_surface.blit(score_text, (PADDING, PADDING))
        score_surface.blit(score_amount, (PADDING, PADDING+30))
        score_surface.blit(level_text, (PADDING, PADDING + 80))
        score_surface.blit(time_text, (PADDING, PADDING + 130))
        preview_surface.blit(preview_text, (PADDING, PADDING))

        score_rect = score_surface.get_rect(topleft=((WINDOW_WIDTH_vs-GAME_WIDTH)//2 - PADDING - RIGHTBAR_WIDTH, 2*PADDING+APPNAME_SIZE))
        preview_rect = preview_surface.get_rect(
            bottomleft=((WINDOW_WIDTH_vs-GAME_WIDTH)//2 - PADDING - RIGHTBAR_WIDTH, score_rect.bottom + preview_surface.get_height() + PADDING))
        controls_rect = controls_surface.get_rect(topright=((WINDOW_WIDTH_vs+GAME_WIDTH)//2 + PADDING + LEFTBAR_WIDTH, 2*PADDING+APPNAME_SIZE))
        scoring_rect = scoring_surface.get_rect(bottomright=((WINDOW_WIDTH_vs+GAME_WIDTH)//2 + PADDING + LEFTBAR_WIDTH, +CONTROLS_HEIGHT+SCORING_HEIGHT+PADDING*3+APPNAME_SIZE))

        self.screen.blit(score_surface, score_rect)
        self.screen.blit(preview_surface, preview_rect)
        self.screen.blit(controls_surface, controls_rect)
        self.screen.blit(scoring_surface, scoring_rect)

    def buttons(self):
        # button box
        pygame.draw.rect(self.screen, BLACK, pause_rect) #fill
        pygame.draw.rect(self.screen, GRAY, pause_rect, 4) #4px border/gaps
        pause_text= font_header.render(self.pause_label, True, LINE_COLOR)
        self.screen.blit(pause_text, (pause_rect.x + (pause_rect.width-pause_text.get_width())// 2, 
                                pause_rect.y + (pause_rect.height-pause_text.get_height())// 2))

        pygame.draw.rect(self.screen, BLACK, reset_rect)#fill
        pygame.draw.rect(self.screen, GRAY, reset_rect, 4)#4px border/gaps
        reset_text= font_header.render("Reset", True, LINE_COLOR)
        self.screen.blit(reset_text, (reset_rect.x + (reset_rect.width-reset_text.get_width())// 2,
                                reset_rect.y + (reset_rect.height-reset_text.get_height())// 2))

        pygame.draw.rect(self.screen, BLACK, menu_rect)#fill
        pygame.draw.rect(self.screen, GRAY, menu_rect, 4)#4px border/gaps
        menu_text = font_header.render("Menu", True, LINE_COLOR)
        self.screen.blit(menu_text , (menu_rect.x + (menu_rect.width-menu_text.get_width())// 2,
                                menu_rect.y + (menu_rect.height-menu_text.get_height())// 2))

class RendererVs(RendererSolo):
    def __init__(self, screen):
        super().__init__(screen)
        self.screen = screen
        self.screen.fill(GRAY)
        self.color_matrix_ai = [[BLACK for _ in range(COLUMNS)] for _ in range(ROWS)]

    def run(self, game_p, game_ai, agent, garbo=False):
        while self.running:
            dt = self.clock.tick(FRAMEPERSEC)

            self.get_input(game_p)

            if self.is_menu:
                return True

            ### GAME LOGIC SECTION
            if self.is_reset or game_p.game_over or game_ai.game_over:
                new_seed = random.randint(0, 2**63-1)
                game_p.reset(new_seed)
                game_ai.reset(new_seed)
                agent.move_time=0
                agent.action_sequence=0
                agent.action=None
                self.__init__(self.screen)

            if not self.paused: #update only if not paused
                self.updates(game_p, game_ai, dt, garbo)
                self.pause_label = "Pause"

                # agent actions
                agent.moves(game_ai, agent, dt, self.color_matrix_ai)
            else: 
                self.pause_label = "Resume"

            self.display_section(game_p, game_ai)
            pygame.display.update()
        
        return False# user wants quit


    def updates(self, game_h, game_ai, dt, garbo):
        if garbo:
            game_h.garbage(game_ai)
            game_ai.garbage(game_h)

        game_h.update(dt, self.color_matrix)
        game_ai.update(dt, self.color_matrix_ai)

        game_h.update_clock(dt)
        game_ai.update_clock(dt)

        game_h.update_fallspeed()
        game_ai.update_fallspeed()


    def display_section(self, game_h, game_ai):
        ### DISPLAY SECTION
        preview_surface.fill(BLACK)
        score_surface.fill(BLACK)
        preview_surface_ai.fill(BLACK)
        score_surface_ai.fill(BLACK)

        # Title text
        title_text = font_title.render("TETRIMIND — PLAYER (LEFT)  vs  AI (RIGHT)", True, LINE_COLOR)
        self.screen.blit(title_text, ((WINDOW_WIDTH_vs - title_text.get_width()) // 2, PADDING))

        self.playfield(game_h, playfield_surface, preview_surface, self.color_matrix)
        self.playfield(game_ai, playfield_surface_ai, preview_surface_ai, self.color_matrix_ai)
        self.panels(game_h, game_ai)
        self.buttons()

    def panels(self, game_h, game_ai):
        preview_surface.blit(font_header.render("     NEXT", True, LINE_COLOR),(PADDING, PADDING))
        score_surface.blit(font_header.render("     SCORE:", True, LINE_COLOR),(PADDING, PADDING))
        score_surface.blit(font_header.render(f"       {game_h.player_score}", True, LINE_COLOR),(PADDING, PADDING + 30))
        score_surface.blit(font_header.render(f"     LEVEL: {game_h.game_level}", True, LINE_COLOR),(PADDING, PADDING + 80))
        score_surface.blit(font_header.render("     TIME: %02d:%02d" %((game_h.elapsed_time//1000)//60,(game_h.elapsed_time//1000)%60),True,LINE_COLOR),(PADDING, PADDING + 130))

        preview_surface_ai.blit(font_header.render("     NEXT", True, LINE_COLOR),(PADDING, PADDING))
        score_surface_ai.blit(font_header.render("     AI SCORE:", True, LINE_COLOR),(PADDING, PADDING))
        score_surface_ai.blit(font_header.render(f"       {game_ai.player_score}", True, LINE_COLOR),(PADDING, PADDING + 30))
        score_surface_ai.blit(font_header.render(f"     LEVEL: {game_ai.game_level}", True, LINE_COLOR),(PADDING, PADDING + 80))
        score_surface_ai.blit(font_header.render("     TIME: %02d:%02d" %((game_ai.elapsed_time//1000)//60,(game_ai.elapsed_time//1000)%60),True,LINE_COLOR),(PADDING, PADDING + 130))

        # Player (left side)
        self.screen.blit(playfield_surface, (left_margin, top_y))
        self.screen.blit(preview_surface,(player_rightbar_x, top_y))
        self.screen.blit(score_surface,(player_rightbar_x,top_y + preview_surface.get_height() + PADDING))

        # AI (right side)
        self.screen.blit(playfield_surface_ai, (ai_x, top_y))
        self.screen.blit(preview_surface_ai,(ai_rightbar_x, top_y))
        self.screen.blit(score_surface_ai,(ai_rightbar_x,top_y + preview_surface_ai.get_height() + PADDING))

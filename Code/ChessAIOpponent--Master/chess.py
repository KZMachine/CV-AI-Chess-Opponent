from math import inf
import pygame_menu
import queue
import sys
import threading
import time
import PhysicalBoard
from Board import *
from settings import *

# Initialize Pygame
pygame.init()

# Fonts
FONT = pygame.font.Font(pygame_menu.font.FONT_OPEN_SANS_BOLD, 18)
BIG_FONT = pygame.font.Font(pygame_menu.font.FONT_OPEN_SANS_BOLD, 26)

# Title and Icon
pygame.display.set_caption("ChessAI")
icon = pygame.image.load(os.path.join('img', 'icon.png'))
pygame.display.set_icon(icon)

class Game:

    def __init__(self):
        self.p1_name = "Player 1"
        self.p2_name = "Minimax"

        self.p1_color = WHITE
        self.p2_color = BLACK

        self.ai_move = queue.Queue()
        self.lock = threading.Lock()

        self.board = Board(self.p1_color)
        self.board.initialize_pieces()

        self.menu_screen()

    def reset(self):
        self.p2_name = "Minimax"
        self.p1_color = WHITE
        self.p2_color = BLACK
        self.board = Board(self.p1_color)
        self.board.initialize_pieces()
        self.ai_move = queue.Queue()

    def set_name(self, name):
        self.p1_name = name

    def set_color(self, color, value):
        self.board.player = value
        self.p1_color = value
        if value == WHITE:
            self.p2_color = BLACK
            self.board.bottomPlayerTurn = False
        else:
            self.p2_color = WHITE
            self.board.bottomPlayerTurn = True
        self.board = Board(value)
        self.board.initialize_pieces()

    def set_ai(self, tup, value):
        self.p2_name = tup[0]

    def menu_screen(self):
        theme = pygame_menu.themes.Theme(title_bar_style=pygame_menu.widgets.MENUBAR_STYLE_NONE,
                                         menubar_close_button=False,
                                         widget_font_color=SMALL_TEXT_COLOR,
                                         background_color=BG_COLOR,
                                         widget_font=pygame_menu.font.FONT_OPEN_SANS_BOLD,
                                         cursor_color=WHITE)

        menu = pygame_menu.Menu(height=SCREEN_HEIGHT, width=SCREEN_WIDTH, title="", theme=theme)
        menu.add_label("ChessAI", align=pygame_menu.locals.ALIGN_CENTER, font_name=pygame_menu.font.FONT_OPEN_SANS_BOLD,
                       font_color=LARGE_TEXT_COLOR, font_size=90, margin=(0, 50))
        menu.add_text_input('Name : ', default=self.p1_name, maxchar=10, onchange=self.set_name)
        menu.add_selector('Color : ', [('White', WHITE), ('Black', BLACK)], onchange=self.set_color)
        menu.add_selector('AI : ', [('Random', 1), ('Minimax', 2)], onchange=self.set_ai)
        menu.add_button('Play', self.game_screen)
        menu.add_button('Quit', pygame_menu.events.EXIT)
        menu.add_label("", align=pygame_menu.locals.ALIGN_CENTER, font_color=BLACK, font_size=70, margin=(0, 50))
        menu.center_content()

        # Keeps track of whether menu screen should keep running or stop
        running = True
        
        self.game_screen()
        
        # Menu screen loop
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            menu.mainloop(SCREEN)

            pygame.display.flip()

    def determine_move(self):
        # Determine move based on selected AI
        self.p2_name = "Minimax"
#         if self.p2_name == "Minimax":
        self.ai_move.put(AI.minimax(self.board.copy(), MINIMAX_DEPTH, inf, -inf, True, self.p2_color)[0])
#         else:
#             self.ai_move.put(AI.random_move(self.board))

        # Close thread after move has been found
        sys.exit()

    def game_screen(self):

        # Create a thread which will be used to determine AI's move concurrently with rest of game
        t = threading.Thread(target=self.determine_move)

        # Creates collision box for resign button
        resign_button = pygame.Rect(BOARD_X + BOARD_SIZE + 8, BOARD_Y + BOARD_SIZE + 8,
                                    int((TILE_SIZE * 4 + 8) / 2 - 4), 28)

        self.board.draw()
        # Game screen loop
        while True:
            if self.board.turn == self.p1_color:
                self.board.select()
                self.board.draw()

            # Draw background first (everything else goes on top of it)
            SCREEN.fill(BG_COLOR)

            # Check for endgame state
            self.board.checkmate_stalemate()
            self.board.insufficient_material()

            # GAME OVER: Checkmate, Stalemate, or Insufficient Material
            if self.board.gameover:
                print("GAME OVER: ", self.board.gameover[0])
                victory()
                if self.board.gameover[0] == "Insufficient Material" or self.board.gameover[0] == "Stalemate":
                    return self.end_screen(self.board.gameover[0], None)
                else:
                    if self.board.gameover[1] == self.board.player:
                        return self.end_screen(self.board.gameover[0], self.p1_name)
                    else:
                        return self.end_screen(self.board.gameover[0], self.p2_name)

            # Tell AI to determine move if...
            # 1 - It is their turn
            # 2 - They haven't found a move already
            # 3 - The game is not over
            # 4 - They aren't currently searching for a move (ensure 'determine_move' thread is not running)
            self.lock.acquire()
            if self.board.turn == self.p2_color \
                    and self.ai_move.qsize() == 0 \
                    and not self.board.gameover \
                    and not t.is_alive():
                # Need to remake thread, since a thread can only be started once
                t = threading.Thread(target=self.determine_move)
                t.start()
            self.lock.release()

            # Tell AI to make their move if...
            # 1 - It is their turn
            # 2 - They found a move
            # 3 - The game is not over
            if self.board.turn == self.p2_color \
                    and self.ai_move.qsize() > 0 \
                    and not self.board.gameover:
                move = self.ai_move.get()
                self.board.make_move(move[0], move[1])
                self.board.next_turn()

            # Draw all components of board
            self.board.draw()

            # Update display
            pygame.display.flip()

    def end_screen(self, condition, winner=None):

        # Create background for end screen
        bg = pygame.Rect(int(BOARD_X + TILE_SIZE * 2.5), int(BOARD_Y + TILE_SIZE * 2.5), TILE_SIZE * 3, TILE_SIZE * 2)

        # Creates collision boxes for rematch and leave buttons
        rematch_button = pygame.Rect(bg.left, bg.bottom - 28, bg.centerx - bg.left - 2, 28)
        leave_button = pygame.Rect(bg.centerx + 2, bg.bottom - 28, bg.centerx - bg.left - 2, 28)

        # Creates fade transitional effect for end screen
        def fade(width, height):
            f = pygame.Surface((width, height))
            f.fill(BG_COLOR)
            for alpha in range(0, 175):
                f.set_alpha(alpha)
                self.board.draw()
                SCREEN.blit(f, (0, 0))
                pygame.display.update()
                pygame.time.delay(1)

        # Controls fade effect
        fading = True

        # End screen loop
        while True:
            for event in pygame.event.get():
                # Pygame window was closed
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                # Check if any buttons were pressed
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos

                    # Rematch button was pressed
                    if rematch_button.collidepoint(mouse_pos):
                        self.reset()
                        return self.game_screen()

                    # Leave button was pressed
                    if leave_button.collidepoint(mouse_pos):
                        self.reset()
                        return self.menu_screen()

            # Apply fade effect
            if fading:
                fade(SCREEN_WIDTH, SCREEN_HEIGHT)
                fading = False

            # Draw UI elements
            self.draw_end_message(condition, winner)

            # Update display
            pygame.display.flip()

    def draw_names(self):
        # Draw top name (player 2)
        pygame.draw.rect(SCREEN, BG_COLOR_LIGHT, [BOARD_X, BOARD_Y - 36, TILE_SIZE * 2, 28])
        p1name = FONT.render(self.p2_name, True, SMALL_TEXT_COLOR)
        SCREEN.blit(p1name, (BOARD_X + 4, BOARD_Y - 34))
        # Draw bottom name (player 1)
        pygame.draw.rect(SCREEN, BG_COLOR_LIGHT, [BOARD_X, BOARD_Y + BOARD_SIZE + 8, TILE_SIZE * 2, 28])
        p2name = FONT.render(self.p1_name, True, SMALL_TEXT_COLOR)
        SCREEN.blit(p2name, (BOARD_X + 4, BOARD_Y + BOARD_SIZE + 10))

    @staticmethod
    def draw_end_message(condition, winner):
        # Draw 'Game Over' text
        bg = pygame.draw.rect(SCREEN, BG_COLOR_LIGHT,
                              [int(BOARD_X + TILE_SIZE * 2.5), int(BOARD_Y + TILE_SIZE * 2.5), TILE_SIZE * 3,
                               TILE_SIZE * 2])
        pygame.draw.rect(SCREEN, BLACK,
                         [int(BOARD_X + TILE_SIZE * 2.5), int(BOARD_Y + TILE_SIZE * 2.5), TILE_SIZE * 3, TILE_SIZE * 2],
                         1)
        txt = BIG_FONT.render("Game Over", True, LARGE_TEXT_COLOR)
        SCREEN.blit(txt, (BOARD_X + TILE_SIZE * 3 - 8, int(BOARD_Y + TILE_SIZE * 2.5 + 4)))

        # Draw win condition and winner (if applicable)
        if winner:
            txt = FONT.render(winner + " won", True, SMALL_TEXT_COLOR)
            SCREEN.blit(txt, (BOARD_X + TILE_SIZE * 3, BOARD_Y + TILE_SIZE * 3 + 4))
            txt = FONT.render(f"by {condition}", True, SMALL_TEXT_COLOR)
            SCREEN.blit(txt, (BOARD_X + TILE_SIZE * 3, int(BOARD_Y + TILE_SIZE * 3.4)))
        else:
            txt = FONT.render(f"{condition}", True, SMALL_TEXT_COLOR)
            if condition == "Insufficient Material":
                SCREEN.blit(txt, (int(BOARD_X + TILE_SIZE * 2.55), int(BOARD_Y + TILE_SIZE * 3.3)))
            else:
                SCREEN.blit(txt, (int(BOARD_X + TILE_SIZE * 3.2), int(BOARD_Y + TILE_SIZE * 3.3)))

        # Draw Rematch button
        pygame.draw.rect(SCREEN, BLACK, [bg.left, bg.bottom - 28, bg.centerx - bg.left + 3, 28], 1)
        txt = FONT.render("Rematch", True, SMALL_TEXT_COLOR)
        SCREEN.blit(txt, (bg.left + 8, bg.bottom - 28 + 2))

        # Draw Leave button
        pygame.draw.rect(SCREEN, BLACK, [bg.centerx + 2, bg.bottom - 28, bg.centerx - bg.left - 2, 28], 1)
        txt = FONT.render("Leave", True, SMALL_TEXT_COLOR)
        SCREEN.blit(txt, (bg.centerx + 20, bg.bottom - 28 + 2))


if __name__ == "__main__":
    Game()

from settings import *


class Tile:
    def __init__(self, piece, x, y):
        self.piece = piece
        self.x = x
        self.y = y
        self.color = BLACK
        self.surface = pygame.Surface((TILE_SIZE, TILE_SIZE))

    def fill(self, color):
        self.surface.fill(color)

    def draw(self):
        SCREEN.blit(self.surface, to_coords(self.x, self.y))
        if self.piece:
            self.piece.draw()

    def contains_piece(self):
        if self.piece.image is None:
            return False
        return True

    def copy(self):
        piece = None
        if self.piece:
            piece = self.piece.copy()
        copy = Tile(piece, self.x, self.y)
        copy.fill(self.color)
        return copy

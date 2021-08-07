from piece import *
from tile import *
from settings import *

import AI
import PhysicalOpponent
import PhysicalBoard
from gpiozero import Button
from time import sleep


class Board:

    def __init__(self, player_color):
        self.tilemap = [[None for _ in range(8)] for _ in range(8)]
        self.initialize_tiles()
        self.selected = None
        self.blackKingCoords = None
        self.whiteKingCoords = None
        self.turn = WHITE
        self.player = player_color
        if self.player == WHITE:
            self.bottomPlayerTurn = True
        else:
            self.bottomPlayerTurn = False
        self.gameover = None

        self.weights = {King: 900, Queen: 650, Rook: 50, Bishop: 30, Knight: 30, Pawn: 10}
        self.blackScore = 1290
        self.whiteScore = 1290

        self.past_moves = []
        
        pixels[32] = (0, 0, 250)
        pixels[33] = (0, 0, 250)
        pixels[34] = (0, 0, 250)
        pixels.show()
        buzzer.beep(0.25, 0.25, 2, False)
        button.wait_for_press()
        pixels[32] = (0, 0, 0)
        pixels[33] = (0, 0, 0)
        pixels[34] = (0, 0, 0)
        pixels.show()
        self.physicalBoardGrid = PhysicalBoard.getPhysicalBoard()
        print("Place chess pieces onto board")
        pixels[34] = (0,0,250)
        pixels.show()
        button.wait_for_press()
        pixels[34] = (0,250,0)
        pixels.show()
        sleep(0.25)
        pixels[34] = (0,0,0)
        pixels.show()
        

    def print(self):
        print("\n-----------------------------------------")
        print("blackKingCoords:  ", self.blackKingCoords)
        print("whiteKingCoords:  ", self.whiteKingCoords)
        print("Turn:             ", self.turn)
        print("CanMoveCount:     ", self.checkmate_stalemate())
        print("InCheck:          ", self.in_check(self.turn))
        print("Player:           ", self.player)
        print("BottomPlayerTurn: ", self.bottomPlayerTurn)
        print("Gameover:         ", self.gameover)
        print("blackScore:       ", self.blackScore)
        print("whiteScore:       ", self.whiteScore)
        print("-----------------------------------------")

    def initialize_pieces(self) -> None:

        # Remove all pieces from board
        for x in range(8):
            for y in range(8):
                self.tilemap[x][y].piece = None

        # Pawns
        for i in range(8):
            self.tilemap[i][1].piece = Pawn(i, 1, BLACK)
            self.tilemap[i][6].piece = Pawn(i, 6, WHITE)

        # Rooks
        self.tilemap[0][0].piece = Rook(0, 0, BLACK)
        self.tilemap[7][0].piece = Rook(7, 0, BLACK)
        self.tilemap[0][7].piece = Rook(0, 7, WHITE)
        self.tilemap[7][7].piece = Rook(7, 7, WHITE)

        # Knights
        self.tilemap[1][0].piece = Knight(1, 0, BLACK)
        self.tilemap[6][0].piece = Knight(6, 0, BLACK)
        self.tilemap[1][7].piece = Knight(1, 7, WHITE)
        self.tilemap[6][7].piece = Knight(6, 7, WHITE)

        # Bishops
        self.tilemap[2][0].piece = Bishop(2, 0, BLACK)
        self.tilemap[5][0].piece = Bishop(5, 0, BLACK)
        self.tilemap[2][7].piece = Bishop(2, 7, WHITE)
        self.tilemap[5][7].piece = Bishop(5, 7, WHITE)

        # Queens
        self.tilemap[3][0].piece = Queen(3, 0, BLACK)
        self.tilemap[3][7].piece = Queen(3, 7, WHITE)

        # Kings
        self.tilemap[4][0].piece = King(4, 0, BLACK)
        self.tilemap[4][7].piece = King(4, 7, WHITE)

        # Store coords of both kings
        self.blackKingCoords = (4, 0)
        self.whiteKingCoords = (4, 7)

        # Reverse piece positions if player is playing black
        if self.player == BLACK:
            self.blackKingCoords = (4, 7)
            self.whiteKingCoords = (4, 0)
            for x in range(8):
                for y in range(8):
                    if self.piece_at_coords((x, y)):
                        if self.tilemap[x][y].piece.color == BLACK:
                            self.tilemap[x][y].piece.color = WHITE
                        else:
                            self.tilemap[x][y].piece.color = BLACK

    def initialize_tiles(self) -> None:
        cnt = 0
        for x in range(8):
            for y in range(8):
                tile = Tile(None, x, y)
                if cnt % 2 == 0:
                    tile.color = TILE_COLOR_LIGHT
                    tile.fill(TILE_COLOR_LIGHT)
                else:
                    tile.color = TILE_COLOR_DARK
                    tile.fill(TILE_COLOR_DARK)
                self.tilemap[x][y] = tile
                cnt += 1
            cnt += 1

    def draw(self) -> None:
        # Draw tiles and pieces
        for row in self.tilemap:
            for tile in row:
                tile.draw()

    def select(self) -> None:
        prevState = PhysicalBoard.takePicture('previousState')
        print("PRESS BUTTON AFTER MOVING")
        
        pixels[33] = (0, 0, 250)
        pixels.show()
        buzzer.beep(0.25, 0.25, 2, False)
        button.wait_for_press()
        pixels[33] = (0, 0, 0)
        pixels.show()
        positionChanges = PhysicalBoard.playerMove(prevState, self.physicalBoardGrid)
        
        
        if self.piece_at_coords((positionChanges[0][0], positionChanges[0][1])) and self.tilemap[positionChanges[0][0]][positionChanges[0][1]].piece.color == WHITE:
            print(positionChanges[0], positionChanges[1])
            self.make_move((positionChanges[0][0], positionChanges[0][1]), (positionChanges[1][0], positionChanges[1][1]))
        elif self.piece_at_coords((positionChanges[1][0], positionChanges[1][1])) and self.tilemap[positionChanges[1][0]][positionChanges[1][1]].piece.color == WHITE:
            print(positionChanges[1], positionChanges[0])
            self.make_move((positionChanges[1][0], positionChanges[1][1]), (positionChanges[0][0], positionChanges[0][1]))
            
        self.next_turn()
        return      
        

    def copy(self):
        copy = Board(self.player)
        for x in range(8):
            for y in range(8):
                if self.piece_at_coords((x, y)):
                    copy.tilemap[x][y].piece = self.tilemap[x][y].piece.copy()
        copy.selected = self.selected
        copy.blackKingCoords = self.blackKingCoords
        copy.whiteKingCoords = self.whiteKingCoords
        copy.turn = self.turn
        copy.bottomPlayerTurn = self.bottomPlayerTurn
        copy.player = self.player
        copy.gameover = self.gameover
        copy.weights = self.weights
        copy.blackScore = self.blackScore
        copy.whiteScore = self.whiteScore
        return copy

    @staticmethod
    def in_bounds(coords) -> bool:
        if coords[0] < 0 or coords[0] >= 8 or coords[1] < 0 or coords[1] >= 8:
            return False
        return True

    def piece_at_coords(self, coords) -> bool:
        if not self.in_bounds(coords) or self.tilemap[coords[0]][coords[1]].piece is None:
            return False
        return True

    def enemy_at_coords(self, coords, color) -> bool:
        if self.piece_at_coords(coords):
            return self.tilemap[coords[0]][coords[1]].piece.color != color

    def valid_move(self, dest, color) -> bool:
        if self.in_bounds(dest) \
                and (not self.piece_at_coords(dest) or self.enemy_at_coords(dest, color)):
            return True
        return False

    def in_check(self, color) -> bool:
        if color == BLACK:
            king_coords = self.blackKingCoords
        else:
            king_coords = self.whiteKingCoords

        # Check if position of King is in any of the valid moves for opposite player
        for x in range(8):
            for y in range(8):
                if self.enemy_at_coords((x, y), color):
                    for move in self.tilemap[x][y].piece.valid_moves(self):
                        if move[0] == king_coords[0] and move[1] == king_coords[1]:
                            return True

        return False

    def in_check_after_move(self, source, dest, color) -> bool:

        # Get shorthand for source and destination tiles and pieces
        source_tile = self.tilemap[source[0]][source[1]]
        dest_tile = self.tilemap[dest[0]][dest[1]]
        source_piece = source_tile.piece
        dest_piece = dest_tile.piece

        # Preserve king coords
        king_coords = None
        if type(source_piece) is King:
            if color == BLACK:
                king_coords = self.blackKingCoords
            else:
                king_coords = self.whiteKingCoords

        # Move piece from source tile to dest tile
        dest_tile.piece = source_piece
        dest_tile.piece.move(dest_tile.x, dest_tile.y)
        source_tile.piece = None

        # Set king coords
        if type(source_piece) is King:
            if color == BLACK:
                self.blackKingCoords = (dest_tile.piece.x, dest_tile.piece.y)
            else:
                self.whiteKingCoords = (dest_tile.piece.x, dest_tile.piece.y)

        # Set player position
        self.bottomPlayerTurn = not self.bottomPlayerTurn

        # See if in check state after move
        if self.in_check(color):
            in_check = True
        else:
            in_check = False

        # Restore king coords
        if type(source_piece) is King:
            if color == BLACK:
                self.blackKingCoords = king_coords
            else:
                self.whiteKingCoords = king_coords

        # Restore player position
        self.bottomPlayerTurn = not self.bottomPlayerTurn

        # Move piece back
        source_tile.piece = source_piece
        dest_tile.piece = dest_piece
        source_tile.piece.move(source_tile.x, source_tile.y)

        return in_check

    def make_move(self, source, dest):

        # Get shorthand for source and destination tiles
        source_tile = self.tilemap[source[0]][source[1]]
        dest_tile = self.tilemap[dest[0]][dest[1]]

        # Store previous state to allow for unmaking move
        previous_state = {"blackScore": self.blackScore,
                          "whiteScore": self.whiteScore,
                          "blackKingCoords": self.blackKingCoords,
                          "whiteKingCoords": self.whiteKingCoords,
                          "tile1": (source, source_tile.copy()),
                          "tile2": (dest, dest_tile.copy()),
                          "gameover": self.gameover
                          }
        self.past_moves.append(previous_state)

        # Update scores
        if dest_tile.piece:
            if self.turn == WHITE:
                self.blackScore -= self.weights[type(dest_tile.piece)]
            else:
                self.whiteScore -= self.weights[type(dest_tile.piece)]

        # Promote piece if it meets requirements
        if type(source_tile.piece) is Pawn:
            if (self.bottomPlayerTurn and dest_tile.y == 0) or (not self.bottomPlayerTurn and dest_tile.y == 7):
                source_tile.piece = Queen(source_tile.piece.x, source_tile.piece.y, source_tile.piece.color)

        # Move piece from source tile to dest tile
        dest_tile.piece = source_tile.piece
        source_tile.piece.move(dest_tile.x, dest_tile.y)
        dest_tile.piece.firstMove = False
        
        # Update king coords if necessary
        if type(source_tile.piece) is King:
            if source_tile.piece.color == BLACK:
                self.blackKingCoords = dest_tile.x, dest_tile.y
            else:
                self.whiteKingCoords = dest_tile.x, dest_tile.y

        # Remove piece from source tile
        source_tile.piece = None
        source_tile.fill(source_tile.color)
        if(self.turn == BLACK):
            print(source_tile.x, source_tile.y, dest_tile.x, dest_tile.y)
            light2.LED_Position(source_tile.x, source_tile.y, dest_tile.x, dest_tile.y, self.physicalBoardGrid)

        # Check win conditions
        self.checkmate_stalemate()
        self.insufficient_material()

    def unmake_move(self):
        # Revert to previous game state using stored values
        previous_state = self.past_moves.pop()
        self.blackScore = previous_state["blackScore"]
        self.whiteScore = previous_state["whiteScore"]
        self.blackKingCoords = previous_state["blackKingCoords"]
        self.whiteKingCoords = previous_state["whiteKingCoords"]
        x = previous_state["tile1"][0][0]
        y = previous_state["tile1"][0][1]
        self.tilemap[x][y] = previous_state["tile1"][1]
        x = previous_state["tile2"][0][0]
        y = previous_state["tile2"][0][1]
        self.tilemap[x][y] = previous_state["tile2"][1]
        self.gameover = previous_state["gameover"]

        self.next_turn()

    def next_turn(self) -> None:
        if self.turn == WHITE:
            self.turn = BLACK
        else:
            self.turn = WHITE

        self.bottomPlayerTurn = not self.bottomPlayerTurn

    def checkmate_stalemate(self) -> bool:

        legal_moves = 0
        for x in range(8):
            for y in range(8):
                if self.piece_at_coords((x, y)) and self.tilemap[x][y].piece.color == self.turn:
                    moves = self.tilemap[x][y].piece.valid_moves(self)  # + self.can_castle(self.tilemap[x][y].piece.color)
                    for move in moves:
                        if not self.in_check_after_move((x, y), move, self.tilemap[x][y].piece.color):
                            legal_moves += 1

        if self.turn == WHITE:
            opponent = BLACK
        else:
            opponent = WHITE

        if legal_moves == 0 and not self.in_check(self.turn):
            self.gameover = ("Stalemate", None)
        elif legal_moves == 0:
            self.gameover = ("Checkmate", opponent)

    def get_moves(self):
        moves = []
        for x in range(8):
            for y in range(8):
                if self.piece_at_coords((x, y)) and self.tilemap[x][y].piece.color == self.turn:
                    for move in self.tilemap[x][y].piece.valid_moves(self):
                        if not self.in_check_after_move((x, y), move, self.turn):
                            if self.enemy_at_coords(move, self.turn):
                                moves.insert(0, ((x, y), move))
                            else:
                                moves.append(((x, y), move))
        return list(set(moves))

    def get_moves_sorted(self):
        b = self.copy()
        moves = {}
        for x in range(8):
            for y in range(8):
                if self.piece_at_coords((x, y)) and self.tilemap[x][y].piece.color == self.turn:
                    for move in self.tilemap[x][y].piece.valid_moves(self):
                        if not self.in_check_after_move((x, y), move, self.turn) and ((x, y), move) not in moves:
                            b.make_move((x, y), move)
                            moves[((x, y), move)] = AI.evaluate(b, self.turn)
                            b.unmake_move()
        return [move for move, score in sorted(moves.items(), key=lambda v: v[1], reverse=True)]

    def insufficient_material(self):
        # Insufficient material
        piece_counts = {"wminor": 0, "bminor": 0, "king": 0, "wknight": 0, "bknight": 0}
        for x in range(8):
            for y in range(8):
                piece = self.tilemap[x][y].piece
                if piece:
                    # if a Queen is present, insufficient material is impossible
                    if type(piece) is Queen:
                        return
                    if type(piece) is King:
                        piece_counts["king"] += 1
                    elif type(piece) is Knight and piece.color == WHITE:
                        piece_counts["wknight"] += 1
                    elif type(piece) is Knight and piece.color == BLACK:
                        piece_counts["bknight"] += 1
                    else:
                        if piece.color == WHITE:
                            piece_counts["wminor"] += 1
                        elif piece.color == BLACK:
                            piece_counts["bminor"] += 1

        # King vs King
        if piece_counts["wminor"] == piece_counts["bminor"] == piece_counts["wknight"] == piece_counts["bknight"] == 0 and piece_counts["king"] == 2:
            self.gameover = ("Insufficient Material", None)
        # King + minor piece vs King
        elif ((piece_counts["wminor"] == 1 and piece_counts["bminor"] == 0) or (piece_counts["bminor"] == 1 and piece_counts["wminor"] == 0)) and piece_counts["king"] == 2 and piece_counts["bknight"] == piece_counts["wknight"] == 0:
            self.gameover = ("Insufficient Material", None)
        # King + two Knights vs King
        elif (piece_counts["wknight"] == 2 and piece_counts["king"] == 2 and piece_counts["wminor"] == piece_counts["bminor"] == 0) or (piece_counts["bknight"] == 2 and piece_counts["king"] == 2 and piece_counts["wminor"] == piece_counts["bminor"] == 0):
            self.gameover = ("Insufficient Material", None)
        elif (piece_counts["wminor"] == 1 and piece_counts["king"] == 2 and piece_counts["bminor"] == 0) or (piece_counts["bminor"] == 1 and piece_counts["king"] == 2 and piece_counts["wminor"] == 0):
            self.gameover = ("Insufficient Material", None)




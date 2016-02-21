# board-- list of lists of chars
# "piece" is the one moving collection of coordinates that we have control over
# once a "piece" is stationary, then it sort of dissolved into the board
# board keeps track of the filled-in spaced so that it can remove rows that are all full
# as the piece moves, board updates with a certain frequency, and in the time between refreshes, we'll wait for user input

# step 1: build board
# step 2: build piece
# step 3: board logic to play game

import copy
import os
import random
import time
from get_c import get_c

class TetrisBoard:
    def __init__(self, height, width):
        """Create a Tetris board.

        Initializes refresh_rate at 0.3 seconds, points at 0, and level at 1.

        Args:
            height (int): Length of board.
            width (int): Width of board.
        """
        self.height, self.width = height, width
        self.board = self.create_board_matrix(height, width)
        self.refresh_rate = 0.3
        self.points = 0  # pieces successfully added
        self.level = 1

    def create_board_matrix(self, height, width):
        """Create matrix to display Tetris board."""
        return [[' '] * width for _ in xrange(height)]

    def display_board(self):
        """Display instructions, board, points, and level."""
        os.system('clear')
        print 'Press "j" to move Left, "l" to move Right, and "k" to Invert the piece.'
        for row in self.board:
            print row
        print 'Points: {}'.format(self.points)
        print 'Level: {}'.format(self.level)

    def add_piece(self):
        """Add a new piece to the board, checking for any collisions."""
        self.active_piece = None
        piece_type = random.randint(0, len(TetrisPiece.PIECE_TYPES) - 1)
        max_row = 10 - TetrisPiece.get_piece_width(piece_type)
        origin = (0, random.randint(0, max_row))
        self.active_piece = TetrisPiece(piece_type, origin)
        if self.will_collide(direction='origin'):
            return False
        else:
            self.points += 1
            return True

    def display_piece(self, clear=False):
        """Place characters on self.board at each of the positions with respect to orgin."""
        for row, col in self.active_piece.positions:
            y, x = self.active_piece.origin[0] + row, self.active_piece.origin[1] + col
            self.board[y][x] = '#' if not clear else ' '

    def update_board_and_check_for_eog(self):
        """Clear piece, check for collisions or end-of-game, move or add piece accordingly.

        Returns:
            str or None: str acknowledges end-of-game.
        """
        self.display_piece(clear=True)
        if self.will_collide():
            self.display_piece()  # put the piece back
            over = self.check_and_clear_rows()  # clear rows, check to see if top has been reached
            if over:
                return over
            else:
                added_piece = self.add_piece()
                if added_piece:
                    self.check_points_and_level_up()
                else:
                    return "Game Over! Couldn't add another piece."
        else:
            self.move_piece()

    def move_piece(self, direction=None):
        """Check for collisions and move piece according to direction.

        Kwargs:
            direction (str): One of 'right', 'left', or 'rotate'. If left as None, then the piece
                             will move down one square with respect to its origin.
        """
        if self.will_collide(direction=direction):
            return
        self.active_piece.move(direction=direction)
        self.display_piece()

    def will_collide(self, direction=None):
        """Check for collisions without moving the piece.

        Kwargs:
            direction (str): One of 'right', 'left', 'origin', or 'rotate'. If left as None, then
                             the piece will move down one square with respect to its origin.
        """
        new_origin, new_positions = self.active_piece.try_move(direction=direction)
        for row, col in new_positions:
            y, x = new_origin[0] + row, new_origin[1] + col
            if y > 19 or y < 0 or x > 9 or x < 0 or self.board[y][x] == '#':
                return True
        return False

    def get_input(self):
        """Get movement input from user."""
        directions = {'j': 'left', 'l': 'right', 'k': 'rotate'}
        direction = get_c()
        if direction and direction in directions.keys():
            return directions[direction]

    def check_and_clear_rows(self):
        """Check to see if the board is finished or if any given row is full."""
        # if board is full, then there will be a '#' in the first row
        if '#' in self.board[0]:
            return 'Game Over! Top has been reached.'
        for row in xrange(self.height):
            # if any given row is full, then that row won't have any blank spaces
            if not ' ' in self.board[row]:
                del self.board[row]
                self.board.insert(0, [' '] * self.width)

    def check_points_and_level_up(self):
        """Check if the user has enough points to decrement the refresh rate and increase their
        level.
        """
        if self.points > 20 * self.level:
            self.level += 1
            self.refresh_rate = self.refresh_rate * 0.75

    def play_game(self):
        """Play the Tetris game."""
        print('Welcome to Tetris! To play, press "j" to move Left, "l" to move Right, and "k" to '
              'Invert the piece.')
        raw_input('Press any key to acknowledge.')
        board.add_piece()
        board.display_piece()
        board.display_board()
        while True:
            over = board.update_board_and_check_for_eog()
            if over:
                print over
                break
            board.display_board()
            start = time.time()
            while time.time() - start < self.refresh_rate:
                direction = board.get_input() # right, left
                if direction:
                    board.display_piece(clear=True)
                    board.move_piece(direction=direction)
                    board.display_board()
                time.sleep(0.1)
        print 'You got {} points!'.format(board.points)
        return


class TetrisPiece:
    # row, col (with respect to origin)
    PIECE_TYPES = [
        [(0, 0), (1, 0), (2, 0), (3, 0)],
        [(0, 0), (1, 0), (0, 1), (1, 1)],
        [(0, 0), (1, 0), (1, 1), (2, 1)],
        [(0, 0), (1, 0), (1, 1), (2, 0)],
        [(0, 1), (1, 1), (1, 0), (2, 0)],
        [(0, 0), (1, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (2, 0)],
    ]

    def __init__(self, piece_type, origin):
        """Create a Tetris piece.

        Args:
            piece_type (int): Integer corresponding to the index of an item in PIECE_TYPES.
            origin (tuple(int, int)): Tuple corresponding to the piece's positon on some
                                      theoretical board.
        """
        self.origin = origin
        self.positions = self.get_piece_coordinates(piece_type)

    @classmethod
    def get_piece_width(cls, piece_type):
        max_x = 0
        piece_positions = cls.PIECE_TYPES[piece_type]
        for y, x in piece_positions:
            max_x = x + 1 if max_x < x + 1 else max_x
        return max_x

    def get_piece_coordinates(self, piece_type):
        """Get piece coordinates."""
        return self.PIECE_TYPES[piece_type]

    def try_move(self, direction=None):
        """Get the origin and positon coordinates for the given direction.

        Kwargs:
            direction (str): One of 'right', 'left', 'origin', or 'rotate'. If left as None, then
                             the piece will move down one square with respect to its origin.

        Returns:
            tuple(tuple, list(tuple)): New origin and new list of positions.
        """
        if direction == 'rotate':
            return (self.origin, self.simple_rotate())
        else:
            return (self.get_new_origin(direction=direction), self.positions)

    def get_new_origin(self, direction=None):
        """Get new origin for the given direction.

        Kwargs:
            direction (str): One of 'right', 'left', or 'origin'. If left as None, then the origin
                             will move down one square with respect to its original origin.

        Returns:
            tuple: New origin coordinates-- (row, column)
        """
        y, x = 1, 0
        direction_coords = {'origin': (0, 0), 'right': (0, 1), 'left': (0, -1)}
        if direction and direction in direction_coords:
            y, x = direction_coords[direction]
        return (self.origin[0] + y, self.origin[1] + x)

    def move(self, direction=None):
        """Move piece in the given direction.

        Kwargs:
            direction (str): One of 'right', 'left', 'origin', or 'rotate'. If left as None, then
                             the piece will move down one square with respect to its origin.
        """
        if direction == 'rotate':
            self.positions = self.simple_rotate()
        else:
            self.origin = self.get_new_origin(direction=direction)

    def simple_rotate(self):
        """Invert the positon coordinates for the piece."""
        new_positions = []
        for i, pos in enumerate(self.positions):
            new_positions.append((pos[1], pos[0]))
        return new_positions


board = TetrisBoard(20, 10)
board.play_game()

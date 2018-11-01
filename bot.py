from __future__ import print_function
from random import randint
try:
    from sys import maxint
except:
    from sys import maxsize
    maxint = maxsize

minint = (-maxint) - 1

try:
    raw_input
except:
    raw_input = input

WHITE = 0
BLACK = 1

class Game:
    def __init__(self):
        self.pieces = [None, None]
        self.pieces[WHITE] =  [
            Pawn(6, 0, WHITE),
            Pawn(6, 1, WHITE),
            Pawn(6, 2, WHITE),
            Pawn(6, 3, WHITE),
            Pawn(6, 4, WHITE),
            Pawn(6, 5, WHITE),
            Pawn(6, 6, WHITE),
            Pawn(6, 7, WHITE),
            Rook(7, 0, WHITE),
            Knight(7, 1, WHITE),
            Bishop(7, 2, WHITE),
            Queen(7, 3, WHITE),
            King(7, 4, WHITE),
            Bishop(7, 5, WHITE),
            Knight(7, 6, WHITE),
            Rook(7, 7, WHITE)]
        self.pieces[BLACK] = [
            Rook(0, 0, BLACK),
            Knight(0, 1, BLACK),
            Bishop(0, 2, BLACK),
            Queen(0, 3, BLACK),
            King(0, 4, BLACK),
            Bishop(0, 5, BLACK),
            Knight(0, 6, BLACK),
            Rook(0, 7, BLACK),
            Pawn(1, 0, BLACK),
            Pawn(1, 1, BLACK),
            Pawn(1, 2, BLACK),
            Pawn(1, 3, BLACK),
            Pawn(1, 4, BLACK),
            Pawn(1, 5, BLACK),
            Pawn(1, 6, BLACK),
            Pawn(1, 7, BLACK)]
        b = self.pieces[BLACK]
        w = self.pieces[WHITE]
        self.dead_pieces = []
        self.board = [
            [ b[0],  b[1],  b[2],  b[3],  b[4],  b[5],  b[6],  b[7]],
            [ b[8],  b[9], b[10], b[11], b[12], b[13], b[14], b[15]],
            [ None,  None,  None,  None,  None,  None,  None,  None],
            [ None,  None,  None,  None,  None,  None,  None,  None],
            [ None,  None,  None,  None,  None,  None,  None,  None],
            [ None,  None,  None,  None,  None,  None,  None,  None],
            [ w[0],  w[1],  w[2],  w[3],  w[4],  w[5],  w[6],  w[7]],
            [ w[8],  w[9], w[10], w[11], w[12], w[13], w[14], w[15]]
        ]
        self.piece_values = {
            King: 600000,
            Queen: 9,
            Rook: 5,
            Bishop: 3.4,
            Knight: 3.2,
            Pawn: 1
        }
        self.turn = WHITE
        self.ply = 1
        self.moves = []
        self.winner = None
#
    def print_board(self, with_axes=True, show_moved_from=True):
        for x in range(len(self.board)):
            print('-' * (len(self.board[x]) * 4 + 1))
            for y in range(len(self.board[x])):
                print('| ' + ('•' if len(self.moves) > 1 and self.moves[-1][0] == (x, y) else ' ' if not isinstance(self.board[x][y], Piece) else self.board[x][y].get_char()) + ' ', end='')
            print('|' if not with_axes else '| ' + str(x))
        print('-' * (len(self.board[-1]) * 4 + 1))
        if with_axes:
            print(' '.join(['  ' + str(i) for i in range(len(self.board[0]))]))
        print()
#
    def get_moves(self, color=None):
        # todo: castling, en passant, pawn promotion
        if color is None:
            color = self.turn
        move_list = []
        for piece in self.pieces[color]:
            move_list.extend(piece.get_move_list(self.board))
        return move_list
#
    def move(self, move):
        assert self.winner == None
        xfrom, yfrom = move[0]
        xto, yto = move[1]
        if isinstance(self.board[xto][yto], Piece):
            piece_to_remove = self.board[xto][yto]
            if type(piece_to_remove) is King:
                self.winner = self.other_color(piece_to_remove.get_color())
            piece_to_remove.died_at = self.ply
            self.dead_pieces.append(piece_to_remove)
            ind_of_piece_to_remove = self.pieces[piece_to_remove.get_color()].index(piece_to_remove)
            self.pieces[piece_to_remove.get_color()].pop(ind_of_piece_to_remove)
        if not len(move) == 3:
            self.board[xfrom][yfrom].move((xto, yto), self.ply)
            self.board[xto][yto] = self.board[xfrom][yfrom]
        elif type(self.board[xfrom][yfrom]) is Pawn:  # pawn promotion... congrats!
            pawn, color = self.board[xfrom][yfrom], self.board[xfrom][yfrom].get_color()
            promoted_piece = move[2](xto, yto, color)
            self.pieces[color][self.pieces[color].index(pawn)] = promoted_piece
            self.board[xto][yto] = promoted_piece
            if hasattr(promoted_piece, "has_moved"):
                promoted_piece.has_moved = True
            promoted_piece.moved_before_promotion = pawn.has_moved
        elif type(move[2]) is Rook:  # castling
            pass
        self.board[xfrom][yfrom] = None
        self.ply += 1
        self.turn = self.other_color(self.turn)
        self.moves.append(move)
#
    def unmove(self):
        move = self.moves.pop()
        self.turn = self.other_color(self.turn)
        xfrom, yfrom = move[0]
        xto, yto = move[1]
        self.ply -= 1
        self.board[xfrom][yfrom] = self.board[xto][yto]
        self.board[xto][yto] = None
        if len(move) == 3 and move[2] is type(self.board[xfrom][yfrom]):
            piece_to_demote = self.board[xfrom][yfrom]
            color = piece_to_demote.get_color()
            self.board[xfrom][yfrom] = Pawn(xto, yto, color)
            self.board[xfrom][yfrom].has_moved = piece_to_demote.moved_before_promotion
            self.pieces[color].pop(self.pieces[color].index(piece_to_demote))
            self.pieces[color].append(self.board[xfrom][yfrom])
        elif len(move) == 3 and type(move[2]) is Rook:
            pass
        self.board[xfrom][yfrom].unmove((xfrom, yfrom), self.ply)
        for piece in self.dead_pieces:
            if piece.died_at == self.ply:
                assert (piece.x, piece.y) == (xto, yto)
                if self.winner is not None:
                    assert self.winner != piece.get_color()
                    self.winner = None
                self.pieces[piece.get_color()].append(piece)
                self.board[piece.x][piece.y] = piece
                self.dead_pieces.pop(self.dead_pieces.index(piece))
                del piece.died_at
                break
#
    def show_moves(self):
        possible_moves = self.get_moves(WHITE)
        for move in possible_moves:
            self.move(move)
            self.print_board(1)
            _ = raw_input()
            self.unmove()
        self.print_board(1)
#
    def random_play(self):
        moves = self.get_moves()
        inp = ''
        while len(moves) > 0 and inp != 'exit':
            self.move(moves[randint(0, len(moves) - 1)])
            self.print_board(1)
            inp = raw_input()
            moves = self.get_moves()
#
    def make_best_move(self, depth=3):
        # original_depth = depth
        # depth = max(2, depth - 2)
        global n
        n = 0
        # value, best_move = self.get_best_move(depth, True)
        value, best_move = self.get_best_move_alpha(depth, minint, maxint, True, self.turn)
        print(n)
        print(value, best_move)
        inp = ''
        while best_move != None and inp != 'exit':
            # if self.ply == 5:
            #     depth = original_depth
            self.move(best_move)
            print(value, best_move)
            self.print_board(1)
            inp = raw_input()
            if inp == 'exit':
                break
            n = 0
            # value, best_move = self.get_best_move(depth, True)
            value, best_move = self.get_best_move_alpha(depth, minint, maxint, True, self.turn)
            print(n)
#
    def play_against_best_move(self, depth=3):
        global n
        n = 0
        value, best_move = self.get_best_move_alpha(depth, minint, maxint, True, self.turn)
        print(n)
        print(value, best_move)
        inp = ''
        while best_move != None and inp != 'exit':
            self.move(best_move)
            print(value, best_move)
            self.print_board(1)
            inp = raw_input()
            if inp == 'exit':
                break
            move = [tuple(map(int, x.split(','))) for x in inp.split(' ')]
            self.move(move)
            print(move)
            self.print_board(1)
            n = 0
            value, best_move = self.get_best_move_alpha(depth, minint, maxint, True, self.turn)
            print(n)
#
    def get_best_move(self, depth, maxing_player):
        global n
        n += 1
        moves = self.get_moves()
        if depth == 0 or len(moves) == 0:
            return ((-1) * self.get_board_value(), None)
        if maxing_player:
            value = minint
            best_move = None
            for move in moves:
                self.move(move)
                new_val, _ = self.get_best_move(depth - 1, False)
                # if (new_val == value and randint(0, 1)) or new_val > value:
                if new_val > value:
                    value = new_val
                    best_move = move
                self.unmove()
            return (value, best_move)
        else:
            value = maxint
            best_move = None
            for move in moves:
                self.move(move)
                new_val, _ = self.get_best_move(depth - 1, True)
                # if (new_val == value and randint(0, 1)) or new_val < value:
                if new_val < value:
                    value = new_val
                    best_move = move
                self.unmove()
            return (value, best_move)
#
    def get_best_move_alpha(self, depth, alpha, beta, maxing_player, valued_player):
        global n
        n += 1
        if self.winner is not None:
            return (maxint if self.winner is valued_player else minint, None)
        moves = self.get_moves()
        if depth == 0 or len(moves) == 0:
            return (self.get_board_value(valued_player), None)
        if maxing_player:
            value = minint
            best_move = None
            for move in moves:
                self.move(move)
                new_val, _ = self.get_best_move_alpha(depth - 1, alpha, beta, False, valued_player)
                # if (new_val == value and randint(0, 1)) or new_val > value:
                if new_val > value:
                    value = new_val
                    best_move = move
                alpha = max(alpha, value)
                self.unmove()
                if alpha >= beta:
                    break
            return (value, best_move)
        else:
            value = maxint
            best_move = None
            for move in moves:
                self.move(move)
                new_val, _ = self.get_best_move_alpha(depth - 1, alpha, beta, True, valued_player)
                # if (new_val == value and randint(0, 1)) or new_val < value:
                if new_val < value:
                    value = new_val
                    best_move = move
                beta = min(beta, value)
                self.unmove()
                if alpha >= beta:
                    break
            return (value, best_move)
#
    def get_board_value(self, color=None):
        if color is None:
            color = WHITE
        return sum([self.piece_value(piece) for piece in self.pieces[color]]) \
             - sum([self.piece_value(piece) for piece in self.pieces[self.other_color(color)]])
#
    def piece_value(self, piece):
        modifier = 0
        if hasattr(piece, "get_modifier"):
            modifier = piece.get_modifier(self.board)
        return self.piece_values[type(piece)] + modifier
#
    def set_from_fen(self, fen_str):
        def get_color(ch):
            return int(ch.islower())
        def get_piece(x, y, ch):
            color = get_color(ch)
            return {
                'k': King,
                'q': Queen,
                'r': Rook,
                'b': Bishop,
                'n': Knight,
                'p': Pawn
            }[ch.lower()](x, y, color)  # return initialized piece object
        fen_lines = fen_str.split('/')
        new_pieces = [[], []]
        new_board = [[None for x in range(8)] for y in range(8)]
        for x in range(8):
            y = -1
            for ch in fen_lines[x]:
                if ch.isdigit():
                    y += int(ch)
                else:
                    y += 1
                    piece = get_piece(x, y, ch)
                    new_pieces[get_color(ch)].append(piece)
                    new_board[x][y] = piece
        self.board = new_board
        self.pieces = new_pieces
        self.ply = 1
        self.turn = 0
        self.moves = []
#
    @staticmethod
    def other_color(color):
        return 1 - color

class Move(object):
    def __init__(self, src, dst, removes=None, state_change=None, promote_to=None):
        self.src = src
        self.dst = dst
        self.removes = removes
        self.promote_to = promote_to
        self.state_change = state_change

class Piece(object):
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
#
    def get_color(self):
        return self.color
#
    def get_diagonals(self, board):
        directions = ((-1, -1), (-1, 1), (1, 1), (1, -1))
        diags = [[] for _ in range(4)]
        for i in range(4):
            x_inc, y_inc = directions[i]
            x, y = self.x + x_inc, self.y + y_inc
            while 0 <= x <= 7 and 0 <= y <= 7 \
            and (board[x][y] is None \
                or (isinstance(board[x][y], Piece) \
                    and board[x][y].get_color() is not self.color)):
                diags[i].append((x, y))
                if isinstance(board[x][y], Piece) and board[x][y].get_color() is not self.color:
                    break
                x += x_inc
                y += y_inc
        return diags
#
    def get_horizontals(self, board):
        directions = ((-1, 0), (0, 1), (1, 0), (0, -1))
        horizons = [[] for _ in range(4)]
        for i in range(4):
            x_inc, y_inc = directions[i]
            x, y = self.x + x_inc, self.y + y_inc
            while 0 <= x <= 7 and 0 <= y <= 7 \
            and (board[x][y] is None \
                or (isinstance(board[x][y], Piece) \
                    and board[x][y].get_color() is not self.color)):
                horizons[i].append((x, y))
                if isinstance(board[x][y], Piece) and board[x][y].get_color() is not self.color:
                    break
                x += x_inc
                y += y_inc
        return horizons
#
    def get_Ls(self, board):
        offsets = ((-2, -1), (-2, 1), (-1, 2), (1, 2), (2, 1), (2, -1), (1, -2), (-1, -2))
        jumps = []
        for i in range(len(offsets)):
            x, y = self.x + offsets[i][0], self.y + offsets[i][1]
            if 0 <= x <= 7 and 0 <= y <= 7 \
            and (board[x][y] is None \
                or (isinstance(board[x][y], Piece) \
                    and board[x][y].get_color() is not self.color)):
                jumps.append((x, y))
        return jumps
#
    def move(self, dest, ply=None):
        self.x, self.y = dest
        if hasattr(self, "has_moved") and not self.has_moved:
            self.has_moved = ply
        if hasattr(self, "just_moved") and not self.just_moved:
            self.just_moved = ply
#
    def unmove(self, src, ply=None):
        self.x, self.y = src
        if hasattr(self, "has_moved") and ply == self.has_moved:
            self.has_moved = False
        if hasattr(self, "just_moved") and ply == self.just_moved:
            self.just_moved = False
#
    def get_move_list(self, board):
        raise NotImplementedError()
#
    def get_char(self):
        raise NotImplementedError()

class Pawn(Piece):
    def __init__(self, x, y, color):
        super(Pawn, self).__init__(x, y, color)
        self.gravity = -1 if self.color == WHITE else 1
        self.start_zone = 6 if self.color == WHITE else 1
        self.end_zone = 0 if self.color == WHITE else 7
#
        self.has_moved = False
        self.just_moved = False  # todo: for en passant
#
    def get_move_list(self, board): # todo: en passant
        move_list = []
        if not self.has_moved and board[self.x + self.gravity][self.y] == None and board[self.x + self.gravity * 2][self.y] == None:
            move_list.append(((self.x, self.y), (self.x + self.gravity * 2, self.y)))
        if 0 <= self.x + self.gravity <= 7 and board[self.x + self.gravity][self.y] == None:
            move_list.append(((self.x, self.y), (self.x + self.gravity, self.y)))
        x, y = self.x + self.gravity, self.y + 1
        if 0 <= x <= 7 and 0 <= y <= 7 and isinstance(board[x][y], Piece) and board[x][y].get_color() != self.color:
            move_list.append(((self.x, self.y), (x, y)))
        x, y = self.x + self.gravity, self.y - 1
        if 0 <= x <= 7 and 0 <= y <= 7 and isinstance(board[x][y], Piece) and board[x][y].get_color() != self.color:
            move_list.append(((self.x, self.y), (x, y)))
        i, n = 0, len(move_list)
        while i < n:
            if move_list[i][1][0] == self.end_zone and len(move_list[i]) == 2:
                move = move_list.pop(i)
                for piece in (Queen, Rook, Bishop, Knight):
                    move_list.append(move + (piece,))
                n -= 1
            else:
                i += 1
        return move_list
#
    def get_modifier(self, board):
        modifier = 0
    #     for x in range(self.start_zone, self.end_zone, self.gravity):
    #         piece = board[x][self.y]
    #         if x != self.x and type(piece) is Pawn and piece.get_color() == self.color:
    #             modifier -= 0.1
    #     safe_spots = (
    #         (self.x + self.gravity, self.y + 1, 0.01),
    #         (self.x + self.gravity, self.y - 1, 0.01),
    #         (self.x + self.gravity * 2, self.y + 1, 0.005),
    #         (self.x + self.gravity * 2, self.y - 1, 0.005)
    #     )
    #     for x, y, val in safe_spots:
    #         if 0 <= x <= 7 and 0 <= y <= 7 \
    #         and type(board[x][y]) is Pawn and board[x][y].get_color() == self.color:
    #             modifier += val
        modifier += (self.gravity * (self.x - self.start_zone) / 4) ** 5
        return modifier
#
    def get_char(self):
        return 'P' if self.color is WHITE else 'p'

class King(Piece):
    def __init__(self, x, y, color):
        super(King, self).__init__(x, y, color)
        self.has_moved = False
        self.has_castled = False
#
    def get_move_list(self, board):
        moves = ((-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1))
        move_list = []
        for i in range(len(moves)):
            x, y = self.x + moves[i][0], self.y + moves[i][1]
            if 0 <= x <= 7 and 0 <= y <= 7 \
            and (board[x][y] is None \
                or (isinstance(board[x][y], Piece) \
                    and board[x][y].get_color() is not self.color)): # \
            # and not self.would_be_in_check(x, y, board):
                move_list.append(((self.x, self.y), (x, y)))
        # if not self.has_moved:
        #     if type(board[self.x][7]) is Rook and not board[self.x][7].has_moved \
        #     and all([board[self.x][y] == None for y in range(self.y + 1, 7)]):
        #         move_list.append(((self.x, self.y), (self.x, 6), board[self.x][7]))
        #     if type(board[self.x][0]) is Rook and not board[self.x][0].has_moved \
        #     and all([board[self.x][y] == None for y in range(self.y - 1, 0, -1)]):\
        #         move_list.append(((self.x, self.y), (self.x, 2), board[self.x][0]))
        return move_list
#
    def in_check(self, board):
        return would_be_in_check(self.x, self.y, board)
#
    def would_be_in_check(self, x, y, board):
        old_x, old_y = self.x, self.y
        old_piece = board[x][y]
        board[self.x][self.y] = None
        board[x][y] = self
        self.x, self.y = x, y
#
        ells = self.get_Ls(board)
        for x_check, y_check in ells:
            if type(board[x_check][y_check]) == Knight \
            and board[x_check][y_check].get_color() is not self.color:
                self.x, self.y = old_x, old_y
                board[x][y] = old_piece
                board[self.x][self.y] = self
                return True
#
        hzns = [end_point[-1] for end_point in self.get_horizontals(board) if len(end_point) > 0]
        print(hzns)
        for x_check, y_check in hzns:
            if type(board[x_check][y_check]) in (Rook, Queen) \
            and board[x_check][y_check].get_color() is not self.color:
                self.x, self.y = old_x, old_y
                board[x][y] = old_piece
                board[self.x][self.y] = self
                return True
#
        diags = [end_point[-1] for end_point in self.get_diagonals(board) if len(end_point) > 0]
        for x_check, y_check in diags:
            if type(board[x_check][y_check]) in (Bishop, Queen) \
            and board[x_check][y_check].get_color() is not self.color:
                self.x, self.y = old_x, old_y
                board[x][y] = old_piece
                board[self.x][self.y] = self
                return True
#
        pawn_attacks = ((-1, 1), (1, 1), (1, -1), (-1, -1))
        for x_offset, y_offset in pawn_attacks:
            x_check, y_check = self.x + x_offset, self.y + y_offset
            if 0 <= x_check <= 7 and 0 <= y_check <= 7 \
            and type(board[x_check][y_check]) is Pawn \
            and board[x_check][y_check].get_color() is not self.color \
            and x_check + board[x_check][y_check].gravity == x:
                self.x, self.y = old_x, old_y
                board[x][y] = old_piece
                board[self.x][self.y] = self
                return True
#
        king_attacks = ((-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1))
        for x_offset, y_offset in king_attacks:
            x_check, y_check = self.x + x_offset, self.y + y_offset
            if 0 <= x_check <= 7 and 0 <= y_check <= 7 \
            and type(board[x_check][y_check]) is King \
            and board[x_check][y_check].get_color() is not self.color:
                self.x, self.y = old_x, old_y
                board[x][y] = old_piece
                board[self.x][self.y] = self
                return True
#
        return False
#
    def get_modifier(self, board):
        return (-0.5 if self.has_moved else 0) + (1 if self.has_castled else 0)
#
    def get_char(self):
        return 'K' if self.color is WHITE else 'k'

class Queen(Piece):
    def get_move_list(self, board):
        return [((self.x, self.y), (x, y)) for d_h in self.get_diagonals(board) + self.get_horizontals(board) for x, y in d_h]
#
    def get_char(self):
        return 'Q' if self.color is WHITE else 'q'

class Rook(Piece):
    def __init__(self, x, y, color):
        super(Rook, self).__init__(x, y, color)
        self.has_moved = False
#
    def get_move_list(self, board):
        return [((self.x, self.y), (x, y)) for h in self.get_horizontals(board) for x, y in h]
#
    def get_modifier(self, board):
        return 0.2 if not self.has_moved else 0
#
    def get_char(self):
        return 'R' if self.color is WHITE else 'r'

class Bishop(Piece):
    def get_move_list(self, board):
        return [((self.x, self.y), (x, y)) for d in self.get_diagonals(board) for x, y in d]
#
    def get_char(self):
        return 'B' if self.color is WHITE else 'b'

class Knight(Piece):
    def get_move_list(self, board):
        return [((self.x, self.y), (x, y)) for x, y in self.get_Ls(board)]
#
    def get_char(self):
        return 'N' if self.color is WHITE else 'n'


if __name__ == "__main__":
    g = Game()
    g.print_board(1)
    g.play_against_best_move(depth=3)
    # g.make_best_move(depth=3)


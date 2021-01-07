from collections import defaultdict
import random
import sys


def mirror(state):
    return tuple(
        tuple(
            state[i][len(row) - j - 1]
            for j, n in enumerate(row)
        )
        for i, row in enumerate(state)
    )

def rotate(state):
    return tuple(
        tuple(
            state[len(row) - j - 1][i]
            for j, n in enumerate(row)
        )
        for i, row in enumerate(state)
    )

# Normalize states to optimize for isomorphic symmetry
def norm(state):
    rotate1 = rotate(state)
    rotate2 = rotate(rotate1)
    rotate3 = rotate(rotate2)
    mirror0 = mirror(state)
    mirror1 = mirror(rotate1)
    mirror2 = mirror(rotate2)
    mirror3 = mirror(rotate3)
    return min(
        state, rotate1, rotate2, rotate3,
        mirror0, mirror1, mirror2, mirror3,
    )

# Create a state with pieces removed from the given positions
def fork(state, positions):
    return norm(tuple(
        tuple(
            0 if (i, j) in positions else n
            for j, n in enumerate(row)
        )
        for i, row in enumerate(state)
    ))

row_names = 'ABCD'
column_names = '1234'

# Get all valid moves from a state
def play(state):
    plays = set()
    for i, row in enumerate(state):
        for j, n in enumerate(row):
            k = 0
            positions = []
            while j + k < len(row) and state[i][j + k]:
                positions.append((i, j + k))
                s = fork(state, positions)
                if s not in plays:
                    m = row_names[i] + column_names[j]
                    if k:
                        m += column_names[j + k]
                    yield m, s
                plays.add(s)
                k += 1
            k = 0
            positions = []
            while i + k < len(state) and state[i + k][j]:
                positions.append((i + k, j))
                s = fork(state, positions)
                if s not in plays:
                    m = row_names[i]
                    if k:
                        m += row_names[i + k]
                    m += column_names[j]
                    yield m, s
                plays.add(s)
                k += 1
    return plays

class Game:
    size = 4
    def __init__(self):
        # Build the stating state
        initial_state = tuple(
            tuple(1 for _ in range(self.size))
            for _ in range(self.size)
        )

        # Build a bidirectional graph of moves
        self.moves = defaultdict(set)
        self.seeds = defaultdict(set)
        new = set([norm(initial_state)])
        while new:
            buds = set()
            for state in new:
                for _, move in play(state):
                    self.moves[state].add(move)
                    self.seeds[move].add(state)
                    buds.add(move)
            new = buds - self.moves.keys()
    
    def winning_states(self):
        # Normalize the winning states
        return set([
            norm(tuple(
                tuple(
                    1 if i == x and j == y else 0
                    for i in range(self.size)
                )
                for j in range(self.size)
            ))
            for x in range(self.size)
            for y in range(self.size)
        ])

    def solve(self):
        winning = self.winning_states()
        # Find moves that give the opponent no winning moves
        perfect = winning.copy()
        while perfect:
            raw = set(
                seed
                for state in perfect
                for move in self.seeds[state]
                for seed in self.seeds[move]
            )
            filtered = set(
                seed for seed in raw
                if not self.moves[seed] & winning
            )
            perfect = [
                seed
                for seed in filtered
                if not self.moves[seed] & filtered
            ]
            winning.update(perfect)
        return winning

print('Enumerating states...')
game = Game()

print('Solving...')
winning = game.solve()

row_map = {v: i for i, v in enumerate(row_names)}
column_map = {v: i for i, v in enumerate(column_names)}
def parse_move(move):
    y = row_map[move[0]]
    # Single piece
    if len(move) == 2:
        return [[y, column_map[move[1]]]]
    z = column_map[move[2]]
    pieces = []
    # Horizontal pieces
    if move[1] in row_map:
        x = y
        while x <= row_map[move[1]]:
            pieces.append([x, z])
            x += 1
    # Vertical pieces
    else:
        x = column_map[move[1]]
        while x <= z:
            pieces.append([y, x])
            x += 1
    return pieces

def parse(history):
    board = [[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1]]
    for move in map(parse_move, history):
        for x, y in move:
            board[x][y] = 0
    return board

def bot(history):
    board = parse(history)
    moves = dict(play(board))
    if not moves:
        return (None, 'You lost')
    winning_moves = [(move, state) for move, state in moves.items() if state in winning]
    if not winning_moves:
        winning_moves = moves.items()
    move, state = random.sample(winning_moves, 1)[0]
    if state == ((0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0)):
        return (move, 'You won')
    return (move, 'Your turn')

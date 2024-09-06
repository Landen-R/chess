import pygame
import chess
import chess.engine
import random

# Initialize Pygame
pygame.init()

# Constants
BOARD_SIZE = 640
SQUARE_SIZE = BOARD_SIZE // 8
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
HIGHLIGHT_COLOR = (0, 255, 0)
FONT_COLOR = (255, 255, 255)
TEXT_BOX_HEIGHT = 50

# Fonts
FONT = pygame.font.SysFont('Arial', 24)

# Load chess pieces (make sure these images are in the 'assets/' folder)
PIECES = {
    'p': pygame.image.load('Chess_pdt60.png'),  # Black pawn
    'P': pygame.image.load('Chess_plt60.png'),  # White pawn
    'r': pygame.image.load('Chess_rdt60.png'),  # Black rook
    'R': pygame.image.load('Chess_rlt60.png'),  # White rook
    'n': pygame.image.load('Chess_ndt60.png'),  # Black knight
    'N': pygame.image.load('Chess_nlt60.png'),  # White knight
    'b': pygame.image.load('Chess_bdt60.png'),  # Black bishop
    'B': pygame.image.load('Chess_blt60.png'),  # White bishop
    'q': pygame.image.load('Chess_qdt60.png'),  # Black queen
    'Q': pygame.image.load('Chess_qlt60.png'),  # White queen
    'k': pygame.image.load('Chess_kdt60.png'),  # Black king
    'K': pygame.image.load('Chess_klt60.png'),  # White king
}

# Create the display
screen = pygame.display.set_mode((BOARD_SIZE, BOARD_SIZE + TEXT_BOX_HEIGHT))
pygame.display.set_caption("Chess Game")

# Draw the board and pieces
def draw_board(display_screen, board, selected_square=None):
    for row in range(8):
        for col in range(8):
            color = WHITE if (row + col) % 2 == 0 else BLACK
            pygame.draw.rect(display_screen, color, pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

            # Highlight the selected square
            if selected_square == (row, col):
                pygame.draw.rect(display_screen, HIGHLIGHT_COLOR, pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)

    for row in range(8):
        for col in range(8):
            piece = board.piece_at(row * 8 + col)
            if piece:
                piece_symbol = piece.symbol()
                display_screen.blit(PIECES[piece_symbol], (col * SQUARE_SIZE, row * SQUARE_SIZE))

# Display text info (for moves or player turn)
def display_info(display_screen, message):
    pygame.draw.rect(display_screen, BLACK, pygame.Rect(0, BOARD_SIZE, BOARD_SIZE, TEXT_BOX_HEIGHT))  # Draw text box background
    text = FONT.render(message, True, FONT_COLOR)
    display_screen.blit(text, (10, BOARD_SIZE + 10))  # Draw the text

class ChessAI:
    def __init__(self, level, engine_path="C:/Users/lande/Downloads/stockfish-windows-x86-64-avx2/stockfish/stockfish-windows-x86-64-avx2.exe"):
        self.level = level
        self.engine = chess.engine.SimpleEngine.popen_uci(engine_path)

    def make_move(self, board):
        if self.level == 'easy':
            return self.random_move(board)
        elif self.level == 'medium':
            return self.stockfish_move(board, depth=10)
        elif self.level == 'hard':
            return self.stockfish_move(board, depth=20)

    @staticmethod
    def random_move(board):
        legal_moves = list(board.legal_moves)
        return random.choice(legal_moves)

    def stockfish_move(self, board, depth=10):
        result = self.engine.play(board, chess.engine.Limit(depth=depth))
        return result.move

    def get_hint(self, board):
        # Get the best move for the player as a hint
        result = self.engine.play(board, chess.engine.Limit(time=0.1))  # Faster hint
        return result.move

    def close_engine(self):
        self.engine.quit()

# Save the game
def save_game(board):
    with open('saved_game.txt', 'w') as f:
        f.write(board.fen())

# Load the game
def load_game():
    with open('saved_game.txt', 'r') as f:
        fen = f.read()
    board = chess.Board(fen)
    return board

def main():
    board = chess.Board()
    ai = ChessAI('medium')

    running = True
    selected_square = None
    player_turn = True  # True for player, False for AI
    last_move = None  # To display last move (player or AI)
    show_hint = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Mouse click to move piece
            if event.type == pygame.MOUSEBUTTONDOWN:
                if player_turn:
                    x, y = pygame.mouse.get_pos()
                    col = x // SQUARE_SIZE
                    row = y // SQUARE_SIZE
                    square = row * 8 + col
                    if selected_square is None and board.piece_at(square):
                        selected_square = square
                    elif selected_square is not None:
                        move = chess.Move(selected_square, square)
                        # Validate the move before pushing
                        if move in board.legal_moves:
                            board.push(move)
                            last_move = board.peek().uci()  # Store UCI format to avoid issues
                            player_turn = False
                        else:
                            display_info(screen, "Invalid move. Try again.")
                        selected_square = None

            # Press 'H' for a hint
            if event.type == pygame.KEYDOWN and event.key == pygame.K_h:
                show_hint = True  # Request hint

            # Press 'U' for undo
            if event.type == pygame.KEYDOWN and event.key == pygame.K_u:
                if len(board.move_stack) > 0:
                    board.pop()  # Undo the last move

        # AI move
        if not player_turn and not board.is_game_over():
            ai_move = ai.make_move(board)
            board.push(ai_move)
            last_move = board.peek().uci()  # Store AI's move
            player_turn = True

        # Check for check, checkmate, or stalemate
        if board.is_checkmate():
            display_info(screen, "Checkmate!")
            running = False  # End the game
        elif board.is_stalemate():
            display_info(screen, "Stalemate!")
            running = False  # End the game
        elif board.is_check():
            display_info(screen, "Check!")
        else:
            # Show the last move
            display_info(screen, f"Last move: {last_move}")

        # Draw the board and show selected pieces
        draw_board(screen, board, selected_square)

        # Show hint if requested
        if show_hint:
            hint_move = ai.get_hint(board)
            hint_san = hint_move.uci()
            display_info(screen, f"Hint: {hint_san}")
            show_hint = False

        pygame.display.flip()

    ai.close_engine()
    pygame.quit()

if __name__ == "__main__":
    main()

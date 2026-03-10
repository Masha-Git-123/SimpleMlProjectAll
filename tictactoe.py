import numpy as np
import cv2

class TicTacToe:
    def __init__(self):
        self.board = np.zeros((3, 3), dtype=int)  # 0 = empty, 1 = X, -1 = O
        self.current_player = 1  # X starts first
        self.winner = None
        self.game_over = False

    def make_move(self, row, col):
        if self.board[row, col] == 0 and not self.game_over:
            self.board[row, col] = self.current_player
            self.check_winner()
            self.current_player *= -1  # Switch player
            return True
        return False

    def check_winner(self):
        for i in range(3):
            # Check rows and columns
            if abs(sum(self.board[i, :])) == 3:
                self.winner = self.board[i, 0]
                self.game_over = True
            if abs(sum(self.board[:, i])) == 3:
                self.winner = self.board[0, i]
                self.game_over = True
        # Check diagonals
        if abs(self.board[0, 0] + self.board[1, 1] + self.board[2, 2]) == 3:
            self.winner = self.board[0, 0]
            self.game_over = True
        if abs(self.board[0, 2] + self.board[1, 1] + self.board[2, 0]) == 3:
            self.winner = self.board[0, 2]
            self.game_over = True
        # Check for draw
        if not self.game_over and not np.any(self.board == 0):
            self.winner = 0
            self.game_over = True

    def draw_board(self, frame):
        height, width, _ = frame.shape
        cell_width = width // 3
        cell_height = height // 3

        # Draw grid
        for i in range(1, 3):
            cv2.line(frame, (0, i * cell_height), (width, i * cell_height), (255, 255, 255), 2)
            cv2.line(frame, (i * cell_width, 0), (i * cell_width, height), (255, 255, 255), 2)

        # Draw marks
        for i in range(3):
            for j in range(3):
                center_x = j * cell_width + cell_width // 2
                center_y = i * cell_height + cell_height // 2
                if self.board[i, j] == 1:  # X
                    cv2.line(frame, (center_x - 40, center_y - 40), (center_x + 40, center_y + 40), (255, 0, 0), 5)
                    cv2.line(frame, (center_x + 40, center_y - 40), (center_x - 40, center_y + 40), (255, 0, 0), 5)
                elif self.board[i, j] == -1:  # O
                    cv2.circle(frame, (center_x, center_y), 40, (0, 255, 0), 5)

        # Show result
        if self.game_over:
            if self.winner == 1:
                text = "X Wins!"
            elif self.winner == -1:
                text = "O Wins!"
            else:
                text = "Draw!"
            cv2.putText(frame, text, (width // 4, height // 2),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 255), 4)

        return frame

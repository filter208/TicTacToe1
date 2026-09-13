from __future__ import annotations

import re


class TicTacToe:
    BOARD_SIZE = 3
    EMPTY = " "
    PLAYERS = ("X", "O")
    INPUT_PATTERN = re.compile(r"^\s*([1-3])\s*[,/ ]\s*([1-3])\s*$")

    def __init__(self):
        self.board: list[list[str]] = []
        self.current_player = "X"
        self.game_over = False
        self.reset()

    def reset(self) -> None:
        """开始一局空棋盘。"""
        self.board = [[self.EMPTY for _ in range(self.BOARD_SIZE)] for _ in range(self.BOARD_SIZE)]
        self.current_player = "X"
        self.game_over = False

    def board_as_text(self) -> str:
        """返回与旧版 print_board 相同格式的棋盘文本。"""
        lines = []
        for index, row in enumerate(self.board):
            lines.append("|".join(row))
            if index < self.BOARD_SIZE - 1:
                lines.append("-" * 5)
        return "\n".join(lines) + "\n"

    def print_board(self) -> None:
        print(self.board_as_text(), end="")

    def validate_input(self, input_str):
        """把 '2,3'、'2/3' 或 '2 3' 转成从零开始的坐标。"""
        if not isinstance(input_str, str):
            return None
        match = self.INPUT_PATTERN.match(input_str)
        if not match:
            return None
        row, col = (int(value) - 1 for value in match.groups())
        return (row, col) if 0 <= row < self.BOARD_SIZE and 0 <= col < self.BOARD_SIZE else None

    def check_winner(self):
        lines = [
            *self.board,
            *[[self.board[row][col] for row in range(self.BOARD_SIZE)] for col in range(self.BOARD_SIZE)],
            [self.board[index][index] for index in range(self.BOARD_SIZE)],
            [self.board[index][self.BOARD_SIZE - 1 - index] for index in range(self.BOARD_SIZE)],
        ]
        for line in lines:
            if line[0] != self.EMPTY and all(cell == line[0] for cell in line):
                return line[0]
        return None

    def check_draw(self) -> bool:
        return self.check_winner() is None and all(self.EMPTY not in row for row in self.board)

    def _valid_coordinates(self, row, col) -> bool:
        return (
            isinstance(row, int) and not isinstance(row, bool)
            and isinstance(col, int) and not isinstance(col, bool)
            and 0 <= row < self.BOARD_SIZE and 0 <= col < self.BOARD_SIZE
        )

    def make_move(self, row, col) -> bool:
        """保留旧版接口：成功落子返回 True，其他情况返回 False。"""
        if self.game_over or not self._valid_coordinates(row, col):
            return False
        if self.board[row][col] != self.EMPTY:
            return False
        self.board[row][col] = self.current_player
        return True

    def run(self) -> None:
        print("欢迎来到井字棋游戏！输入行列号（1-3），格式如：1,3")
        print("------------------------------------------")
        while not self.game_over:
            self.print_board()
            print(f"玩家 {self.current_player} 的回合，请输入行列号：")
            raw = input().strip()
            if raw.lower() == "help":
                print("输入规则：行号和列号用逗号/斜杠/空格分隔（例如：2,3 或 1 2）")
                continue
            position = self.validate_input(raw)
            if position is None:
                print("无效输入！请重新输入（示例：1,3）")
                continue
            if not self.make_move(*position):
                print("该位置已被占用，请重新选择！")
                continue
            winner = self.check_winner()
            if winner:
                self.print_board()
                print(f"玩家 {winner} 获胜！")
                self.game_over = True
            elif self.check_draw():
                self.print_board()
                print("游戏结束，平局！")
                self.game_over = True
            else:
                self.current_player = "O" if self.current_player == "X" else "X"


if __name__ == "__main__":
    TicTacToe().run()

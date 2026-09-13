from __future__ import annotations

import re
from typing import Callable, Optional


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
        self.board = [[self.EMPTY for _ in range(self.BOARD_SIZE)] for _ in range(self.BOARD_SIZE)]
        self.current_player, self.game_over = "X", False

    new_game = reset

    def board_as_text(self) -> str:
        lines = []
        for index, row in enumerate(self.board):
            lines.append("|".join(row))
            if index < self.BOARD_SIZE - 1:
                lines.append("-" * 5)
        return "\n".join(lines) + "\n"

    def print_board(self) -> None:
        print(self.board_as_text(), end="")

    def print_board_to(self, output_fn: Callable[[str], None]) -> None:
        for line in self.board_as_text().splitlines():
            output_fn(line)

    def validate_input(self, input_str):
        if not isinstance(input_str, str):
            return None
        match = self.INPUT_PATTERN.match(input_str)
        if not match:
            return None
        row, col = (int(value) - 1 for value in match.groups())
        return (row, col) if 0 <= row < self.BOARD_SIZE and 0 <= col < self.BOARD_SIZE else None

    def available_moves(self) -> list[tuple[int, int]]:
        return [(row, col) for row in range(3) for col in range(3) if self.board[row][col] == self.EMPTY]

    def _valid_coordinates(self, row, col) -> bool:
        return (isinstance(row, int) and not isinstance(row, bool) and isinstance(col, int)
                and not isinstance(col, bool) and 0 <= row < 3 and 0 <= col < 3)

    def make_move(self, row, col) -> bool:
        """兼容步骤 1：仅落子，不自动切换玩家。"""
        if self.game_over or not self._valid_coordinates(row, col) or self.board[row][col] != self.EMPTY:
            return False
        self.board[row][col] = self.current_player
        return True

    def _winner_for_board(self, board):
        lines = [*board, *[[board[row][col] for row in range(3)] for col in range(3)],
                 [board[i][i] for i in range(3)], [board[i][2 - i] for i in range(3)]]
        return next((line[0] for line in lines if line[0] != self.EMPTY and all(cell == line[0] for cell in line)), None)

    def check_winner(self):
        return self._winner_for_board(self.board)

    def check_draw(self) -> bool:
        return self.check_winner() is None and not self.available_moves()

    def status(self) -> dict[str, object]:
        winner = self.check_winner()
        if winner:
            return {"state": "won", "winner": winner}
        if self.check_draw():
            return {"state": "draw", "winner": None}
        return {"state": "playing", "winner": None}

    def play_move(self, row, col) -> dict[str, object]:
        """执行完整回合；返回机器可断言的结果，而不依赖 print。"""
        if self.game_over:
            return {"ok": False, "reason": "game_over", "status": self.status()}
        if not self._valid_coordinates(row, col):
            return {"ok": False, "reason": "out_of_range", "status": self.status()}
        if self.board[row][col] != self.EMPTY:
            return {"ok": False, "reason": "occupied", "status": self.status()}
        player = self.current_player
        self.make_move(row, col)
        result = self.status()
        if result["state"] == "playing":
            self.current_player = "O" if player == "X" else "X"
        else:
            self.game_over = True
        return {"ok": True, "row": row, "col": col, "player": player, "status": result}

    def run(self, input_fn: Optional[Callable[[], str]] = None, output_fn: Optional[Callable[[str], None]] = None) -> str:
        """仍能直接交互；注入输入输出后可自动化测试。"""
        input_fn, output_fn = input_fn or input, output_fn or print
        output_fn("欢迎来到井字棋游戏！输入行列号（1-3），格式如：1,3")
        while True:
            self.print_board_to(output_fn)
            if self.game_over:
                winner = self.check_winner()
                output_fn(f"玩家 {winner} 获胜！" if winner else "游戏结束，平局！")
                return "finished"
            output_fn(f"玩家 {self.current_player} 的回合，请输入行列号：")
            try:
                raw = input_fn().strip()
            except (EOFError, StopIteration):
                return "eof"
            if raw.lower() == "help":
                output_fn("输入规则：例如 2,3 或 1 2")
                continue
            position = self.validate_input(raw)
            if position is None:
                output_fn("无效输入！请重新输入（示例：1,3）")
                continue
            result = self.play_move(*position)
            if not result["ok"]:
                output_fn("该位置已被占用，请重新选择！")


if __name__ == "__main__":
    TicTacToe().run()

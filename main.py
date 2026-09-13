from __future__ import annotations

import re
from typing import Callable, Optional


class TicTacToe:
    BOARD_SIZE = 3
    EMPTY = " "
    PLAYERS = ("X", "O")
    INPUT_PATTERN = re.compile(r"^\s*([1-3])\s*[,/ ]\s*([1-3])\s*$")

    def __init__(self, allow_undo: bool = True):
        self.allow_undo = bool(allow_undo)
        self.scores = {"X": 0, "O": 0, "draws": 0}
        self.board: list[list[str]] = []
        self.current_player = "X"
        self.game_over = False
        self.winner: Optional[str] = None
        self.draw = False
        self.move_history: list[dict[str, int | str]] = []
        self._scored_result: Optional[str] = None
        self.reset(keep_scores=True)

    def reset(self, keep_scores: bool = True) -> None:
        self.board = [[self.EMPTY for _ in range(3)] for _ in range(3)]
        self.current_player, self.game_over = "X", False
        self.winner, self.draw, self.move_history, self._scored_result = None, False, [], None
        if not keep_scores:
            self.scores = {"X": 0, "O": 0, "draws": 0}

    new_game = reset

    def board_as_text(self) -> str:
        lines = []
        for index, row in enumerate(self.board):
            lines.append("|".join(row))
            if index < 2:
                lines.append("-" * 5)
        return "\n".join(lines) + "\n"

    def print_board(self) -> None:
        print(self.board_as_text(), end="")

    def print_board_to(self, output_fn: Callable[[str], None]) -> None:
        for line in self.board_as_text().splitlines():
            output_fn(line)

    def validate_input(self, input_str):
        if not isinstance(input_str, str): return None
        match = self.INPUT_PATTERN.match(input_str)
        if not match: return None
        row, col = (int(value) - 1 for value in match.groups())
        return (row, col) if self._valid_coordinates(row, col) else None

    def parse_command(self, command: str):
        if not isinstance(command, str) or not command.strip(): return "invalid", None
        text = command.strip()
        position = self.validate_input(text)
        if position is not None: return "move", position
        name = text.lower()
        return {"h": ("help", None), "help": ("help", None), "u": ("undo", None), "undo": ("undo", None),
                "stats": ("stats", None), "score": ("stats", None), "new": ("new", None),
                "reset": ("new", None), "q": ("quit", None), "quit": ("quit", None), "exit": ("quit", None)}.get(name, ("invalid", None))

    def available_moves(self) -> list[tuple[int, int]]:
        return [(r, c) for r in range(3) for c in range(3) if self.board[r][c] == self.EMPTY]

    def _valid_coordinates(self, row, col) -> bool:
        return (isinstance(row, int) and not isinstance(row, bool) and isinstance(col, int) and not isinstance(col, bool)
                and 0 <= row < 3 and 0 <= col < 3)

    def make_move(self, row, col) -> bool:
        if self.game_over or not self._valid_coordinates(row, col) or self.board[row][col] != self.EMPTY: return False
        self.board[row][col] = self.current_player
        self.move_history.append({"row": row, "col": col, "player": self.current_player})
        return True

    def check_winner(self):
        lines = [*self.board, *[[self.board[r][c] for r in range(3)] for c in range(3)],
                 [self.board[i][i] for i in range(3)], [self.board[i][2-i] for i in range(3)]]
        return next((line[0] for line in lines if line[0] != self.EMPTY and all(cell == line[0] for cell in line)), None)

    def check_draw(self) -> bool:
        return self.check_winner() is None and not self.available_moves()

    def status(self) -> dict[str, object]:
        winner = self.check_winner()
        if winner: return {"state": "won", "winner": winner}
        if self.check_draw(): return {"state": "draw", "winner": None}
        return {"state": "playing", "winner": None}

    def _update_terminal_state(self) -> dict[str, object]:
        result = self.status()
        if result["state"] == "won":
            self.game_over, self.winner, self.draw = True, result["winner"], False
            if self._scored_result is None:
                self.scores[self.winner] += 1; self._scored_result = self.winner
        elif result["state"] == "draw":
            self.game_over, self.winner, self.draw = True, None, True
            if self._scored_result is None:
                self.scores["draws"] += 1; self._scored_result = "draw"
        return result

    def play_move(self, row, col) -> dict[str, object]:
        if self.game_over: return {"ok": False, "reason": "game_over", "status": self.status()}
        if not self._valid_coordinates(row, col): return {"ok": False, "reason": "out_of_range", "status": self.status()}
        if self.board[row][col] != self.EMPTY: return {"ok": False, "reason": "occupied", "status": self.status()}
        player = self.current_player
        self.make_move(row, col)
        result = self._update_terminal_state()
        if result["state"] == "playing": self.current_player = "O" if player == "X" else "X"
        return {"ok": True, "row": row, "col": col, "player": player, "status": result}

    def undo(self) -> bool:
        """撤回最后一步；若该步结束棋局，也同步撤回本局计分。"""
        if not self.allow_undo or not self.move_history: return False
        if self._scored_result is not None:
            self.scores["draws" if self._scored_result == "draw" else self._scored_result] -= 1
        move = self.move_history.pop()
        self.board[move["row"]][move["col"]] = self.EMPTY
        self.current_player = move["player"]
        self.game_over, self.winner, self.draw, self._scored_result = False, None, False, None
        return True

    def scoreboard(self) -> dict[str, int]: return dict(self.scores)
    def format_scoreboard(self) -> str: return f"X: {self.scores['X']} | O: {self.scores['O']} | 平局: {self.scores['draws']}"

    def run(self, input_fn: Optional[Callable[[], str]] = None, output_fn: Optional[Callable[[str], None]] = None) -> str:
        input_fn, output_fn = input_fn or input, output_fn or print
        output_fn("欢迎来到井字棋游戏！输入坐标，或输入 help 查看命令。")
        while True:
            self.print_board_to(output_fn)
            if self.game_over:
                output_fn("本局已结束；输入 new 开始下一局，undo 撤销，quit 退出。")
            else: output_fn(f"玩家 {self.current_player} 的回合，请输入行列号：")
            try: raw = input_fn()
            except (EOFError, StopIteration): return "eof"
            command, argument = self.parse_command(raw)
            if command == "move":
                result = self.play_move(*argument)
                if not result["ok"]: output_fn("该位置不可落子。")
            elif command == "undo": output_fn("已悔棋。" if self.undo() else "当前没有可悔棋的落子。")
            elif command == "stats": output_fn(self.format_scoreboard())
            elif command == "new": self.reset(keep_scores=True); output_fn("已开始新的一局。")
            elif command == "help": output_fn("坐标如 1,3；命令：undo、stats、new、quit")
            elif command == "quit": output_fn("已退出游戏。"); return "quit"
            else: output_fn("无效输入！输入 help 查看帮助。")


if __name__ == "__main__":
    TicTacToe().run()

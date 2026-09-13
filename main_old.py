import re


class TicTacToe:
    def __init__(self):
        self.board = [[' ' for _ in range(3)] for _ in range(3)]
        self.current_player = 'X'
        self.game_over = False

    def print_board(self):
        """打印当前棋盘状态"""
        for i, row in enumerate(self.board):
            print('|'.join(row))
            if i < 2:
                print('-' * 5)

    def validate_input(self, input_str):
        """验证输入格式有效性（严格正则校验版本）"""
        try:
            # 类型检查
            if not isinstance(input_str, str):
                return None

            # 正则匹配：允许单个分隔符（,/ 空格），严格限制数值范围
            pattern = r'^\s*([1-3])\s*[,/ ]\s*([1-3])\s*$'
            if not re.match(pattern, input_str):
                return None

            # 提取并转换数值，从1-3转换为0-2
            row = int(re.search(r'\d', input_str).group()) - 1
            col = int(re.search(r'\d(?=\D*$)', input_str).group()) - 1

            if 0 <= row <= 2 and 0 <= col <= 2:
                return row, col
            return None
        except (AttributeError, ValueError):
            return None

    def check_winner(self):
        """检查胜利条件"""
        # 检查行
        for row in self.board:
            if row[0] == row[1] == row[2] != ' ':
                return row[0]

        # 检查列
        for col in range(3):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] != ' ':
                return self.board[0][col]

        # 检查对角线
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != ' ':
            return self.board[0][0]
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != ' ':
            return self.board[0][2]

        return None

    def check_draw(self):
        """检查平局条件"""
        if self.check_winner() is not None:
            return False
        else:
            for row in self.board:
                if ' ' in row:
                    return False
            return True

    def make_move(self, row, col):
        """执行落子操作"""
        # 检查行号和列号是否在合法范围内
        if row < 0 or row > 2 or col < 0 or col > 2:
            return False
        if self.board[row][col] == ' ':
            self.board[row][col] = self.current_player
            return True
        return False

    def run(self):
        """主游戏循环"""
        print("欢迎来到井字棋游戏！输入行列号（1-3），格式如：1,3")
        print("------------------------------------------")

        while not self.game_over:
            self.print_board()
            print(f"玩家 {self.current_player} 的回合，请输入行列号：")

            # 输入处理
            input_str = input().strip()
            if input_str.lower() == 'help':
                print("输入规则：行号和列号用逗号/空格分隔（例如：2,3 或 1 2）")
                continue

            pos = self.validate_input(input_str)
            if not pos:
                print("无效输入！请重新输入（示例：1,3）")
                continue
            row, col = pos

            # 执行落子
            if not self.make_move(row, col):
                print("该位置已被占用，请重新选择！")
                continue

            # 胜负判定
            winner = self.check_winner()
            if winner:
                self.print_board()
                print(f"玩家 {winner} 获胜！")
                self.game_over = True
                break

            if self.check_draw():
                self.print_board()
                print("游戏结束，平局！")
                self.game_over = True
                break

            # 切换玩家
            self.current_player = 'O' if self.current_player == 'X' else 'X'


if __name__ == "__main__":
    game = TicTacToe()
    game.run()

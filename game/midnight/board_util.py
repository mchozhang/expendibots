#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
load board utility data, evaluate board
"""


class BoardUtil:
    """
    static utility methods or objects for Board
    """
    # stack score table
    stack_score_table = {2: 1, 3: 2.5, 4: 4.5, 5: 5, 6: 6}

    cardinal = dict()
    surround = dict()

    @staticmethod
    def initialize(data):
        """
        parse board-util-data.json which contains the adjacent cell data of every cell
        Args:
            data: json data from board-util-data.json
        """
        for pos, steps in data["cardinal"].items():
            BoardUtil.cardinal[eval(pos)] = dict()
            for step, cells in steps.items():
                BoardUtil.cardinal[eval(pos)][int(step)] = [eval(cell) for cell in cells]

        for pos, cells in data["surround"].items():
            BoardUtil.surround[eval(pos)] = [eval(cell) for cell in cells]

    @staticmethod
    def valid_pos(x, y):
        """
        (x, y) is in range (1, 8)
        """
        return -1 < x < 8 and -1 < y < 8

    @staticmethod
    def manhattan(x, y, x1, y1):
        return abs(x - x1) + abs(y - y1)

    @staticmethod
    def evaluate_round(pre_board, mid_board, post_board, own_action, opponent_action, colour):
        """
        evaluate the reward by comparing the board before and after both
        players(or one player and game ends) have took an action
        Args:
            pre_board: board before self takes an action
            mid_board: board after self takes an action
            post_board: board after opponent takes an action, None if game ends before taking action
            own_action: the action self takes
            opponent_action: the action opponent takes, None if game ends before taking action
            colour: own colour

        Returns:
            reward value
        """
        reward = 0

        # game ends with the last action
        if not post_board:
            post_board = mid_board

        reward += BoardUtil.token_diff_score(pre_board, mid_board, post_board, own_action, opponent_action)
        reward += BoardUtil.early_stack_score(post_board)
        reward += BoardUtil.vulnerable_score(post_board, own_action)
        reward += BoardUtil.partition_token_diff_score(post_board)

        return reward

    @staticmethod
    def token_diff_score(pre_board, mid_board, post_board, own_action, opponent_action):
        """
        calculate score by comparing the difference of the token number, stack number,
        opponent tokens/stacks killed, self tokens/stacks killed

        Returns:
            score
        """
        colour = pre_board.colour
        pre_own_token_num, _ = pre_board.own_token_cell_num()
        pre_opponent_token_num, _ = pre_board.opponent_token_cell_num()
        mid_own_token_num, _ = mid_board.own_token_cell_num()
        mid_opponent_token_num, _ = mid_board.opponent_token_cell_num()
        post_own_token_num, _ = post_board.own_token_cell_num()
        post_opponent_token_num, _ = post_board.opponent_token_cell_num()

        kill_token, dead_token, bonus = 0, 0, 0
        # opponent tokens killed by you
        if own_action[0] == "BOOM":
            kill_token = pre_opponent_token_num - mid_opponent_token_num
            dead_token = pre_own_token_num - mid_own_token_num

            # punish to unbenefited boom
            if dead_token >= kill_token and post_opponent_token_num >= post_own_token_num:
                bonus += dead_token - kill_token - 2

        # bonus of the end game
        if post_opponent_token_num == 0:
            if post_own_token_num == 0:
                # force to draw with 1 token remained
                if pre_own_token_num == 1 and pre_opponent_token_num > 1:
                    bonus += 5
                # force to draw with more than 1 token behind
                elif pre_own_token_num + 1 < pre_opponent_token_num:
                    bonus += 2.5
            else:
                # win bonus
                bonus += 5
        elif post_own_token_num == 0:
            # lose bonus
            bonus -= 5

        # own tokens died
        dead_token = pre_own_token_num - post_own_token_num
        score = kill_token - dead_token + bonus
        return score

    @staticmethod
    def early_stack_score(board):
        """
        give reward for forming new stacks and for cells in corners and borders
        Args:
            board: board object
        Returns:
            score
        """
        score = 0
        own_token_num, own_cell_num = board.own_token_cell_num()

        for cell in board.get_own_cells():
            if 1 < cell.n:
                n = cell.n if cell.n < 7 else 6
                score += BoardUtil.stack_score_table[n]
            # deduction for cornered cell
            if BoardUtil.is_cornered(cell):
                score -= 0.5
            if not BoardUtil.is_marginal(cell):
                score += 0.3
        return score / own_token_num

    @staticmethod
    def early_non_bottom_num(board):
        """
        get the number of tokens that are not in bottom row
        Args:
            board: board object
        Returns:
            number of tokens, return 0 if not early
        """
        # only in early stage
        if board.cost < 13:
            return sum([cell.n for cell in board.get_own_cells if cell.y != board.bottom_row])
        return 0

    @staticmethod
    def is_marginal(cell):
        """
        is a cell on the border
        Args:
            cell: cell object
        Returns:
            Boolean
        """
        return cell.x == 0 or cell.y == 0 or cell.x == 7 or cell.y == 7

    @staticmethod
    def own_marginal_token_num(board):
        """
        number of own token that are near the edge
        Args:
            board: board object
        Returns:
            marginal token number
        """
        return sum([c.n for c in board.board.values() if c.colour == board.colour and BoardUtil.is_marginal(c)])

    @staticmethod
    def is_cornered(cell):
        """
        is a cell at the corner
        Args:
            cell: cell object
        Returns:
            Boolean
        """
        return cell.pos == (0, 0) or cell.pos == (0, 7) or cell.pos == (7, 0) or cell.pos == (7, 7)

    @staticmethod
    def own_cornered_token_num(board):
        """
        number of own tokens that are in the corners
        Args:
            board: board object
        Returns:
            cornered token number
        """
        return sum([c.n for c in board.board.values() if c.colour == board.colour and BoardUtil.is_cornered(c)])

    @staticmethod
    def get_partitions(board, is_own):
        """
        get partitions that contain own(or opponent) cells,
        a partition is a group of connected cells that will boom together
        Args:
            board: board object
            is_own: own partitions or opponent partitions
        Returns:
            list of cell lists that contain all cells forming a partition
        """
        cells = board.get_own_cells() if is_own else board.get_opponent_cells()

        visited = set()
        partitions = []

        def recursive_search(x, y, part):
            """
            find all the cells that belong to a partition
            """
            part.append(board.board[(x, y)])
            visited.add((x, y))

            for (next_x, next_y) in BoardUtil.surround[(x, y)]:
                if (next_x, next_y) in board.board and (next_x, next_y) not in visited:
                    recursive_search(next_x, next_y, part)

        for cell in cells:
            partition = []
            if cell.pos not in visited:
                recursive_search(cell.x, cell.y, partition)
                partitions.append(partition)

        return partitions

    @staticmethod
    def max_partition_token_diff(partitions, colour):
        """
        calculate the maximum token difference of all own partitions
        Args:
            partitions: partition list
            colour: own color
        Returns:
            maximum token difference
        """
        max_num = 0
        for partition in partitions:
            own_num, opponent_num = 0, 0
            for cell in partition:
                if cell.colour == colour:
                    own_num += cell.n
                else:
                    opponent_num += cell.n

            num = opponent_num - own_num
            if num > max_num:
                max_num = num
        return max_num

    @staticmethod
    def partition_token_diff_score(board):
        own_partition = BoardUtil.get_partitions(board, True)
        own_partition_token_diff = BoardUtil.max_partition_token_diff(own_partition, board.colour)

        opponent_partition = BoardUtil.get_partitions(board, False)
        opponent_partition_token_diff = BoardUtil.max_partition_token_diff(opponent_partition, board.opponent_colour)
        return (own_partition_token_diff - opponent_partition_token_diff) / 2

    @staticmethod
    def vulnerable_spots(board, partitions, is_own):
        """
        find the spots that surround a partition and count their overlapping numbers
        Args:
            board: board object
            partitions: list of partitions
            is_own: is own partition
        Returns:
            counter of the vulnerable value of the spots
        """
        spots = dict()
        opponent_cells = board.get_opponent_cells() if is_own else board.get_own_cells()
        partition_colour = board.colour if is_own else board.opponent_colour

        # partitions that contain more main colour cells
        vulnerable_partitions = []
        for partition in partitions:
            count = len([cell for cell in partition if cell.colour == partition_colour])
            if count * 2 > len(partition):
                vulnerable_partitions.append(partition)

        # for each vulnerable partition,
        # find vulnerable spots and the opponent cells that can reach to them
        for partition in vulnerable_partitions:
            for cell in partition:
                for pos in BoardUtil.surround[cell.pos]:
                    if pos not in board.board:
                        if pos in spots:
                            spots[pos]["value"] += 1
                        else:
                            spot = {"value": 1, "reaches": []}
                            for oc in opponent_cells:
                                if oc not in partition and pos in BoardUtil.cardinal[oc.pos][oc.n]:
                                    spot["reaches"].append(pos)
                            spots[pos] = spot
        return spots

    @staticmethod
    def partition_vulnerability(spots):
        """
        maximum vulnerable value caused that the cells that can reach opponent's vulnerable spots
        Args:
            spots: partition vulnerable spots dictionary
        Returns:
            max vulnerable value
        """
        values = [spot["value"] for spot in spots.values() if spot["reaches"]]
        max_value = max(values) if values else 0
        # vulnerable values greater than 1 will be seen as vulnerability
        return max_value if max_value > 1 else 0

    @staticmethod
    def vulnerable_score(board, own_action):
        """
        score of own vulnerabilities and opponent vulnerabilities
        Args:
            board: board object
            own_action: action
        Returns:
            score
        """
        if own_action[0] == "MOVE":
            opponent_partitions = BoardUtil.get_partitions(board, False)
            opponent_vulnerable_spots = BoardUtil.vulnerable_spots(board, opponent_partitions, False)
            opponent_vulnerable_value = BoardUtil.partition_vulnerability(opponent_vulnerable_spots)

            own_partitions = BoardUtil.get_partitions(board, True)
            own_vulnerable_spots = BoardUtil.vulnerable_spots(board, own_partitions, True)
            own_vulnerable_value = BoardUtil.partition_vulnerability(own_vulnerable_spots)

            return (opponent_vulnerable_value - own_vulnerable_value) / 3
        return 0

    @staticmethod
    def average_vulnerable_value(spots, token_num):
        """
        average vulnerable value for every token
        Args:
            spots: counter of vulnerable spots
            token_num: token number
        Returns:
            value
        """
        values = sum([spot["value"] for spot in spots.values() if spot["value"] > 1])
        return values / token_num if token_num else 0

    @staticmethod
    def opponent_leftover_chasing(board, spots):
        """
        calculate the score of minimum distance between opponent's remain cells and your cells when having advantage
        Args:
            board: board object
            spots: opponent vulnerable spots
        Returns:
            chasing score
        """
        own_token_num, own_cell_num = board.own_token_cell_num()
        opponent_token_num, opponent_cell_num = board.opponent_token_cell_num()
        token_diff = own_token_num - opponent_token_num

        # chase when we have advantage
        if token_diff > 3 or (token_diff >= 0 and opponent_cell_num < 3):
            # only chase when we can't reach opponent's vulnerability
            for spot in spots.values():
                if spot["reaches"]:
                    return 0

            max_score = 0
            for cell in board.get_own_cells():
                for vul_pos in spots.keys():
                    dist = BoardUtil.board_distance(cell, vul_pos)
                    if dist == 0 and cell.n > 1:
                        score = 3 - cell.n / 3
                    else:
                        score = 3 / dist

                    if score > max_score:
                        max_score = score
            return max_score
        return 0

    @staticmethod
    def board_distance(cell, goal):
        """
        calculate the minimum steps for a stack to get to a goal cell
        Args:
            cell: start cell
            goal: goal position
        Returns:
            number of steps
        """
        goal_x, goal_y = goal[0], goal[1]
        x_dist = abs(cell.x - goal_x)
        y_dist = abs(cell.y - goal_y)
        if cell.n == 1:
            return x_dist + y_dist
        else:
            x_remain = 1 if x_dist % cell.n else 0
            y_remain = 1 if y_dist % cell.n else 0
            x_steps = x_dist // cell.n + x_remain
            y_steps = y_dist // cell.n + y_remain
            return x_steps + y_steps

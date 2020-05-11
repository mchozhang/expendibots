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
    MAX_STACK_SCORE = 3
    stack_score_table = {1: 0, 2: 0.4, 3: 1, 4: 1.8, 5: 2.5, 6: 3}

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
        reward += BoardUtil.stack_score(post_board)
        reward += BoardUtil.vulnerability_score(post_board, own_action)
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
    def stack_score(board):
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
            # get stack score from score table
            score += BoardUtil.stack_score_table.get(cell.n, BoardUtil.MAX_STACK_SCORE)

            # deduction for cornered cell
            if BoardUtil.is_cornered(cell):
                score -= 0.3
            # bonus for non-marginal cell
            if not BoardUtil.is_marginal(cell):
                score += 0.1
        return score / own_token_num if own_token_num else 0

    @staticmethod
    def average_stack_score(board):
        """
        average score for own stacks
        Args:
            board: board object
        Returns:
            float, average stack score value
        """
        cells = board.get_own_cells()

        if cells:
            return sum([BoardUtil.stack_score_table.get(cell.n, BoardUtil.MAX_STACK_SCORE) for cell in cells]) / len(
                cells)
        else:
            return 0

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
            return sum([cell.n for cell in board.get_own_cells() if cell.y != board.bottom_row])
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
    def partitions_and_vulnerable_spots(board, is_own):
        """
        get a list of partitions that contain own(or opponent) cells and
        a partition is a group of connected cells that will boom together,
        each partition item has the following structure
        {
          "cells": [],           # cells in partition
          "black": <black_cell_number>
          "white": <white_cell_number>
        }
        vul_spots has the following structure
        {
            (x, y): {
                "value": <vul_value>
                "reaches": []        # opponent cells that can reach this spot
                "black": <int>       # black token num that will be eliminated if boom here
                "white": <int>       # white token num that will be eliminated if boom here
            }
        }
        Args:
            board: board object
            is_own: own partitions or opponent partitions
        Returns:
            a tuple of
            list of partition items that contain at least one own(or opponent) cell,
            dictionary of vulnerable spots
        """
        cells = board.get_own_cells() if is_own else board.get_opponent_cells()
        opponent_cells = board.get_opponent_cells() if is_own else board.get_own_cells()
        own_colour = board.colour if is_own else board.opponent_colour
        opponent_colour = board.opponent_colour if is_own else board.colour

        visited = set()
        partitions = []
        vul_spots = dict()

        def recursive_search(pos, connected_list):
            """
            find all the cells that belong to a partition
            """
            current_cell = board.board[pos]
            connected_list.append(current_cell)
            visited.add(pos)

            for next_pos in BoardUtil.surround[pos]:
                if next_pos not in board.board:
                    # a vulnerable spot
                    if next_pos in vul_spots:
                        vul_spots[next_pos]["value"] += 1
                        vul_spots[next_pos][current_cell.colour] += 1
                    else:
                        spot = dict()
                        spot["value"] = 1
                        spot["reaches"] = []
                        if current_cell.colour == "white":
                            spot["white"] = 1
                            spot["black"] = 0
                        else:
                            spot["white"] = 0
                            spot["black"] = 1
                        vul_spots[next_pos] = spot
                elif next_pos not in visited:
                    # cell in partition
                    recursive_search(next_pos, connected_list)

        # find partitions
        for cell in cells:
            if cell.pos not in visited:
                partition = dict()
                partition_cells = []
                recursive_search(cell.pos, partition_cells)
                partition["cells"] = partition_cells
                partition["black"] = sum([cell.n for cell in partition_cells if cell.colour == "black"])
                partition["white"] = sum([cell.n for cell in partition_cells if cell.colour == "white"])
                partitions.append(partition)

        # find reachable opponent cells for partitions containing more own tokens
        for partition in partitions:
            if partition[own_colour] > partition[opponent_colour]:
                for pos, spot in vul_spots.items():
                    for oc in opponent_cells:
                        if oc not in partition and pos not in BoardUtil.cardinal[oc.pos][oc.n]:
                            spot["reaches"].append(oc)

        return partitions, vul_spots

    @staticmethod
    def max_partition_token_diff(partitions, colour):
        """
        calculate the maximum token difference of all own partitions,
        token-diff = opponent_num - own_num
        Args:
            partitions: partition list
            colour: own color
        Returns:
            maximum token difference
        """
        own_colour = colour
        opponent_colour = "black" if colour == "white" else "white"
        return max([p[opponent_colour] - p[own_colour] for p in partitions]) if partitions else 0

    @staticmethod
    def partition_token_diff_score(board):
        """
        reward for maximum token difference in partitions
        Args:
            board: board object
        Returns:
            score
        """
        own_partition, _ = BoardUtil.partitions_and_vulnerable_spots(board, True)
        own_partition_token_diff = BoardUtil.max_partition_token_diff(own_partition, board.colour)

        opponent_partition, _ = BoardUtil.partitions_and_vulnerable_spots(board, False)
        opponent_partition_token_diff = BoardUtil.max_partition_token_diff(opponent_partition, board.opponent_colour)
        return (own_partition_token_diff - opponent_partition_token_diff) / 2

    @staticmethod
    def max_vulnerability_score(spots, own_colour):
        """
        maximum vulnerable value caused that the cells that can reach opponent's vulnerable spots
        Args:
            spots: partition vulnerable spots dictionary
            own_colour: main partition colour
        Returns:
            max vulnerable value
        """
        opponent_colour = "white" if own_colour == "black" else "black"

        # probability for each max-vulnerability-value to successfully kill opponent tokens
        probability_table = {0: 0, 1: 0.3, 2: 0.7, 3: 0.8, 4: 0.9}

        # find max vulnerability score
        max_score = 0
        for pos, spot in spots.items():
            if spot["reaches"]:
                token_diff = spot[own_colour] - spot[opponent_colour] - min([c.n for c in spot["reaches"]])
                vul_value = spot["value"]
                score = token_diff * probability_table.get(vul_value, 0.9)

                if score > max_score:
                    max_score = score
        return max_score

    @staticmethod
    def vulnerability_score(board, own_action):
        """
        reward for own vulnerabilities and opponent vulnerabilities
        Args:
            board: board object
            own_action: action
        Returns:
            score
        """
        if own_action[0] == "MOVE":
            opponent_partitions, opponent_vul_spots = BoardUtil.partitions_and_vulnerable_spots(board, False)
            opponent_vulnerable_score = BoardUtil.max_vulnerability_score(opponent_vul_spots, board.opponent_colour)

            own_partitions, own_vul_spots = BoardUtil.partitions_and_vulnerable_spots(board, True)
            own_vulnerable_value = BoardUtil.max_vulnerability_score(own_vul_spots, board.colour)

            return (opponent_vulnerable_score - own_vulnerable_value) / 2
        return 0

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

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
load board utility data, evaluate board
"""


class BoardUtil:
    """
    static utility methods or objects for Board
    """

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
    def validPos(x, y):
        """
        (x, y) is in range (1, 8)
        """
        return -1 < x < 8 and -1 < y < 8


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
    if post_board:
        # game doesn't end
        reward += token_diff_score(pre_board, mid_board, post_board, own_action, opponent_action)
    else:
        # game ends with the last action
        reward += token_diff_score(pre_board, mid_board, mid_board, own_action, opponent_action)

    return reward


def token_diff_score(pre_board, mid_board, post_board, own_action, opponent_action):
    """
    calculate score by comparing the difference of the token number, stack number, 
    opponent tokens/stacks killed, self tokens/stacks killed 
    
    Returns:
        score
    """
    colour = pre_board.colour
    pre_black_token_num, _ = pre_board.black_token_cell_num()
    pre_white_token_num, _ = pre_board.white_token_cell_num()
    mid_black_token_num, _ = mid_board.black_token_cell_num()
    mid_white_token_num, _ = mid_board.white_token_cell_num()
    post_black_token_num, _ = post_board.black_token_cell_num()
    post_white_token_num, _ = post_board.white_token_cell_num()

    kill_token, die_token, bonus = 0, 0, 0
    # opponent tokens killed by you
    if own_action[0] == "BOOM":
        if colour == "white":
            kill_token = pre_black_token_num - mid_black_token_num
        else:
            kill_token = pre_white_token_num - mid_white_token_num

    # own tokens
    if colour == "white":
        if post_white_token_num == 0:
            bonus -= 10
        elif post_black_token_num == 0:
            bonus += 10

        die_token = pre_white_token_num - post_white_token_num
    else:
        if post_black_token_num == 0:
            bonus -= 10
        elif post_white_token_num == 0:
            bonus += 10

        die_token = pre_black_token_num - post_black_token_num

    score = kill_token - die_token + bonus
    return score


def marginal_num(board):
    """
    number of own cells that are near the edge
    Args:
        board: board object

    Returns:
        marginal cell number
    """
    cells = board.get_white_cells() if board.colour == "white" else board.get_black_cells()
    return len(list(filter(lambda cell: cell.x == 0 or cell.x == 7 or cell.y == 0 or cell.y == 7, cells)))


def get_own_partitions(board):
    """
    get partitions that contain own cells
    Args:
        board: board object
    Returns:
        list of partition set
    """
    cells = board.get_own_cells()
    visited = set()
    partitions = []

    def recursive_search(x, y, part):
        """
        find all the cells that belong to a partition
        """
        part.add(board.board[(x, y)])
        visited.add((x, y))

        for (next_x, next_y) in BoardUtil.surround[(x, y)]:
            if (next_x, next_y) in board.board and (next_x, next_y) not in visited:
                recursive_search(next_x, next_y, part)

    for cell in cells:
        partition = set()
        if cell.pos not in visited:
            recursive_search(cell.x, cell.y, partition)
            partitions.append(partition)

    return partitions

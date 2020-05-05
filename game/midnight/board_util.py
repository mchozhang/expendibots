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
    states = dict()

    @staticmethod
    def initialize(data, state_data=None):
        """
        parse board-util-data.json which contains the adjacent cell data of every cell
        Args:
            data: json data from board-util-data.json
            state_data: json data from board-state-data.json
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
            bonus -= 5
        elif post_black_token_num == 0:
            bonus += 5

        die_token = pre_white_token_num - post_white_token_num
    else:
        if post_black_token_num == 0:
            bonus -= 5
        elif post_white_token_num == 0:
            bonus += 5

        die_token = pre_black_token_num - post_black_token_num

    score = kill_token - die_token + bonus
    return score


def marginal_token_num(board):
    """
    number of own token that are near the edge
    Args:
        board: board object

    Returns:
        marginal token number
    """
    def is_marginal(cell):
        return cell.x == 0 or cell.y == 0 or cell.x == 7 or cell.y == 7

    return sum([cell.n for cell in board.board.values() if cell.colour == board.colour and is_marginal(cell)])


def cornered_token_num(board):
    """
    number of own tokens that are in the corners
    Args:
        board: board object
    Returns:
        cornered token number
    """
    def is_cornered(cell):
        return cell.pos == (0, 0) or cell.pos == (0, 7) or cell.pos == (7,0) or cell.pos == (7,7)

    return sum([cell.n for cell in board.board.values() if cell.colour == board.colour and is_cornered(cell)])


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


def partition_kill_rate(partitions, colour):
    """
    calculate the maximum kill rate(average number of opponents tokens killed by an own token)
    of all own partitions
    Args:
        partitions: partition list
        colour: own color
    Returns:
        kil rate, float
    """
    max_rate = 0
    for partition in partitions:
        own_num, opponent_num = 0, 0
        for cell in partition:
            if cell.colour == colour:
                own_num += cell.n
            else:
                opponent_num += cell.n

        rate = opponent_num // own_num
        if rate > max_rate:
            max_rate = rate

    return max_rate

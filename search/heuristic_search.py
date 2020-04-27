#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
heuristic search algorithm:
astar search, weighted astar search
"""

from queue import PriorityQueue


def astar_search(board):
    """
    A* algorithm
    Args:
        board: initial board

    Returns:
        solution board
    """
    queue = PriorityQueue()
    explored = set()

    queue.put((black_number_heuristic(board), board))
    explored.add(board)

    while not queue.empty():
        current = queue.get()[1]
        if len(current.get_black_cells()) == 0:
            return current

        for action in current.get_valid_actions():
            newNode = current.copy()
            newNode.take_action(action)
            if newNode not in explored:
                newNode.parent = current

                explored.add(newNode)
                priority = 10 * black_number_heuristic(newNode) + newNode.cost
                queue.put((priority, newNode))
    return None


def weighted_astar_search(board):
    """
    weighted A* algorithm, coefficient 10
    Args:
        board: initial board
    Returns:
        solution board
    """
    queue = PriorityQueue()
    explored = set()

    queue.put((black_number_heuristic(board), board))
    explored.add(board)

    while not queue.empty():
        current = queue.get()[1]
        if len(current.get_black_cells()) == 0:
            return current

        for action in current.get_valid_actions():
            new_node = current.copy()
            new_node.take_action(action)
            if new_node not in explored:
                new_node.parent = current

                explored.add(new_node)
                priority = 10 * black_number_heuristic(new_node) + new_node.cost
                queue.put((priority, new_node))
    return None


def black_number_heuristic(board):
    """
    number of the black cells remained
    """
    return len(board.get_black_cells())


astar = astar_search
wastar = weighted_astar_search

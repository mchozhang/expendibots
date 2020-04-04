#!/usr/bin/env python
# -*- coding: utf-8 -*-

from queue import PriorityQueue


def aStarSearch(board):
    """
    A* algorithm
    Args:
        board: initial board

    Returns:
        solution board
    """
    queue = PriorityQueue()
    explored = set()

    queue.put((blackNumberHeuristic(board), board))
    explored.add(board)

    while not queue.empty():
        current = queue.get()[1]
        if len(current.getBlackCells()) == 0:
            return current

        for action in current.getValidActions():
            newNode = current.copy()
            newNode.takeAction(action)
            if newNode not in explored:
                newNode.parent = current

                explored.add(newNode)
                priority = 10 * blackNumberHeuristic(newNode) + newNode.cost
                queue.put((priority, newNode))
    return None


def weightedAStarSearch(board):
    """
    weighted A* algorithm, coefficient 10
    Args:
        board: initial board
    Returns:
        solution board
    """
    queue = PriorityQueue()
    explored = set()

    queue.put((blackNumberHeuristic(board), board))
    explored.add(board)

    while not queue.empty():
        current = queue.get()[1]
        if len(current.getBlackCells()) == 0:
            return current

        for action in current.getValidActions():
            newNode = current.copy()
            newNode.takeAction(action)
            if newNode not in explored:
                newNode.parent = current

                explored.add(newNode)
                priority = 10 * blackNumberHeuristic(newNode) + newNode.cost
                queue.put((priority, newNode))
    return None


def blackNumberHeuristic(board):
    """
    number of the black cells remained
    """
    return len(board.getBlackCells())


astar = aStarSearch
wastar = weightedAStarSearch

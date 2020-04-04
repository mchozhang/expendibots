#!/usr/bin/env python
# -*- coding: utf-8 -*-
from queue import Queue


def depthFirstSearch(board):
    """
    depth first search
    Args:
        board: initial board
    Returns:
        solution board
    """
    stack = [board]
    explored = set()

    while stack:
        current = stack.pop()
        if len(current.getBlackCells()) == 0:
            return current

        explored.add(current)
        for action in current.getValidActions():
            newNode = current.copy()
            newNode.takeAction(action)

            if newNode not in explored:
                newNode.parent = current
                stack.append(newNode)
    return None


def breathFirstSearch(board):
    """
    breadth first search
    Args:
        board: initial board

    Returns:
        solution board
    """
    queue = Queue()
    explored = set()

    explored.add(board)
    queue.put(board)

    while queue:
        current = queue.get()
        if len(current.getBlackCells()) == 0:
            return current

        for action in current.getValidActions():
            newNode = current.copy()
            newNode.takeAction(action)

            if newNode not in explored:
                newNode.parent = current
                explored.add(newNode)
                queue.put(newNode)
    return None


dfs = depthFirstSearch
bfs = breathFirstSearch

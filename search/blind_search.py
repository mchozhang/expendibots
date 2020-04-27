#!/usr/bin/env python
# -*- coding: utf-8 -*-
from queue import Queue


def depth_first_search(board):
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
        if len(current.get_black_cells()) == 0:
            return current

        explored.add(current)
        for action in current.get_valid_actions():
            newNode = current.copy()
            newNode.take_action(action)

            if newNode not in explored:
                newNode.parent = current
                stack.append(newNode)
    return None


def breath_first_search(board):
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
        if len(current.get_black_cells()) == 0:
            return current

        for action in current.get_valid_actions():
            new_node = current.copy()
            new_node.take_action(action)

            if new_node not in explored:
                new_node.parent = current
                explored.add(new_node)
                queue.put(new_node)
    return None


dfs = depth_first_search
bfs = breath_first_search

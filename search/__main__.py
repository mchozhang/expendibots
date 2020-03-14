import sys
import json
from copy import deepcopy
from queue import Queue
from search.board import Board
from search.util import print_board, print_boom, print_move


def main():
    with open(sys.argv[1]) as file:
        data = json.load(file)
        board = Board(data)
        print_board(board.getBoardDict(), compact=False)
        result = depthFirstSearch(board)
        printSolution(result)


def depthFirstSearch(board):
    stack = [board]
    explored = set()

    while stack:
        current = stack.pop()
        if len(current.blackCells) == 0:
            return current

        explored.add(str(current))
        for action in current.getValidActions():
            newNode = deepcopy(current)
            newNode.takeAction(action)
            if str(newNode) not in explored:
                stack.append(newNode)
    return None


def breathFirstSearch(board):
    queue = Queue()
    queueSet = set()
    explored = set()

    queue.put(board)
    queueSet.add(str(board))

    while queue:
        current = queue.get()
        queueSet.remove(str(current))
        print(len(current.path))
        if len(current.blackCells) == 0:
            return current

        explored.add(str(current))
        for action in current.getValidActions():
            newNode = deepcopy(current)
            newNode.takeAction(action)

            if str(newNode) not in explored and str(newNode) not in queueSet:
                queue.put(newNode)
                queueSet.add(str(newNode))
    return None


def printSolution(board):
    """
    final state of the board which have found the solution
    """
    if not board:
        print("no solution.")

    for action in board.path:
        if action[0] == 0:
            print_boom(action[1], action[2])
        else:
            print_move(action[0], action[1], action[2], action[3], action[4])


if __name__ == '__main__':
    main()

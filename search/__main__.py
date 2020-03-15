import sys
import json
from copy import deepcopy
from queue import Queue, PriorityQueue
from search.board import Board
from search.util import print_board, print_boom, print_move
import time


def main():
    with open(sys.argv[1]) as file:
        data = json.load(file)
        board = Board(data)
        print_board(board.board, compact=False)
        result = astar(board)
        printSolution(result)


def depthFirstSearch(board):
    stack = [board]
    explored = set()

    while stack:
        current = stack.pop()
        if len(current.getBlackCells()) == 0:
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
    explored = set()

    explored.add(board)
    queue.put(board)

    while queue:
        current = queue.get()
        if len(current.getBlackCells()) == 0:
            return current

        for action in current.getValidActions():
            newNode = deepcopy(current)
            newNode.takeAction(action)
            if newNode not in explored:
                explored.add(newNode)
                queue.put(newNode)
    return None


def aStarSearch(board):
    queue = PriorityQueue()
    explored = set()

    queue.put((blackNumberHeuristic(board), board))
    explored.add(board)

    while not queue.empty():
        current = queue.get()[1]
        if len(current.getBlackCells()) == 0:
            return current

        for action in current.getValidActions():
            newNode = deepcopy(current)
            newNode.takeAction(action)
            if newNode not in explored:
                explored.add(newNode)
                priority = 3 * generalHeristic(newNode) + len(newNode.path)
                queue.put((priority, newNode))
    return None


def generalHeristic(board):
    return blackNumberHeuristic(board)


def blackNumberHeuristic(board):
    """
    number of the black cells remained
    """
    return len(board.getBlackCells())


def printSolution(board):
    """
    final state of the board which have found the solution
    """
    if board is None:
        print("# no solution.")
        return

    for action in board.path:
        if action[0] == 0:
            print_boom(action[1], action[2])
        else:
            print_move(action[0], action[1], action[2], action[3], action[4])


# abbreviation of searching
dfs = depthFirstSearch
bfs = breathFirstSearch
astar = aStarSearch

if __name__ == '__main__':
    start = time.time()
    main()
    print('#', time.time() - start)

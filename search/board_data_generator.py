#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pre-calculate all the valid adjacent cells of each cell
import json

if __name__ == "__main__":
    with open("board-data.json", "w") as boardFile:
        cardinal = dict()
        surround = dict()

        cardinalDirs = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        surroundDirs = [(1, -1), (1, 0), (1, 1), (0, 1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]

        for x in range(8):
            for y in range(8):
                cardinal[str((x, y))] = dict()
                accumulation = []
                for step in range(1, 8):
                    cardinal[str((x, y))][step] = accumulation.copy()
                    for dir in cardinalDirs:
                        nextX, nextY = x + dir[0] * step, y + dir[1] * step
                        if -1 < nextX < 8 and -1 < nextY < 8:
                            accumulation.append(str((nextX, nextY)))
                            cardinal[str((x, y))][step].append(str((nextX, nextY)))

                surround[str((x, y))] = []
                for dir in surroundDirs:
                    nextX, nextY = x + dir[0], y + dir[1]
                    if -1 < nextX < 8 and -1 < nextY < 8:
                        surround[str((x, y))].append(str((nextX, nextY)))

        boardData = dict()
        boardData["cardinal"] = cardinal
        boardData["surround"] = surround

        data = json.dumps(boardData)
        boardFile.write(data)
        boardFile.close()

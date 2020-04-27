#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
pre-calculate all the valid adjacent cells of each cell
"""
import json

if __name__ == "__main__":
    with open("board-data.json", "w") as board_file:
        cardinal = dict()
        surround = dict()

        cardinal_dirs = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        surround_dirs = [(1, -1), (1, 0), (1, 1), (0, 1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]

        for x in range(8):
            for y in range(8):
                cardinal[str((x, y))] = dict()
                accumulation = []
                for step in range(1, 8):
                    cardinal[str((x, y))][step] = accumulation.copy()
                    for direction in cardinal_dirs:
                        nextX, nextY = x + direction[0] * step, y + direction[1] * step
                        if -1 < nextX < 8 and -1 < nextY < 8:
                            accumulation.append(str((nextX, nextY)))
                            cardinal[str((x, y))][step].append(str((nextX, nextY)))

                surround[str((x, y))] = []
                for direction in surround_dirs:
                    nextX, nextY = x + direction[0], y + direction[1]
                    if -1 < nextX < 8 and -1 < nextY < 8:
                        surround[str((x, y))].append(str((nextX, nextY)))

        board_data = dict()
        board_data["cardinal"] = cardinal
        board_data["surround"] = surround

        data = json.dumps(board_data)
        board_file.write(data)
        board_file.close()

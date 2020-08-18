#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
pre-calculate all the valid adjacent cells of each cell
"""
import json

if __name__ == "__main__":
    with open("board-util-data.json", "w") as board_file:
        cardinal = dict()
        surround = dict()

        cardinal_dirs = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        surround_dirs = [(1, -1), (1, 0), (1, 1), (0, 1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]

        for x in range(8):
            for y in range(8):
                cardinal[str((x, y))] = dict()
                accumulation = []
                for step in range(1, 13):
                    cardinal[str((x, y))][step] = accumulation.copy()
                    for direction in cardinal_dirs:
                        next_x, next_y = x + direction[0] * step, y + direction[1] * step
                        if -1 < next_x < 8 and -1 < next_y < 8:
                            accumulation.append(str((next_x, next_y)))
                            cardinal[str((x, y))][step].append(str((next_x, next_y)))

                surround[str((x, y))] = []
                for direction in surround_dirs:
                    next_x, next_y = x + direction[0], y + direction[1]
                    if -1 < next_x < 8 and -1 < next_y < 8:
                        surround[str((x, y))].append(str((next_x, next_y)))

        board_data = dict()
        board_data["cardinal"] = cardinal
        board_data["surround"] = surround

        data = json.dumps(board_data)
        board_file.write(data)
        board_file.close()

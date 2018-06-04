from __future__ import division
from Queue import PriorityQueue
from utils import HopliteError

import random

import logging

logger = logging.getLogger(__name__)


class NoPathExistsError(HopliteError):
    pass


class NotFoundError(HopliteError):
    pass


DIRECTIONS = [(0, -1), (-1, 0), (-1, 1), (0, 1), (1, 0), (1, -1)]

VALID_CELLS = [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, -1), (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (2, -2),
               (2, -1), (2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (3, -3), (3, -2), (3, -1), (3, 0), (3, 1), (3, 2),
               (3, 3), (3, 4), (4, -4), (4, -3), (4, -2), (4, -1), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4), (5, -4),
               (5, -3), (5, -2), (5, -1), (5, 0), (5, 1), (5, 2), (5, 3), (5, 4), (6, -4),
               (6, -3), (6, -2), (6, -1), (6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (7, -4), (7, -3), (7, -2), (7, -1),
               (7, 0), (7, 1), (7, 2), (7, 3), (7, 4), (8, -4), (8, -3), (8, -2), (8, -1), (8, 0), (8, 1), (8, 2),
               (8, 3), (9, -4), (9, -3), (9, -2), (9, -1), (9, 0), (9, 1), (9, 2), (10, -4), (10, -3), (10, -2),
               (10, -1), (10, 0), (10, 1), (11, -4), (11, -3), (11, -2), (11, -1), (11, 0)]


def arc(origin, direction, depth):
    """A set of cells extending from three neighbors of the start cell."""
    results = set()
    index = DIRECTIONS.index(direction)
    for i in range(1, depth+1):
        for j in range(index - 1, index + 2):
            angle = DIRECTIONS[j % 6]

            vector = mult(angle, i)
            target = add(origin, vector)
            if isValid(target):
                results.add(target)
    return results


def burst(cell, distance=1):
    """The set of cells within :distance: distance of :cell:"""
    results = set((cell,))
    for i in range(0, distance):
        results = reduce(lambda r, cell: r | neighbors(cell), results, results)
    return results


def cells_in_polygon(*corners):
    """Given a set of corners, determine all the cells partially or completely enclosed within that polygon"""
    raise NotImplementedError


def cone(origin, left, right, depth):
    """Set of cells extending depth from origin bounded by left and right as viewed from origin"""
    raise NotImplementedError


def diagonals(cell):
    """Determine the valid cells that are located diagonally from the cell provided."""
    offsets = [(-2, 1), (-1, 2), (1, 1), (2, -1), (1, -2), (-1, -1)]
    cL, cR = cell
    return set(filter(isValid, [(cL + oL, cR + oR) for (oL, oR) in offsets]))


def distance(start, end):
    """Minimum number of cells crossed to get from :start: to :end:"""
    a = to_cubic(start)
    b = to_cubic(end)
    return (abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])) / 2


def find(grid, obj):
    """Locate the given obj in a grid"""
    for pos, item in self.cells.items():
        if item == obj or obj in item:
            return pos
    raise NotFoundError


def find_path(grid, start, goals):
    """Find the shortest possible path across :grid: from :start: to a cell in :goals:"""
    if not isinstance(list(goals)[0], tuple):
        goals = [goals]
    frontier = PriorityQueue()
    frontier.put((0, [start]))

    cost_so_far = {start: 0}

    while not frontier.empty():
        cost, path = frontier.get()
        current = path[-1]

        if current in goals:
            return path

        for next in sorted(neighbors(current), key=lambda k: random.random()):
            new_cost = cost + float("inf") if next in grid else 1
            if new_cost < cost_so_far.get(next, float("inf")):
                cost_so_far[next] = new_cost
                priority = new_cost + \
                    min(map(lambda x: distance(next, x), goals))
                frontier.put((priority, path + [next]))
    raise NoPathExistsError()


def isValid(cell):
    """Determine if a cell is on the standard sized grid I'm using."""
    L, R = cell
    if abs(R) <= 4 and \
            0 <= R + L <= 11 and \
            0 <= L <= 11:
        return True
    return False


def line(cell, direction, distance=1):
    results = set()
    L, R = cell
    dL, dR = direction
    for d in range(0, distance + 1):
        if isValid((L + dL * d, R + dR * d)):
            results.add((L + dL * d, R + dR * d))
    return results


def lines(cell, distance=1):
    results = set()
    for direction in DIRECTIONS:
        results = results | line(cell, direction, distance)
    return results


def neighbors(cell):
    """Determine the valid cells that are next to the cell provided."""
    cL, cR = cell
    return set(filter(isValid, [(cL + oL, cR + oR) for (oL, oR) in DIRECTIONS]))


def to_cubic(cell):
    q, r = cell
    return (q, -q - r, r)


def unit_vector(src, dest):
    """Normalize the distance between two cells, such that the longest either direction is one."""
    sL, sR = src
    dL, dR = dest
    denominator = max(abs(dL - sL), abs(dR - sR))
    return (int((dL - sL) / denominator) if denominator != 0 else 0,
            int((dR - sR) / denominator) if denominator != 0 else 0)


def add(start, vector):
    return (start[0] + vector[0], start[1] + vector[1])


def mult(vector, scalar):
    return (vector[0] * scalar, vector[1] * scalar)

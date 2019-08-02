import json
from typing import List
from dataclasses import dataclass


def to_dict(obj):
    return json.loads(json.dumps(obj, default=lambda o: o.__dict__))


@dataclass
class Vector:
    x: int
    y: int


@dataclass
class Entity:
    position: Vector
    client_id: str


@dataclass
class World:
    width: int
    height: int
    entities: List[Entity]

    def in_bounds(self, vector: Vector):
        return (vector.x >= 0 and vector.x < self.height
                and vector.y >= 0 and vector.y < self.width)

    def make_grid(self) -> List[List[List[Entity]]]:
        """
        Derive a 2D list of the contents of each coordinate location. The outer
        grid is the y coordinate, and the inner is the x coordinate (think rows
        and columns)
        """
        grid = []
        for y in range(self.width):
            grid.append([])
            for x in range(self.height):
                grid[y].append([])
                grid[y][x] = []

        for e in self.entities:
            grid[e.position.y][e.position.x].append(e)
        return grid


@dataclass
class Action:
    client_id: str
    kind: str  # Move | Attack
    direction: str  # North | South | East | West

from dataclasses import dataclass
from typing import List, Optional
from .domain import Entity, Vector


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

    def get_entity_by_id(self, id: str) -> Optional[Entity]:
        """Get the entity by its id. This is the preferred way of retrieving
        and entity, and can be optimized for constant-time looking as needed"""
        for e in self.entities:
            if e.client_id == id:
                return e
        return None

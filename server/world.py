from dataclasses import dataclass
from typing import List, Optional
from .domain import Entity, Vector


@dataclass
class Tile:
    """The environment at a given Tile; ground, walls. """
    tile_id: str
    is_dense: bool


@dataclass
class World:
    width: int
    height: int
    entities: List[Entity]
    tile_grid: List[List[Tile]]

    def get_tile(self, position: Vector) -> Tile:
        """Returns the tile for a position; position must be in bounds"""
        return self.tile_grid[position.y][position.x]

    def in_bounds(self, vector: Vector) -> bool:
        return (vector.x >= 0 and vector.x < self.height
                and vector.y >= 0 and vector.y < self.width)

    def get_entity_by_id(self, id: str) -> Optional[Entity]:
        """
        Get the entity by its id. This is the preferred way of retrieving
        and entity, and can be optimized for constant-time lookup when needed
        """
        for e in self.entities:
            if e.client_id == id:
                return e
        return None


@dataclass
class Location:
    """Represents the contents of a given a position in the world"""
    tile: Tile
    entity: Optional[Entity]


@dataclass
class LogicGrid:
    """
    Derived state from the world. Places entities and tiles in the same 2D
    grid for efficient lookups.  Movement operations should be made through
    the logic grid via move_entity for positional tracking on the grid. If an
    entity's position is updated outside of the logic grid, the grid should
    be invalidated and re-derived from the world state."""

    world: World
    grid: List[List[Location]]

    @staticmethod
    def get_logic_grid(world: World) -> "LogicGrid":
        """
        Derive a 2D grid of Locations. The outer list is
        the y coordinate, and the inner is the x coordinate (think rows
        and columns)
        """
        grid: List[List[Location]] = []
        for y in range(world.width):
            grid.append([])
            for x in range(world.height):
                grid[y].append(Location(tile=world.get_tile(Vector(x, y)),
                                        entity=None))

        for e in world.entities:
            grid[e.position.y][e.position.x].entity = e
        return LogicGrid(grid=grid, world=world)

    def is_passable(self, position: Vector):
        if self.world.in_bounds(position):
            location = self.get_location(position)
            return (not location.tile.is_dense
                    and not location.entity)
        return False

    def get_location(self, position: Vector) -> Location:
        return self.grid[position.y][position.x]

    def move_entity(self, entity: Entity, destination: Vector) -> bool:
        """
        Movements through the course of a tick need to be handled through move
        entity to keep the internal state of the logic grid consistent.
        """
        origin_loc = self.get_location(entity.position)
        dest_loc = self.get_location(destination)
        if self.is_passable(destination):
            origin_loc.entity = None
            dest_loc.entity = entity
            entity.position = destination
            return True
        return False

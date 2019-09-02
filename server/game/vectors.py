from dataclasses import dataclass
from typing import Callable, List, Optional, Tuple


@dataclass(frozen=True)
class Vector:
    x: int
    y: int


def dir_to_vec(direction: str) -> Vector:
    """Convert a cardinal direction to a vector"""
    dir_vec_map = {
        # TODO - handle flipping the orientation to "Screen Space" on the
        # the client.  y=-1 for north is confusing
        "North": Vector(0, -1),
        "South": Vector(0, 1),
        "East": Vector(1, 0),
        "West": Vector(-1, 0),
    }
    return dir_vec_map.get(direction, Vector(0, 0))


def add(a: Vector, b: Vector) -> Vector:
    return Vector(a.x + b.x, a.y + b.y)


def subtract(a: Vector, b: Vector) -> Vector:
    return Vector(a.x - b.x, a.y - a.y)


def multiply(a: Vector, scalar: int):
    return Vector(a.x * scalar, a.y * scalar)


def raycast(start: Vector,
            direction: Vector,
            max_dist: int = 10,
            predicate: Callable[[Vector], bool] = lambda x: True
            ) -> Tuple[Optional[Vector], List[Vector]]:
    """
    Cast a ray starting from position `start` in Vector `direction`.
    Return a tuple (hit, positions) where `hit` is the first Vector position
    that fails the `predicate`, and positions is a list of positions (Vectors)
    to a max distance of `maxDist` that pass the predicate
    """
    ray = (add(start, multiply(direction, i + 1)) for i in range(max_dist))
    hit = None
    ray_path = []
    for e in ray:
        if predicate(e):
            ray_path.append(e)
        else:
            hit = e
            break
    return (hit, ray_path)

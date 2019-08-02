from .domain import Vector


def dir_to_vec(direction: str):
    """Convert a cardinal direction to a vector"""
    dir_vec_map = {
        # TODO - handle flipping the orientation to "Screen Space" on the
        # the client.  y=-1 for north is confusing
        "North": Vector(0, -1),
        "South": Vector(0, 1),
        "East": Vector(1, 0),
        "West": Vector(-1, 0),
    }
    return dir_vec_map.get(direction)


def add(a: Vector, b: Vector) -> Vector:
    return Vector(a.x + b.x, a.y + b.y)


def subtract(a: Vector, b: Vector) -> Vector:
    return Vector(a.x - b.x, a.y - a.y)

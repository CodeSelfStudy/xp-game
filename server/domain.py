import json
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
    health: int

    def get_name(self):
        return self.client_id[-7:]


@dataclass
class Action:
    client_id: str
    kind: str  # Move | Attack
    direction: str  # North | South | East | West

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

@dataclass
class Action:
    client_id: str
    action: str


from dataclasses import dataclass
from .vectors import Vector


@dataclass
class Entity:
    position: Vector
    client_id: str
    health: int

    def get_name(self):
        return self.client_id[-7:]

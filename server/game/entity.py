from dataclasses import dataclass
from typing import Optional, Tuple
from common.messages import Action, Ability
from .vectors import Vector


@dataclass
class Entity:
    position: Vector
    client_id: str
    health: int
    current_action: Optional[Tuple[Action, Ability]] = None

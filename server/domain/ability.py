from typing import Union, Optional
from dataclasses import dataclass


@dataclass(frozen=True)
class Ability:
    kind: str  # Move | Attack | Dash
    color: str
    reach: int
    delay: int
    damage: Optional[int] = None

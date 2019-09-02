from typing import Union
from dataclasses import dataclass


@dataclass(frozen=True)
class Action:
    """An action in the game world undertaken by a specific entity"""
    entity_id: str
    kind: str  # Move | Attack | Spawn | Despawn | Dash
    direction: str = ""  # North | South | East | West


@dataclass(frozen=True)
class LoginEventDetail:
    character_name: str


@dataclass(frozen=True)
class ClientEvent:
    """A lifecycle event associated with a specific client"""
    kind: str  # login
    detail: Union[LoginEventDetail]

    LOGIN_EVENT_KIND = "login"

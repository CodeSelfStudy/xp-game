from dataclasses import dataclass
from typing import Dict, Generator, Any, Tuple, Optional
from server.domain.messages import Action
from server.domain import vectors as vec
from .world import LogicGrid


@dataclass(frozen=True)
class Ability:
    kind: str  # Move | Attack | Dash
    color: str
    reach: int
    delay: int
    damage: Optional[int] = None


@dataclass(frozen=True)
class Context:
    logic_grid: LogicGrid
    user_data: Dict[str, str]
    socket: Any


ActionFrame = Tuple[Action, Context]
ActionRoutine = Generator[None, ActionFrame, None]

abilities: Dict[str, Ability] = {
    'Attack': Ability(kind="Attack", color="red",
                      reach=1, damage=2, delay=10),
    'Aimed Shot': Ability(kind="Aimed Shot", color="red",
                          reach=3, damage=1, delay=15),
    'Move':   Ability(kind="Move", color="blue", reach=1, delay=5),
    'Dash':   Ability(kind="Dash", color="blue", reach=2, delay=10),
}


def perform_ability(action: Action) -> ActionRoutine:
    ability = abilities[action.kind]
    duration = ability.delay

    def execute_action(a: Action, c: Context):
        if a.kind == "Move":
            return perform_move(a, c)
        if a.kind == "Attack":
            return perform_attack(a, c)
        if a.kind == "Dash":
            return perform_dash(a, c)
        if a.kind == "Aimed Shot":
            return perform_aimed_shot(a, c)

    while duration > 0:
        # yield until the duration has expired
        _ = (yield)
        duration -= 1
    a, c = (yield)
    execute_action(a, c)


def perform_move(action: Action, ctx: Context) -> None:
    entity, direction = action.entity, action.direction
    step = vec.dir_to_vec(direction)
    destination = vec.add(step, entity.position) if step else None
    if destination and ctx.logic_grid.is_passable(destination):
        ctx.logic_grid.move_entity(entity, destination)


def perform_attack(action: Action, ctx: Context) -> None:
    ability = abilities["Attack"]
    entity, direction = action.entity, action.direction
    step = vec.dir_to_vec(direction)
    target_pos = vec.add(step, entity.position)

    loc = (ctx.logic_grid.get_location(target_pos)
           if ctx.logic_grid.world.in_bounds(target_pos) else None)

    if loc and loc.entity:
        target = loc.entity
        result = (f"They strike {ctx.user_data.get(target.client_id)}, "
                  f"dealing {ability.damage} damage.")
        target.health -= ability.damage or 0
    else:
        result = "They miss."

    event = {
        'id': "",
        'body': f"""{ctx.user_data.get(entity.client_id)} swings their """
                f"""vorpal sword to the {direction}. {result}"""
    }
    ctx.socket.emit('chat', event)


def perform_dash(action: Action, ctx: Context) -> None:
    ability = abilities['Dash']
    entity, direction = action.entity, action.direction
    step_dir = vec.dir_to_vec(direction)
    if not step_dir:
        return None
    _, path = vec.raycast(entity.position, step_dir, max_dist=ability.reach,
                          predicate=ctx.logic_grid.is_passable)
    if path:
        ctx.logic_grid.move_entity(entity, path[-1])


def perform_aimed_shot(action: Action, ctx: Context) -> None:
    ability = abilities["Aimed Shot"]
    entity, direction = action.entity, action.direction
    step = vec.dir_to_vec(direction)
    if not step:
        return None
    hit, path = vec.raycast(entity.position, step, max_dist=ability.reach,
                            predicate=ctx.logic_grid.is_passable)
    loc = (ctx.logic_grid.get_location(hit)
           if hit and ctx.logic_grid.world.in_bounds(hit) else None)
    if loc and loc.entity:
        target = loc.entity
        result = (f"They strike {ctx.user_data.get(target.client_id)}, "
                  f"dealing {ability.damage} damage.")
        target.health -= ability.damage or 0
    else:
        result = "They miss."

    event = {
        'id': "",
        'body': f"{ctx.user_data.get(entity.client_id)} draws their "
                f"bow, aiming to the {direction}. {result}"
    }
    ctx.socket.emit('chat', event)

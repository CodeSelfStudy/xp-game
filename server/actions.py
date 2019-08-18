from dataclasses import dataclass
from typing import Dict
from .domain import Ability, Action
from .world import LogicGrid
from . import vectors as vec


@dataclass(frozen=True)
class Context:
    logic_grid: LogicGrid
    user_data: Dict[str, str]
    socket: any


allowed_actions = {'Attack', 'Move', 'Dash', 'Aimed Shot'}
abilities: Dict[str, Ability] = {
    'Attack': Ability(kind="Attack", color="red",
                      reach=1, damage=1),
    'Aimed Shot': Ability(kind="Aimed Shot", color="red",
                          reach=3, damage=1),
    'Move':   Ability(kind="Move", color="blue", reach=1),
    'Dash':   Ability(kind="Dash", color="blue", reach=2),
}


def perform_ability(action: Action, ctx: Context) -> None:
    if action.kind == "Move":
        return perform_move(action, ctx)
    if action.kind == "Attack":
        return perform_attack(action, ctx)
    if action.kind == "Dash":
        return perform_dash(action, ctx)
    if action.kind == "Aimed Shot":
        return perform_aimed_shot(action, ctx)


def perform_move(action: Action, ctx: Context) -> None:
    entity, direction = action.entity, action.direction
    step = vec.dir_to_vec(direction)
    destination = vec.add(step, entity.position) if step else None
    if destination and ctx.logic_grid.is_passable(destination):
        ctx.logic_grid.move_entity(entity, destination)


def perform_attack(action: Action, ctx: Context) -> None:
    entity, direction = action.entity, action.direction
    step = vec.dir_to_vec(direction)
    target_pos = vec.add(step, entity.position) if step else None

    loc = (ctx.logic_grid.get_location(target_pos)
           if ctx.logic_grid.world.in_bounds(target_pos) else None)

    if loc and loc.entity:
        target = loc.entity
        result = (f"They strike {ctx.user_data.get(target.client_id)}, "
                  "dealing 1 damage.")
        target.health -= 1
    else:
        result = "They miss."

    event = {
        'id': "",
        'body': f"""{ctx.user_data.get(entity.client_id)} swings their """
                f"""vorpal sword to the {direction}. {result}"""
    }
    ctx.socket.emit('chat', event)


def perform_dash(action: Action, ctx: Context) -> None:
    entity, direction = action.entity, action.direction
    step_dir = vec.dir_to_vec(direction)
    if not step_dir:
        return None
    _, path = vec.raycast(entity.position, step_dir, max_dist=2,
                          predicate=ctx.logic_grid.is_passable)
    if path:
        ctx.logic_grid.move_entity(entity, path[-1])


def perform_aimed_shot(action: Action, ctx: Context) -> None:
    entity, direction = action.entity, action.direction
    step = vec.dir_to_vec(direction)
    if not step:
        return None
    hit, path = vec.raycast(entity.position, step, max_dist=3,
                            predicate=ctx.logic_grid.is_passable)
    loc = (ctx.logic_grid.get_location(hit)
           if hit and ctx.logic_grid.world.in_bounds(hit) else None)
    if loc and loc.entity:
        target = loc.entity
        result = (f"They strike {ctx.user_data.get(target.client_id)}, "
                  "dealing 1 damage.")
        target.health -= 1
    else:
        result = "They miss."

    event = {
        'id': "",
        'body': f"""{ctx.user_data.get(entity.client_id)} draws their """
                f"""bow, aiming to the {direction}. {result}"""
    }
    ctx.socket.emit('chat', event)

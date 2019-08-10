import queue
import time
from collections import defaultdict
from typing import Callable, Dict
from .utils import to_dict
from .domain import Entity, Action, Vector
from .world import World, LogicGrid
from .environment import generate_random_map
from . import vectors as vec


TICK_INTERVAL = 1
WORLD_WIDTH = 10
WORLD_HEIGHT = 10

action_queue = queue.Queue()

game_state = World(
    width=WORLD_WIDTH,
    height=WORLD_HEIGHT,
    entities=[],
    tile_grid=generate_random_map(WORLD_WIDTH, WORLD_HEIGHT)
)


socket_server = None
user_map: Dict[str, str]


def emit(channel, data, room=None):
    if socket_server:
        socket_server.emit(channel, to_dict(data), room=room)


def enqueue_action(action_message, client_id):
    if not action_message or 'kind' not in action_message:
        return
    action = Action(client_id=client_id,
                    kind=action_message.get('kind'),
                    direction=action_message.get('direction'))
    action_queue.put(action)

    # if the action should be telegraphed between ticks, broadcast it
    if action.kind in {"Attack", "Move"}:
        entity = game_state.get_entity_by_id(action.client_id)
        if entity:
            emit('view', {'entity': entity, 'action': action})


def process_tick():
    action_filter: dict[str, Action] = {}
    while not action_queue.empty():
        # filter to a single action per user
        a = action_queue.get(block=True)
        action_filter[a.client_id] = a

    # group actions by kind
    actions: dict[str, list[Action]] = defaultdict(list)
    for a in action_filter.values():
        actions[a.kind].append(a)

    logic_grid = LogicGrid.get_logic_grid(game_state)

    def perform_on_logic_grid(
            func: Callable[[Action, str, LogicGrid], None],
            action: Action) -> None:
        entity = game_state.get_entity_by_id(action.client_id)
        if entity:
            func(entity, action.direction, logic_grid)

    # Process actions in order of Despawn -> Move -> Attack -> Spawn
    for a in actions.get('Despawn', []):
        despawn_entity(a.client_id)

    for a in actions.get('Move', []):
        perform_on_logic_grid(perform_move, a)

    for a in actions.get('Attack', []):
        perform_on_logic_grid(perform_action, a)

    for a in actions.get('Spawn', []):
        spawn_entity(a.client_id)

    for e in game_state.entities:
        if e.health <= 0:
            despawn_entity(e.client_id)


def perform_move(entity: Entity, direction: str, logic_grid: LogicGrid):
    step = vec.dir_to_vec(direction)
    destination = vec.add(step, entity.position) if step else None

    if destination and logic_grid.is_passable(destination):
        logic_grid.move_entity(entity, destination)


def perform_action(entity: Entity, direction: str, logic_grid: LogicGrid):
    # TODO cache making the grid per frame, and make available to actions
    step = vec.dir_to_vec(direction)
    target_pos = vec.add(step, entity.position) if step else None

    loc = (logic_grid.get_location(target_pos)
           if logic_grid.world.in_bounds(target_pos) else None)
    if loc and loc.entity:
        target = loc.entity
        result = (f"They strike {target.get_name()}, "
                  + "dealing 1 damage.")
        target.health -= 1
    else:
        result = "They miss."

    event = {
        'id': "",
        # TODO - replace the sliced client id with a name
        'body': f"""{user_data.get(entity.client_id)} swings their vorpal """
                f"""sword to the {direction}. {result}"""
    }
    socket_server.emit('chat', event)


def spawn_entity(client_id):
    # despawn any existing entity for the client_id
    despawn_entity(client_id)
    # create an entity identified by the given client_id
    game_state.entities.append(Entity(position=Vector(0, 0),
                                      client_id=client_id,
                                      health=5))


def despawn_entity(client_id):
    entity = game_state.get_entity_by_id(client_id)
    if entity:
        game_state.entities.remove(entity)
        emit('despawn', {})


def run_ticker(socketio, user_map):
    """
    Main game loop; loop fires every TICK_INTERVAL, updates game state,
    and broadcasts the update to clients
    """
    global socket_server
    global user_data
    socket_server = socketio
    user_data = user_map
    tick = 0
    while(True):
        time.sleep(TICK_INTERVAL)
        print("Current tick: " + str(tick))
        process_tick()
        emit('world', game_state)
        tick += 1

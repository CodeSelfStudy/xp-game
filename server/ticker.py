from queue import Queue
import time
from random import randint
from typing import Callable, Dict, Any
from .utils import to_dict
from .domain import Entity, Action, Vector
from .world import World, LogicGrid
from .environment import generate_random_map
from .actions import perform_ability, Context, allowed_actions, abilities


TICK_INTERVAL = 1
WORLD_WIDTH = 10
WORLD_HEIGHT = 10

action_queue: Any = Queue()

game_state = World(
    width=WORLD_WIDTH,
    height=WORLD_HEIGHT,
    entities=[],
    tile_grid=generate_random_map(WORLD_WIDTH, WORLD_HEIGHT)
)


socket_server = None
user_data: Dict[str, str]


def emit(channel, data, room=None):
    if socket_server:
        socket_server.emit(channel, to_dict(data), room=room)


def enqueue_action(action_message, client_id):
    if not action_message or 'kind' not in action_message:
        return
    kind = action_message['kind']
    if kind == 'Despawn':
        despawn_entity(client_id)
    elif kind == 'Spawn':
        spawn_entity(client_id)
    elif kind in allowed_actions:
        entity = game_state.get_entity_by_id(client_id)
        if entity:
            action = Action(entity=entity,
                            kind=kind,
                            direction=action_message.get('direction'))
            action_queue.put(action)
            emit('view', {
                'action': action,
                'ability': abilities.get(action.kind)
            })


def process_tick():
    action_filter: Dict[str, Action] = {}
    while not action_queue.empty():
        # filter to a single action per user
        a = action_queue.get(block=True)
        if not a.entity:
            continue
        action_filter[a.entity.client_id] = a

    logic_grid = LogicGrid.get_logic_grid(game_state)

    def perform_with_context(
            func: Callable[[Action, Context], None],
            action: Action) -> None:
        context = Context(logic_grid=logic_grid,
                          user_data=user_data,
                          socket=socket_server)
        if action.entity:
            func(action, context)

    for a in action_filter.values():
        if a.kind in allowed_actions:
            perform_with_context(perform_ability, a)

    for e in game_state.entities:
        if e.health <= 0:
            despawn_entity(e.client_id)


def spawn_entity(client_id):
    # despawn any existing entity for the client_id
    despawn_entity(client_id)
    # create an entity identified by the given client_id
    x_pos = randint(0, WORLD_WIDTH-1)
    y_pos = randint(0, WORLD_HEIGHT-1)
    game_state.entities.append(Entity(position=Vector(x_pos, y_pos),
                                      client_id=client_id,
                                      health=5))


def despawn_entity(client_id):
    entity = game_state.get_entity_by_id(client_id)
    if entity:
        game_state.entities.remove(entity)
        emit('despawn', {}, room=client_id)


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

from queue import Queue
import time
from random import randint
from typing import Dict, Optional, Tuple, List
from server.utilities.serialize import to_dict
from server.domain.entity import Entity
from server.domain.vectors import Vector
from server.domain.messages import Action
from .world import World, LogicGrid
from .environment import generate_random_map
from .actions import perform_ability, Context, abilities, ActionRoutine


TICK_INTERVAL = 0.1
WORLD_WIDTH = 10
WORLD_HEIGHT = 10

ActionMessage = Tuple[Action, Optional[ActionRoutine]]

action_queue: 'Queue[ActionMessage]' = Queue()

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


def enqueue_client_message(message: Dict[str, str], client_id: str):
    """
    Formats a message from the client into an `Action` object, to be placed
    on the action_queue. Messages to spawn/despawn are processed immediately
    """
    if not message or 'kind' not in message:
        return
    kind = message['kind']
    if kind == 'Despawn':
        despawn_entity(client_id)
        return
    if kind == 'Spawn':
        spawn_entity(client_id)
        return
    entity = game_state.get_entity_by_id(client_id)
    if entity:
        action = Action(entity=entity, kind=kind,
                        direction=message.get('direction', ""))
        enqueue_action(action, None)


def enqueue_action(action: Action,
                   in_progress: Optional[ActionRoutine] = None):
    """Put an action into the action queue, to be processed at the next tick"""
    if action.entity and action.kind in abilities:
        action_queue.put((action, in_progress))
        emit('view', {
            'action': action,
            'ability': abilities.get(action.kind)
        })


def process_tick() -> List[Tuple[Action, ActionRoutine]]:
    """
    Process all the actions in the action_queue.  The consists of user inputs,
    and actions that are processed over multiple ticks. Return a list of
    ongoing `ActionRoutine`s, to be placed back in the action_queue
    """

    # filter the action queue down to a single action per client
    # TODO - if an `ActionMessage` is of the same kind as another action
    # that has an ongoing `ActionRoutine`, don't drop the `ActionRoutine`!!
    # This leads to pressing the move button twice cancelling the previous move
    action_filter: Dict[str, ActionMessage] = {}
    while not action_queue.empty():
        a, in_progress = action_queue.get(block=True)
        if not a.entity:
            continue
        action_filter[a.entity.client_id] = (a, in_progress)

    context = Context(logic_grid=LogicGrid.get_logic_grid(game_state),
                      user_data=user_data,
                      socket=socket_server)

    actions_in_progress = []
    for a, in_progress in action_filter.values():
        if a.kind in abilities:
            if not in_progress:
                in_progress = perform_ability(a)
                in_progress.__next__()
            try:
                in_progress.send((a, context))
            except StopIteration:
                in_progress = None
            if in_progress:
                actions_in_progress.append((a, in_progress))

    for e in game_state.entities:
        if e.health <= 0:
            despawn_entity(e.client_id)
    return actions_in_progress


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
        if tick % 100 == 0:
            print("Current tick: " + str(tick))
        partial_actions = process_tick()
        emit('world', game_state)
        for p in partial_actions:
            enqueue_action(*p)
        tick += 1

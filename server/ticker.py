import queue
import time
from collections import defaultdict
from .domain import Entity, Action, Vector, to_dict
from .world import World
from . import vectors as vec


TICK_INTERVAL = 1
WORLD_WIDTH = 5
WORLD_HEIGHT = 5

action_queue = queue.Queue()

game_state = World(
    width=WORLD_WIDTH,
    height=WORLD_HEIGHT,
    entities=[],
)


socket_server = None


def emit(channel, data):
    if socket_server:
        socket_server.emit(channel, to_dict(data))


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
    action_filter = {}
    while not action_queue.empty():
        # filter to a single action per user
        a = action_queue.get(block=True)
        action_filter[a.client_id] = a

    # group actions by kind
    actions: dict[str, list[Action]] = defaultdict(list)
    for a in action_filter.values():
        actions[a.kind].append(a)

    def action_args(action: Action) -> (Entity, str):
        entity = game_state.get_entity_by_id(action.client_id)
        return entity, action.direction

    # Process actions in order of Despawn -> Move -> Attack -> Spawn
    for a in actions.get('Despawn', []):
        despawn_entity(a.client_id)

    for a in actions.get('Move', []):
        perform_move(*action_args(a))

    for a in actions.get('Attack', []):
        perform_action(*action_args(a))

    for a in actions.get('Spawn', []):
        spawn_entity(a.client_id)


def perform_move(entity: Entity, direction: str):
    step = vec.dir_to_vec(direction)
    position = vec.add(step, entity.position) if step else None

    if position and game_state.in_bounds(position):
        entity.position = position


def perform_action(entity: Entity, direction: str):
    # TODO cache making the grid per frame, and make available to actions
    grid = game_state.make_grid()
    step = vec.dir_to_vec(direction)
    target_pos = vec.add(step, entity.position) if step else None

    loc = (grid[target_pos.y][target_pos.x]
           if game_state.in_bounds(target_pos) else None)
    if loc:
        target = loc[0]
        result = (f"They strike {target.client_id[0:5]}, "
                  + "felling them in a single blow.")
        despawn_entity(target.client_id)
    else:
        result = "They miss."

    event = {
        'id': "",
        # TODO - replace the sliced client id with a name
        'body': f"""{entity.client_id[0:5]} swings their vorpal """
                f"""sword to the {direction}. {result}"""
    }
    socket_server.emit('chat', event)


def spawn_entity(client_id):
    # despawn any existing entity for the client_id
    despawn_entity(client_id)
    # create an entity identified by the given client_id
    game_state.entities.append(Entity(position=Vector(0, 0),
                                      client_id=client_id))


def despawn_entity(client_id):
    entity = game_state.get_entity_by_id(client_id)
    if entity:
        game_state.entities.remove(entity)


def run_ticker(socketio):
    """
    Main game loop; loop fires every TICK_INTERVAL, updates game state,
    and broadcasts the update to clients
    """
    global socket_server
    global game_state
    socket_server = socketio
    tick = 0
    while(True):
        time.sleep(TICK_INTERVAL)
        print("Current tick: " + str(tick))
        process_tick()
        emit('world', game_state)
        tick += 1

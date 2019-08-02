import queue
import time
from .domain import Entity, World, Action, Vector, to_dict
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


def client_connect(client_id):
    # TOOD - process as an action in tick loop
    game_state.entities.append(Entity(position=Vector(0, 0),
                                      client_id=client_id))


def client_disconnect(client_id):
    # THIS IS BAD AND NOT AT ALL SAFE.  DON'T DO THIS.
    # TODO - should be processed synchronously as an action in tick loop
    # or asynchronously using a safe structure
    game_state.entities = [e for e in game_state.entities
                           if e.client_id != client_id]


def enqueue_action(action_message, client_id):
    if not action_message or 'kind' not in action_message:
        return
    action = Action(client_id=client_id,
                    kind=action_message.get('kind'),
                    direction=action_message.get('direction'))
    action_queue.put(action)
    entity_maybe = [e for e in game_state.entities
                    if e.client_id == action.client_id]
    if len(entity_maybe) == 1:
        entity = entity_maybe[0]
        emit('view', {'entity': entity, 'action': action})


def broadcast_state():
    emit('world', game_state)


def process_tick():
    actions = {}
    while not action_queue.empty():
        a = action_queue.get(block=True)
        actions[a.client_id] = a

    for entity in game_state.entities:
        a = actions.get(entity.client_id)
        if a is None:
            continue
        if a.kind == "Move":
            perform_move(entity, a.direction)
        if a.kind == "Attack":
            perform_action(entity, a.direction)


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

    target = (grid[target_pos.y][target_pos.x]
              if game_state.in_bounds(target_pos) else None)
    if target:
        result = f"They strike {target[0].client_id[0:5]}"
    else:
        result = "They miss."

    event = {
        'id': "",
        # TODO - replace the sliced client id with a name
        'body': f"""{entity.client_id[0:5]} swings their vorpal """
                f"""sword to the {direction}. {result}"""
    }
    socket_server.emit('chat', event)


def run_ticker(socketio):
    global socket_server
    socket_server = socketio
    tick = 0
    while(True):
        time.sleep(TICK_INTERVAL)
        print("Current tick: " + str(tick))
        process_tick()
        broadcast_state()
        tick += 1

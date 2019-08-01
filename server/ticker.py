import queue
import time
from .domain import Entity, World, Action, Vector, to_dict

TICK_INTERVAL = 1

action_queue = queue.Queue()

game_state = World(
    width=5,
    height=5,
    entities=[]
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
    # TODO - should be processed as an action in tick loop
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
            perform_move(entity, a)
        if a.kind == "Attack":
            print(f"{a.client_id} Attacks {a.direction}")


def perform_move(entity: Entity, a: Action):
    if a.direction == 'West' and entity.position.x > 0:
        entity.position.x -= 1
    if a.direction == 'East' and entity.position.x < game_state.height - 1:
        entity.position.x += 1
    if a.direction == 'North' and entity.position.y > 0:
        entity.position.y -= 1
    if a.direction == 'South' and entity.position.y < game_state.height - 1:
        entity.position.y += 1


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

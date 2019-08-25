import os
from typing import Dict
from flask import Flask, request, render_template
from flask_socketio import SocketIO
from server.sanitizer import sanitize
from server.logger import create_logger
import server.ticker as ticker
from server.domain import ClientEvent
from server.utils import from_dict
from server.actions import allowed_actions
from server.assets import cache_buster


log = create_logger(__name__)
log.game_event('created logger')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('GAME_SECRET', 'notarealsecret')
HOST = os.environ.get('GAME_HOST', '127.0.0.1')
PORT = os.environ.get('GAME_PORT', 5000)

socketio = SocketIO(app)
client_names: Dict[str, str] = {}

# This query string can be appended to any static assets in the
# template.
cache_busting_query = cache_buster()


@app.route('/')
def homepage():
    """Render the index.html file with the frontend application."""
    data = {
        'cache_buster': cache_busting_query
    }
    return render_template('index.html', data=data)


@socketio.on('connect')
def handle_connect():
    # Authentication can go here
    log.game_event(f'client_connected: {request.sid}')


@socketio.on('disconnect')
def handle_disconnect():
    log.game_event(f'client_disconnected: {request.sid}')
    ticker.enqueue_client_message({'kind': 'Despawn'}, request.sid)


@socketio.on('event')
def handle_event(event_dict):
    """
    Events are of the format { kind: str, data: {...}}
    """
    global client_names
    event = from_dict(event_dict, ClientEvent)

    if event and event.kind == ClientEvent.LOGIN_EVENT_KIND:
        # TODO-- get from_dict to parse recursively
        client_names[request.sid] = event.detail['character_name']
        ticker.enqueue_client_message({'kind': 'Spawn'}, request.sid)


@socketio.on('action')
def handle_action(action):
    if action['kind'] in allowed_actions:
        log.game_event(f'action: {action} by {request.sid}')
        ticker.enqueue_client_message(action, request.sid)


@socketio.on('chat')
def handle_chat(incoming):
    """Respond to `chat` message from the frontend.

    `incoming` is `{'body': 'the message content'}`.
    """
    trimmed_message = incoming['body'].strip()
    if trimmed_message:
        outgoing = {
            'id': client_names.get(request.sid),
            'body': sanitize(trimmed_message),
        }
        log.game_event(f'chat_message: {outgoing}')
        socketio.emit('chat', outgoing)


if __name__ == '__main__':
    print(f"Starting server at {HOST}:{PORT}")
    socketio.start_background_task(ticker.run_ticker, socketio, client_names)
    socketio.run(app, use_reloader=True, debug=True, log_output=True,
                 host=HOST, port=PORT)

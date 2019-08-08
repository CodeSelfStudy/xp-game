import os
from flask import Flask, request, render_template
from flask_socketio import SocketIO
from server.sanitizer import sanitize
from server.logger import create_logger
import server.ticker as ticker

log = create_logger(__name__)
log.game_event('created logger')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('GAME_SECRET', 'notarealsecret')
HOST = os.environ.get('GAME_HOST', '127.0.0.1')
PORT = os.environ.get('GAME_PORT', 5000)

socketio = SocketIO(app)


@app.route('/')
def homepage():
    """Render the index.html file that contains the frontend application."""
    return render_template('index.html')


@socketio.on('connect')
def handle_connect():
    # Authentication can go here
    print('hi {}'.format(request.sid))
    log.game_event('client_connected: {}'.format(request.sid))


@socketio.on('disconnect')
def handle_disconnect():
    log.game_event('client_disconnected: {}'.format(request.sid))
    ticker.enqueue_action({'kind': 'Despawn'}, request.sid)


@socketio.on('action')
def handle_action(action):
    log.game_event('action: {} by {}'.format(action, request.sid))
    ticker.enqueue_action(action, request.sid)


@socketio.on('chat')
def handle_chat(incoming):
    """Respond to `chat` message from the frontend.

    `incoming` is `{'body': 'the message content'}`.
    """
    outgoing = {
        'id': request.sid,
        'body': sanitize(incoming['body']),
    }
    log.game_event('chat_message: {}'.format(outgoing))
    socketio.emit('chat', outgoing)


if __name__ == '__main__':
    print(f"Starting server at {HOST}:{PORT}")
    socketio.start_background_task(ticker.run_ticker, socketio)
    socketio.run(app, use_reloader=True, debug=True, log_output=True,
                 host=HOST, port=PORT)

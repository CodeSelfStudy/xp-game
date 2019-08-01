from flask import Flask, request, render_template
from flask_socketio import SocketIO
import server.ticker as ticker


app = Flask(__name__)
app.config['SECRET_KEY'] = 'notarealsecret'
socketio = SocketIO(app)


@app.route('/')
def homepage():
    """Render the index.html file that contains the frontend application."""
    return render_template('index.html')



@socketio.on('action')
def handle_action(action):
    ticker.enqueue_action(action, request.sid)


@socketio.on('connect')
def handle_connect():
    ticker.client_connect(request.sid)


@socketio.on('disconnect')
def handle_disconnect():
    ticker.client_disconnect(request.sid)


@socketio.on('chat')
def handle_chat(incoming):
    """Respond to `chat` message from the frontend.

    `incoming` is `{'body': 'the message content'}`.
    """
    print('received chat message: ', incoming)
    outgoing = {
        'id': request.sid,
        **incoming,
    }
    socketio.emit('chat', outgoing)


DEBUG_HOST = '127.0.0.1'
DEBUG_PORT = 5000
if __name__ == '__main__':
    print(f"Starting server at {DEBUG_HOST}:{DEBUG_PORT}")
    socketio.start_background_task(ticker.run_ticker, socketio)
    socketio.run(app, use_reloader=True, debug=True, log_output=True,
                 host=DEBUG_HOST, port=DEBUG_PORT)

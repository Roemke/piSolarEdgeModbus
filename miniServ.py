from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  # Zum Testen den CORS erlauben

@socketio.on('connect')
def handle_connect():
    print("Client connected!")
    socketio.emit('test_event', {'message': 'Hello from server!'})

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected!")

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=8090, debug=True)
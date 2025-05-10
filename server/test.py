from websockets.sync.client import connect
import json

def jsonify(data):
    return json.dumps(data)

with connect("ws://127.0.0.1:7890/api/ws") as websocket:
    websocket.send("ping")
    message = websocket.recv()
    print(message)

    websocket.send(json.dumps({"action": "auth", "token":"your_api_key"}))
    print(websocket.recv())

    websocket.send(json.dumps({"action": "is_running"}))
    print(websocket.recv())
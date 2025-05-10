import threading
from flask import Flask, request, jsonify, render_template
import logging
import time
from zeroconf import Zeroconf, ServiceInfo
from flask_sock import Sock, Server
import socket
import readline
import sys
import json
from flask_cors import CORS, cross_origin

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


levels = [
    {"target_score":1,
    "min_speed":0,
    "max_speed":0,
    "min_delay":500,
    "max_delay":2000},

    {"target_score":2,
    "min_speed":20,
    "max_speed":50,
    "min_delay":500,
    "max_delay":2000},

    {"target_score":5,
    "min_speed":100,
    "max_speed":200,
    "min_delay":0,
    "max_delay":250}
]

def print_with_prompt(message):
    sys.stdout.write("\r" + " " * 100 + "\r")
    print(message)
    sys.stdout.write(f"shooter> {readline.get_line_buffer()}")
    sys.stdout.flush()

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    local_ip = s.getsockname()[0]
    s.close()
    return local_ip


def start_mdns(service_name="shooter_server", service_type="_http._tcp.local.", port=7890):
    """Démarre un serveur mDNS et réannonce le service périodiquement."""
    zeroconf = Zeroconf()
    local_ip = get_local_ip()
    
    service_info = ServiceInfo(
        type_=service_type,
        name=f"{service_name}.{service_type}",
        addresses=[socket.inet_aton(local_ip)],
        port=port
    )

    zeroconf.register_service(service_info)
    print(f"mDNS annoncé : {service_name} -> http://{local_ip}:{port}")

    try:
        while True:
            time.sleep(1)
            zeroconf.update_service(service_info)
    except KeyboardInterrupt:
        pass
    finally:
        zeroconf.unregister_service(service_info)
        zeroconf.close()

threading.Thread(target=start_mdns, daemon=True).start()


app = Flask(__name__)
sock = Sock(app)
CORS(app)

running = False 
scores = {}
level_counter = 0
target_score = 0
min_speed = 0
max_speed = 0
min_delay = 0
max_delay = 0

app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@sock.route("/api/ws")
def websocket(ws:Server):
    authed = False
    ip = request.remote_addr
    while True:
        raw = ws.receive()

        if raw == "ping":
            ws.send("pong")
            continue

        data = json.loads(raw)
        action = data.get("action")

        if action == "get_scores":
            ws.send(json.dumps({"scores":[scores[d] for d in list(scores.keys())], "target_score":target_score}))
            continue

        if action == "auth":
            token = data.get("token")
            if token == None: ws.close()
            if token in API_KEYS: authed = True

            ws.send(json.dumps({"res":"success"}))
            continue

        if action == "is_running":
            if not authed: ws.close()
            ws.send(json.dumps({"res":running}))

        if action == "update_score":
            score = data.get("score")
            
            if not authed: ws.close()
            if score == None:
                ws.send(json.dumps({"success":False,"message": "missing 'score' value"}))
                continue

        if (not ip in list(scores.keys())) or (scores[ip]!=score) and running:
            score.update({ip:score})
            print_with_prompt(f"Score ({ip}) : {scores[ip]}")
            if scores[ip]>=target_score:
                print_with_prompt(f"Score ({ip}) : {scores[ip]}")
                if scores[ip]>=target_score:
                    print_with_prompt(f"Niveau terminé ({ip}) !")

                ws.send(json.dumps({"success":True}))

            ws.send(json.dumps({"success":False}))

        if action == "get_level_counter":
            if not authed: ws.close()
            ws.send(json.dumps({"success":True,"data":level_counter}))

        if action == "get_level_info":
            if not authed: ws.close()
            ws.send(json.dumps({"level_counter":level_counter, 
                                "target_score":target_score,
                                "min_speed":min_speed,
                                "max_speed":max_speed,
                                "min_delay":min_delay,
                                "max_delay":max_delay
                            }))

def run():
    app.run(host="0.0.0.0", port=7890, debug=False)

def load_level(level_id):
    reset_scores()
    global level_counter
    target_score = levels[level_id].get("target_score")
    min_speed = levels[level_id].get("min_speed")
    max_speed = levels[level_id].get("max_speed")
    min_delay = levels[level_id].get("min_delay")
    max_delay = levels[level_id].get("max_delay")
    level_counter += 1

def reset_scores():
    for i in list(scores.keys()):
        scores[i] = 0

flask_thread = threading.Thread(target=run, daemon=True)
flask_thread.start()

time.sleep(1)

print("Console interactive. Tape 'exit' pour quitter.")

while True:
    cmd = input("shooter> ")

    if cmd == "exit":
        print("Arrêt du serveur et fermeture de la console.")
        break

    elif cmd.startswith("echo "):
        print(cmd[5:])

    elif cmd == "start":
        running = True
        print("Serveur démarré.")

    elif cmd == "stop":
        running = False
        print("Serveur arrêté.")

    elif cmd == "status":
        print(f"Server {'running' if running else 'stopped'}.")

    elif cmd == "scores":
        for i in list(scores.keys()):
            print(f"Score ({i}) : {scores[i]}")

    elif cmd.startswith("load "):
        load_level(int(cmd[5:]))
        print(f"Level {cmd[5:]} chargé.")

    elif cmd.startswith("reset"):
        reset_scores()
        level_counter += 1
        print(f"Level reset.")

    else:
        print("Commande inconnue.")
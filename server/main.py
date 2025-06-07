import threading
from flask import Flask, request, jsonify, render_template
import logging
import time
from zeroconf import Zeroconf, ServiceInfo
import socket
import readline
import sys
from flask_cors import CORS, cross_origin

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

API_KEYS = ["your_api_key"]

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


class FlaskApp :
    def __init__(self):
        self.app = Flask(__name__, static_url_path='/static', static_folder='static') 
        CORS(self.app)

        self.running = False
        self.is_playing = False
        self.scores = {}
        self.level_counter = 0
        self.level_id = 0
        self.target_score = 0
        self.min_speed = 0
        self.max_speed = 0
        self.min_delay = 0
        self.max_delay = 0

        self.load_level(0)

        self.picture = "None"
        self.picture_counter = 0

        self.app.config['TEMPLATES_AUTO_RELOAD'] = True
        self.app.add_url_rule("/", "index", self.index)
        self.app.add_url_rule("/api/get_scores", "get_scores", self.get_scores)
        self.app.add_url_rule("/api/get_picture", "get_picture", self.get_picture)
        self.app.add_url_rule("/api/is_running", "is_running", self.is_running, methods=['POST'])
        self.app.add_url_rule("/api/update_score", "update_score", self.update_score, methods=['POST'])
        self.app.add_url_rule("/api/get_level_info", "get_level_info", self.get_level_info, methods=['POST'])
        self.app.add_url_rule("/api/get_level_counter", "get_level_counter", self.get_level_counter, methods=['POST'])

    def index(self):
        return render_template("index.html")
    
    def get_picture(self):
        return jsonify({"picture":self.picture, "picture_counter":self.picture_counter})

    def get_scores(self):
        return jsonify({"scores":[self.scores[d] for d in list(self.scores.keys())], "target_score":self.target_score, "level":self.level_id+1, "is_playing":self.running})

    def is_running(self):
        data = request.get_json()
        api_key = data.get("api_key")
        if api_key  in API_KEYS:
            if self.running:
                return "true"
            else:
                return "false" 
        return "", 498

    def update_score(self):
        data = request.get_json()
        api_key = data.get("api_key")
        score = data.get("data")
        ip = request.remote_addr
        if api_key  in API_KEYS:
            if (not ip in list(self.scores.keys())) or (self.scores[ip]!=score) and self.running:
                self.scores.update({ip:score})
                print_with_prompt(f"Score ({ip}) : {self.scores[ip]}")
                if self.scores[ip]>=self.target_score:
                        print_with_prompt(f"Niveau terminé ({ip}) !")
            
            return "", 200
        return "", 498

    def get_level_counter(self):
        data = request.get_json()
        api_key = data.get("api_key")
        if api_key  in API_KEYS:
            return str(self.level_counter)
        return "", 498

    def get_level_info(self):
        data = request.get_json()
        api_key = data.get("api_key")
        if api_key  in API_KEYS:
            return jsonify({"level_counter":self.level_counter, 
                            "target_score":self.target_score,
                            "min_speed":self.min_speed,
                            "max_speed":self.max_speed,
                            "min_delay":self.min_delay,
                            "max_delay":self.max_delay})
        return "", 498

    def run(self):
        self.app.run(host="0.0.0.0", port=7890, debug=False)

    def load_level(self, level_id):
        self.reset_scores()
        self.level_id = level_id
        self.target_score = levels[level_id].get("target_score")
        self.min_speed = levels[level_id].get("min_speed")
        self.max_speed = levels[level_id].get("max_speed")
        self.min_delay = levels[level_id].get("min_delay")
        self.max_delay = levels[level_id].get("max_delay")
        self.level_counter += 1

    def reset_scores(self):
        for i in list(self.scores.keys()):
            self.scores[i] = 0



flask_app = FlaskApp()
flask_thread = threading.Thread(target=flask_app.run, daemon=True)
flask_thread.start()

time.sleep(1)

print("Console interactive. Tape 'exit' pour quitter.")

print(f"Server local IP : {get_local_ip():}")

while True:
    cmd = input("shooter> ")

    if cmd == "exit":
        print("Arrêt du serveur et fermeture de la console.")
        break
        
    elif cmd.startswith("help"):
        print("exit - Quitte le programme")
        print("echo - Affiche du texte")
        print("start - Lance le jeu")
        print("stop - Stop le jeu")
        print("scores - Affiche les scores")
        print("load - Load un niveau")
        print("reset - Reset les scores")

    elif cmd.startswith("echo "):
        print(cmd[5:])

    elif cmd == "start":
        flask_app.running = True
        print("Serveur démarré.")

    elif cmd == "stop":
        flask_app.running = False
        print("Serveur arrêté.")

    elif cmd == "status":
        print(f"Server {'running' if flask_app.running else 'stopped'}.")

    elif cmd == "scores":
        for i in list(flask_app.scores.keys()):
            print(f"Score ({i}) : {flask_app.scores[i]}")

    elif cmd.startswith("load "):
        flask_app.load_level(int(cmd[5:]))
        print(f"Level {cmd[5:]} chargé.")

    elif cmd.startswith("picture "):
        image_name = cmd[8:]
        # Ajouter automatiquement le préfixe /static/ si ce n'est pas déjà fait
        if not image_name.startswith("/static/") and not image_name.startswith("http"):
            image_name = f"/static/{image_name}"
        flask_app.picture = image_name
        flask_app.picture_counter += 1
        print(f"Picture set to {flask_app.picture}.")

    elif cmd.startswith("reset"):
        flask_app.reset_scores()
        flask_app.level_counter += 1
        print(f"Level reset.")

    else:
        print("Commande inconnue.")

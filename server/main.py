import threading
from flask import Flask, request, jsonify, render_template
import logging
import time
import socket
import readline
import sys
from flask_cors import CORS, cross_origin

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

API_KEYS = []

levels = [
    {"target_score":2,
     "min_speed":1,
     "max_speed":3,
     "min_delay":500,
     "max_delay":2000},

    {"target_score":5,
     "min_speed":3,
     "max_speed":6,
     "min_delay":0,
     "max_delay":250}
]

def print_with_prompt(message):
    sys.stdout.write("\r" + " " * 100 + "\r")
    print(message)
    sys.stdout.write(f"shooter> {readline.get_line_buffer()}")
    sys.stdout.flush()


class FlaskApp :
    def __init__(self):
        self.app = Flask(__name__) 
        CORS(self.app)

        self.running = False 
        self.scores = {}
        self.level_counter = 0
        self.target_score = 0
        self.min_speed = 0
        self.max_speed = 0
        self.min_delay = 0
        self.max_delay = 0
        
        self.load_level(0)

        self.app.config['TEMPLATES_AUTO_RELOAD'] = True
        self.app.add_url_rule("/", "index", self.index)
        self.app.add_url_rule("/api/get_scores", "get_scores", self.get_scores, methods=['POST'])
        self.app.add_url_rule("/api/is_running", "is_running", self.is_running, methods=['POST'])
        self.app.add_url_rule("/api/update_score", "update_score", self.update_score, methods=['POST'])
        self.app.add_url_rule("/api/get_level_info", "get_level_info", self.get_level_info, methods=['POST'])
        self.app.add_url_rule("/api/get_level_counter", "get_level_counter", self.get_level_counter, methods=['POST'])

    def index(self):
        return render_template("index.html")
    
    def get_scores(self):
        data = request.get_json()
        api_key = data.get("api_key")
        if api_key  in API_KEYS:
            return jsonify({"scores":[self.scores[d] for d in list(self.scores.keys())], "target_score":self.target_score})
        return "", 498

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
        self.app.run(host="0.0.0.0", port=8081, debug=False)

    def load_level(self, level_id):
        self.reset_scores()
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
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
print(f"Server local IP : {s.getsockname()[0]}")
s.close()

while True:
    cmd = input("shooter> ")

    if cmd == "exit":
        print("Arrêt du serveur et fermeture de la console.")
        break

    elif cmd.startswith("echo "):
        print(cmd[5:])

    elif cmd == "start":
        flask_app.running = True
        print("Serveur démarré.")

    elif cmd == "stop":
        flask_app.running = False
        print("Serveur arrêté.")

    elif cmd == "status":
        print(f"Serveur {'en cours d\'exécution' if flask_app.running else 'arrêté'}.")

    elif cmd == "scores":
        for i in list(flask_app.scores.keys()):
            print(f"Score ({i}) : {flask_app.scores[i]}")

    elif cmd.startswith("load "):
        flask_app.load_level(int(cmd[5:]))
        print(f"Level {cmd[5:]} chargé.")

    elif cmd.startswith("reset"):
        flask_app.reset_scores()
        flask_app.level_counter += 1
        print(f"Level reset.")

    else:
        print("Commande inconnue.")
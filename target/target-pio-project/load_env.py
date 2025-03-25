import os
from dotenv import load_dotenv

env_path = os.path.join(os.getcwd(), ".env")

if os.path.exists(env_path):
    load_dotenv(env_path)

flags = []
for key in ["WIFI_SSID", "WIFI_PASSWORD", "API_KEY"]:
    value = os.getenv(key)
    if value:
        flags.append(f'-D {key}=\\"{value}\\"')

print(" ".join(flags))

#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include "Coms.h"
#include "Global.h"
#include <ESPmDNS.h>

Coms::Coms(String ssid, String password,  String api_key, Global* global) 
    : ssid(ssid), password(password),  api_key(api_key), global(global) {
    debug = false;
    server_port = 7890;
    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);
    Serial.println("\nConnecting to " + ssid);

    while(WiFi.status() != WL_CONNECTED){
        Serial.print(".");
        vTaskDelay(pdMS_TO_TICKS(100));
    }

    Serial.println("\nConnected to the WiFi network");
    Serial.print("Local ESP32 IP: ");
    Serial.println(WiFi.localIP());
    find_server();
}

void Coms::find_server() {
    if (!MDNS.begin("target_client")) {
        Serial.println("Erreur : échec de l'initialisation de mDNS");
        return;
    }

    Serial.println("Recherche du serveur mDNS...");
    int i = 1;

    while (true) {
        IPAddress serverIP = MDNS.queryHost("shooter_server");
        if (serverIP) {
            server_ip_address = serverIP.toString();
            Serial.print("Serveur trouvé : ");
            Serial.println(serverIP);
            return;
        }
        Serial.print("Essai ");
        Serial.print(i);
        Serial.println(" : Serveur non trouvé, nouvelle tentative...");
        i++;
        delay(1000);
    }
}

void Coms::loop_backend() {
    int score;
    int level_counter=0;
    global->running = true;
    while (true) {
        String is_running = post_request("/api/is_running");
        global->running = (is_running == "true");

        if (is_running=="true") {global->running==true;}
        else if (is_running=="ERROR") {find_server();}
        if (global->running) {
            int level_counter_ = post_request("/api/get_level_counter").toInt();

            if (level_counter != level_counter_) {
                Serial.println("Level changed !");
                randomSeed(analogRead(6));
                level_counter = level_counter_;
                String jsonLevel = post_request("/api/get_level_info");

                StaticJsonDocument<200> level;
                DeserializationError error = deserializeJson(level, jsonLevel);

                global->score = 0;
                global->target_score = level["target_score"];
                global->min_speed = level["min_speed"];
                global->max_speed = level["max_speed"];
                global->min_delay = level["min_delay"];
                global->max_delay = level["max_delay"];
                global->level_counter = level_counter;
            }

            if (score!=global->score) {
                score = global->score;
                post_request("/api/update_score", (String)score);
            }
        }
    }
}

String Coms::get_request(String address) {
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
  
        String serverPath = "http://" + (String)server_ip_address + ":" + (String)server_port + address;
        
        if (debug) {Serial.println(serverPath);}

        http.begin(serverPath.c_str());

        int httpResponseCode = http.GET();
        
        if (httpResponseCode > 0) {
            String payload = http.getString();
            http.end();
            if (debug) {
                Serial.println(payload);
                Serial.println(httpResponseCode);
            }
            return payload;
        }
        else {
            Serial.print("Error code: ");
            Serial.println(httpResponseCode);
            http.end();
            return "ERROR";
        }
        
    } else {
        Serial.println("WiFi Disconnected");
        return "ERROR";
    }
}

String Coms::post_request(String address) {
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
  
        String serverPath = "http://" + (String)server_ip_address + ":" + (String)server_port + address;
        
        String jsondata = "{\"api_key\":\"" + api_key + "\"}";

        if (debug) {
            Serial.println(serverPath);
            Serial.println(jsondata);
        }
        http.begin(serverPath.c_str());
        http.addHeader("Content-Type", "application/json");

        int httpResponseCode = http.POST(jsondata);
        
        if (httpResponseCode > 0) {
            String payload = http.getString();
            http.end();
            if (debug) {
                Serial.println(payload);
                Serial.println(httpResponseCode);
            }
            return payload;
        } else {
            Serial.print("Error code: ");
            Serial.println(httpResponseCode);
            http.end();
            return "ERROR";
        }
        
    } else {
        Serial.println("WiFi Disconnected");
        return "ERROR";
    }
}

String Coms::post_request(String address, String data) {
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
  
        String serverPath = "http://" + (String)server_ip_address + ":" + (String)server_port + address;
        
        String jsondata = "{\"data\":" + data + ", \"api_key\":\"" + api_key + "\"}";

        if (debug) {
            Serial.println(serverPath);
            Serial.println(jsondata);
        }
        http.begin(serverPath.c_str());
        http.addHeader("Content-Type", "application/json");

        int httpResponseCode = http.POST(jsondata);
        
        if (httpResponseCode > 0) {
            String payload = http.getString();
            http.end();
            if (debug) {
                Serial.println(payload);
                Serial.println(httpResponseCode);
            }
            return payload;
        } else {
            Serial.print("Error code: ");
            Serial.println(httpResponseCode);
            http.end();
            return "ERROR";
        }
        
    } else {
        Serial.println("WiFi Disconnected");
        return "ERROR";
    }
}


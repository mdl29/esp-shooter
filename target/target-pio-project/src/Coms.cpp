#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include "Coms.h"
#include "Global.h"

Coms::Coms(String ssid, String password, String server_ip_address, int server_port, String api_key, Global* global)
    : ssid(ssid), password(password), server_ip_address(server_ip_address), server_port(server_port), api_key(api_key), global(global) {

    debug = false;
    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);
    Serial.println("\nConnecting");

    while(WiFi.status() != WL_CONNECTED){
        Serial.print(".");
        vTaskDelay(pdMS_TO_TICKS(100));
    }

    Serial.println("\nConnected to the WiFi network");
    Serial.print("Local ESP32 IP: ");
    Serial.println(WiFi.localIP());
}

void Coms::loop_backend() {
    int score;
    int level_counter=0;
    global->running = true;
    while (true) {
        String is_running = post_request("/api/is_running");
        global->running = (is_running == "true");

        if (is_running=="true") {global->running==true;}
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


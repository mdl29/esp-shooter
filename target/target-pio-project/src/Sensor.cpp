#include <Arduino.h>
#include "Sensor.h"
#include "Global.h"

Sensor::Sensor(int sensor_pin, int max_value, Global* global)
    : sensor_pin(sensor_pin), max_value(max_value), global(global) {
    debug = false;
    pinMode(sensor_pin, INPUT);
}

int Sensor::get_sensor_value() {
    return analogRead(sensor_pin);
}

bool Sensor::detection() {
    return detection(get_sensor_value());
}

bool Sensor::detection(int value) {
    if (value>max_value) {
        Serial.print(" SENSOR | TIR DETECTE | ");
        Serial.println(value);
        return true;
    }
    else {
        if (debug) {
            Serial.print(" SENSOR |     RIEN    | ");
            Serial.println(value);
        }
        return false;
    }
}

void Sensor::loop_backend() {
    while (true) {
        if (global->running) {
            if (global->score>=global->target_score) {
                Serial.println("Bien joué ma couille !");
                vTaskDelay(pdMS_TO_TICKS(1000));
            }
            else if (detection()) {
                global->score++;
                if (global->score<global->target_score) {
                    vTaskDelay(pdMS_TO_TICKS(1500));
                }
            }
        }

        vTaskDelay(pdMS_TO_TICKS(10));
    }
}
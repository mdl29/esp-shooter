#include <Arduino.h>
#include "ServoEasing.hpp"
#include "Sensor.h"
#include "Coms.h"
#include "Global.h"

// SERVO
const int servo_pin = SERVO_PIN;
// SENSOR
const int sensor_pin = SENSOR_PIN; // ~10K 
// COMS
const char* ssid = WIFI_SSID;
const char* password = WIFI_PASSWORD;
const char* api_key = API_KEY;

struct SensorParams {
    Sensor *sensor;
};

struct ComsParams {
    Coms *coms;
};

void sensor_wrapper(void *pvParameters) {
    SensorParams *params = static_cast<SensorParams*>(pvParameters);
    params->sensor->loop_backend();
}

void coms_wrapper(void *pvParameters) {
    ComsParams *params = static_cast<ComsParams*>(pvParameters);
    params->coms->loop_backend();
}

void setup() {
    Serial.begin(9600);
    vTaskDelay(pdMS_TO_TICKS(1000));
    Serial.println("Programme lancé");

    static Global global;
    global.running = false;
    global.score=0;
    global.target_score=0;
    global.min_speed = 10;
    global.max_speed = 10;
    global.min_delay = 0;
    global.max_delay = 1;

    static Sensor* sensor = new Sensor(sensor_pin, &global);
    static SensorParams *sensor_params = new SensorParams{sensor};
    xTaskCreate(sensor_wrapper, "SensorTask", 3000, (void*)sensor_params, 1, NULL);

    static Coms* coms = new Coms(ssid, password, api_key, &global);
    static ComsParams *coms_params = new ComsParams{coms};
    xTaskCreate(coms_wrapper, "ComsTask", 8000, (void*)coms_params, 1, NULL);

    // Servo

    ServoEasing myservo;

    myservo.attach(servo_pin, 90);
    bool debug = false;
    
    while (true) {
        if (global.running && global.score<global.target_score) {
            if (global.max_speed != 0) {
                int speed = random(global.min_speed, global.max_speed);
                int target_pos = random(1, 180);
                myservo.easeTo(target_pos, speed);
                if (debug) {
                    Serial.print("SERVO  | goto:");
                    Serial.println(target_pos);
                }
                delay(random(global.min_delay, global.max_delay));
            }
            else if (global.max_speed == 0) {
                myservo.easeTo(90,180);
            }
        }
        else {
            myservo.stop();
        }
    }
}

void loop() {
}

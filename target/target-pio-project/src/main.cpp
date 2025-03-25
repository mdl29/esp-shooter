#include <Arduino.h>
#include <WiFi.h>
#include "ServoMotor.h"
#include "Sensor.h"
#include "Coms.h"
#include "Global.h"

// SERVO
#define SERVO_PIN 7
// SENSOR
#define SENSOR_PIN 4 // 10K 
#define LED_PIN 21
#define MAX_VALUE 1000
// COMS
const char* ssid = WIFI_SSID;
const char* password = WIFI_PASSWORD;
const char* api_key = API_KEY;



struct ServoParams {
    ServoMotor *servo;
};

struct SensorParams {
    Sensor *sensor;
};

struct ComsParams {
    Coms *coms;
};

void servo_wrapper(void *pvParameters) {
    ServoParams *params = static_cast<ServoParams*>(pvParameters);
    params->servo->loop_program();
}

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
    
    static ServoMotor* servo = new ServoMotor(SERVO_PIN, &global);
    static ServoParams *servo_params = new ServoParams{servo};
    xTaskCreate(servo_wrapper, "ServoTask", 3000, (void*)servo_params, 1, NULL);

    static Sensor* sensor = new Sensor(SENSOR_PIN, LED_PIN, MAX_VALUE, &global);
    static SensorParams *sensor_params = new SensorParams{sensor};
    xTaskCreate(sensor_wrapper, "SensorTask", 3000, (void*)sensor_params, 1, NULL);

    static Coms* coms = new Coms(ssid, password, api_key, &global);
    static ComsParams *coms_params = new ComsParams{coms};
    xTaskCreate(coms_wrapper, "ComsTask", 8000, (void*)coms_params, 1, NULL);
}

void loop() {
}

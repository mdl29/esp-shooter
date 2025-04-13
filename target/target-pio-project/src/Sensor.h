#pragma once

#include "Global.h"

class Sensor {
    private:
        int sensor_pin;
        Global* global;
    public:
        bool debug;
        int max_value;
        Sensor(int sensor_pin, int max_value, Global* global);
        int get_sensor_value();
        bool detection();
        bool detection(int value);
        void loop_backend();
};
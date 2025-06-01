#pragma once

#include "Global.h"

class Sensor {
    private:
        int sensor_pin;
        Global* global;
    public:
        bool debug;
        Sensor(int sensor_pin, Global* global);
        int get_sensor_value();
        bool detection();
        bool detection(int value);
        void loop_backend();
};
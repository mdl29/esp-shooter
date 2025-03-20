#pragma once

#include <Servo.h>
#include "Global.h"

class ServoMotor {
    private:
        Servo myservo;
        int servo_pin;
        Global* global;
    public:
        bool debug;
        ServoMotor(int servo_pin, Global* global);
        void loop_program();
        void write(int val);
};
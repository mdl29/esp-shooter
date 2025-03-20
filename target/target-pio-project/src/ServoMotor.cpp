#include <Servo.h>
#include "ServoMotor.h"
#include "Global.h"

ServoMotor::ServoMotor(int servo_pin, Global* global) 
    : servo_pin(servo_pin), global(global) {
    Servo myservo;
    debug=false;
    write(0);
}

void ServoMotor::write(int val) {
    myservo.write(servo_pin, val);
}

void ServoMotor::loop_program() {
    int pos = 0;
    int speed = random(global->min_speed, global->max_speed);
    int target_pos = random(1+speed, 180-speed);
    bool sense = true;
    int level_counter = global->level_counter;
    while (true) {
        if (global->running && global->score<global->target_score) {
            if (level_counter!=global->level_counter){
                level_counter = global->level_counter;
                target_pos = random(1, 179);
                speed = random(global->min_speed, global->max_speed);
                sense = (pos<target_pos);
            }
            else if (sense && pos<target_pos) {
                pos+=speed;
            }
            else if (!sense && pos>target_pos) {
                pos-=speed;
            }
            else {
                vTaskDelay(pdMS_TO_TICKS(random(global->min_delay, global->max_delay)));
                target_pos = random(1, 179);
                speed = random(global->min_speed, global->max_speed);
                sense = (pos<target_pos);
            }

            write(pos);
            
            if (debug) {
                Serial.print("SERVO  | pos:");
                Serial.println(pos);
            }
        }
        vTaskDelay(pdMS_TO_TICKS(50));
    }
}
#pragma once

#include "Global.h"

class Coms {
    private:
        String ssid;
        String password;
        String server_ip_address;
        int server_port;
        String api_key;
        Global* global;
    public:
        bool debug;
        Coms(String ssid, String password, String api_key, Global* global);
        void find_server();
        String get_request(String address);
        String post_request(String address);
        String post_request(String address, String data);
        void loop_backend();
};
#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include <AccelStepper.h>

// ---------- CONFIG ----------
const char* ssid = "your_ssid";
const char* password = "your_pass";
const int step_pin = 26; // example
const int dir_pin = 27;
const int enable_pin = 14;

WebServer server(80);
AccelStepper stepper(AccelStepper::DRIVER, step_pin, dir_pin);

volatile float current_angle = 0.0;
float target_angle = 0.0;
bool moving = false;
unsigned long last_move_ms = 0;

void handle_root() {
  server.send(200, "text/plain", "ESP32 Turntable READY");
}

void handle_status() {
  String res = "{";
  res += "\"state\": \"";
  res += moving ? "moving" : "idle";
  res += "\"";
  res += ", \"angle\": ";
  res += String(current_angle);
  res += "}";
  server.send(200, "application/json", res);
}

void handle_home() {
  // simple homing: set angle to 0
  target_angle = 0.0;
  moving = true;
  server.send(200, "application/json", "{\"result\":\"homing\"}");
}

void handle_rotate() {
  if (!server.hasArg("deg")) {
    server.send(400, "text/plain", "missing deg") ;
    return;
  }
  float d = server.arg("deg").toFloat();
  target_angle = fmod(d + 360.0, 360.0);
  moving = true;
  server.send(200, "application/json", "{\"result\":\"ok\"}");
}

void handle_step() {
  if (!server.hasArg("deg")) {
    server.send(400, "text/plain", "missing deg") ;
    return;
  }
  float d = server.arg("deg").toFloat();
  target_angle = fmod(current_angle + d + 360.0, 360.0);
  moving = true;
  server.send(200, "application/json", "{\"result\":\"ok\"}");
}

void setup() {
  Serial.begin(115200);
  pinMode(enable_pin, OUTPUT);
  digitalWrite(enable_pin, LOW);
  stepper.setMaxSpeed(1000);
  stepper.setAcceleration(500);

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println(" connected");

  server.on("/", handle_root);
  server.on("/status", handle_status);
  server.on("/home", handle_home);
  server.on("/rotate", handle_rotate);
  server.on("/step", handle_step);
  server.begin();
}

void loop() {
  server.handleClient();
  if (moving) {
    // convert target angle to steps (assume 200 steps/rev and gear ratio if any)
    float delta = target_angle - current_angle;
    if (delta > 180) delta -= 360;
    if (delta < -180) delta += 360;
    if (fabs(delta) < 0.1) {
      moving = false;
      current_angle = target_angle;
    } else {
      float step_delta = delta * 10.0; // scale factor: steps per deg (example)
      // move a small portion per loop to be non-blocking
      stepper.move((long)step_delta);
      stepper.run();
      current_angle += (step_delta / 10.0);
    }
  }
}

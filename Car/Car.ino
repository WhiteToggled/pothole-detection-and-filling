/* 
  ESP32 WebSocket realtime controller for L298N (2 motors) + MG90S servo.
  - WiFi AP: "ESP32-Car" (password "12345678") — change if you want STA mode.
  - Websocket server on port 81.
  - Minimal web UI served at "/" to control motion with press-and-hold.
  
  Libraries required:
    - WiFi (built-in)
    - WebSocketsServer (install "arduinoWebSockets")
    - ESP32Servo (already used)
*/

#include <WiFi.h>
#include <WebServer.h>
#include <WebSocketsServer.h>
#include <ESP32Servo.h>

// ========= network =========
const char *apSSID = "FillerBot";
const char *apPASS = "12345678";
WebServer httpServer(80);
WebSocketsServer webSocket = WebSocketsServer(81);

// ========= motor pinout (your pins) =========
// Motor A
int enA = 19;  // ENA pin (PWM)
int in1 = 18;  // IN1
int in2 = 5;   // IN2

// Motor B
int enB = 4;   // ENB pin (PWM)
int in3 = 17;  // IN3
int in4 = 16;  // IN4

// PWM properties
const int freq = 1000;
const int pwmChannelA = 0;
const int pwmChannelB = 1;
const int resolution = 8;
const int DEFAULT_DUTY = 150; // recommended starting duty (0..255)

// ========= servo =========
Servo filler;
const int SERVO_PIN = 13;
int currentAngle = 90;

// beeper
const int BEEPER_PIN = 27;      // change to your buzzer pin
const int BUILTIN_LED = 2;
const int LED_PIN = BUILTIN_LED;

// ========= runtime state =========
volatile bool forwardActive = false;
volatile bool backwardActive = false;
volatile bool leftActive = false;
volatile bool rightActive = false;
int currentDuty = DEFAULT_DUTY;

// ========= forward declarations =========
void handleRoot();
void webSocketEvent(uint8_t num, WStype_t type, uint8_t * payload, size_t length);
void startMotion();
void stopMotion();
void startDirection(const char* dir);
void stopDirection(const char* dir);
void sweepTo(int targetAngle);

// ============ setup =============
void setup() {
  Serial.begin(115200);
  delay(100);
  Serial.println("hello");

  // Motor direction pins
  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);
  pinMode(in3, OUTPUT);
  pinMode(in4, OUTPUT);

  // Setup PWM channels + attach pins
  if (!ledcAttachChannel(enA, freq, resolution, pwmChannelA)) {
    Serial.println("WARN: ledcAttachChannel failed for enA");
  }
  if (!ledcAttachChannel(enB, freq, resolution, pwmChannelB)) {
    Serial.println("WARN: ledcAttachChannel failed for enB");
  }

  // Set motors off initially
  stopMotors();

  // Setup servo
  filler.attach(SERVO_PIN);
  currentAngle = 90;
  filler.write(currentAngle);
  delay(200);

  // BeeperLED setup
  pinMode(BEEPER_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(BEEPER_PIN, LOW);
  digitalWrite(LED_PIN, LOW);

  // Start WiFi AP
  WiFi.softAP(apSSID, apPASS);
  IPAddress IP = WiFi.softAPIP();
  Serial.print("AP IP: ");
  Serial.println(IP);

  // HTTP route for index
  httpServer.on("/", handleRoot);
  httpServer.begin();
  Serial.println("HTTP server started");

  // WebSocket server
  webSocket.begin();
  webSocket.onEvent(webSocketEvent);
  Serial.println("WebSocket server started on port 81");
}

// ============ loop =============
void loop() {
  httpServer.handleClient();
  webSocket.loop();

  // Continuously ensure motion state is applied
  startMotion(); // this only writes pins according to flags (non-blocking)
}

// ============ web handler & HTML UI ============
void handleRoot() {
  String html = R"rawliteral(
  <!doctype html>
  <html>
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1"/>
    <title>ESP32 Car WS</title>
    <style>
      body{ font-family: Arial; text-align:center; padding:10px; }
      .row { display:flex; justify-content:center; gap:12px; margin:12px; }
      button { width:110px; height:70px; font-size:18px; border-radius:8px; }
      #status { margin-top:8px; color:green; }
    </style>
  </head>
  <body>
    <h2>ESP32 Car - WebSocket</h2>
    <div class="row">
      <button id="forward">Forward</button>
    </div>
    <div class="row">
      <button id="left">Left</button>
      <button id="stop">Stop</button>
      <button id="right">Right</button>
    </div>
    <div class="row">
      <button id="back">Backward</button>
    </div>
    <div class="row">
      <button id="fill">Fill</button>
    </div>
    <div id="status">connecting...</div>

    <script>
      let ws;
      const status = document.getElementById('status');

      function connect() {
        const loc = window.location.hostname;
        ws = new WebSocket('ws://' + loc + ':81/');
        ws.onopen = () => { status.textContent = 'connected'; status.style.color='green'; };
        ws.onclose = () => { status.textContent = 'disconnected - retrying'; status.style.color='red'; setTimeout(connect, 1000); };
        ws.onmessage = (evt) => { console.log('recv', evt.data); };
      }
      connect();

      function send(msg) {
        if (ws && ws.readyState === WebSocket.OPEN) ws.send(msg);
      }

      function wireButton(id, action) {
        const btn = document.getElementById(id);
        btn.addEventListener('mousedown', ()=>send('down:' + action));
        btn.addEventListener('mouseup', ()=>send('up:' + action));
        btn.addEventListener('mouseleave', ()=>send('up:' + action));
        btn.addEventListener('touchstart', (e)=>{ e.preventDefault(); send('down:' + action); });
        btn.addEventListener('touchend', (e)=>{ e.preventDefault(); send('up:' + action); });
      }

      wireButton('forward', 'forward');
      wireButton('back', 'backward');
      wireButton('left', 'left');
      wireButton('right', 'right');

      document.getElementById('stop').addEventListener('click', ()=>send('stop'));
      document.getElementById('fill').addEventListener('click', ()=>send('fill'));
    </script>
  </body>
  </html>
  )rawliteral";

  httpServer.send(200, "text/html", html);
}

// ============ WebSocket message handling ============
// Messages format:
//   "down:forward"  -- start moving forward (on button press)
//   "up:forward"    -- stop moving forward (on button release)
//   "stop"          -- immediate stop
//   "sweep:ANGLE"   -- sweep servo to ANGLE (0..180)
void webSocketEvent(uint8_t num, WStype_t type, uint8_t * payload, size_t length) {
  if (type == WStype_TEXT) {
    String msg = String((char*)payload);
    Serial.printf("WS msg: %s\n", msg.c_str());

    if (msg == "stop") {
      forwardActive = backwardActive = leftActive = rightActive = false;
      stopMotors();
      return;
    }

    if (msg == "fill") {
      doFill();
      return;
    }

    if (msg.startsWith("down:")) {
      String act = msg.substring(5);
      startDirection(act.c_str());
      return;
    }
    if (msg.startsWith("up:")) {
      String act = msg.substring(3);
      stopDirection(act.c_str());
      return;
    }
  }
}

// ============ Fill routine ============
void doFill() {
  // move servo 90 → 180
  for (int a = 90; a <= 180; a++) {
    filler.write(a);
    digitalWrite(BEEPER_PIN, HIGH);
    digitalWrite(LED_PIN, HIGH);
    delay(12);
    digitalWrite(BEEPER_PIN, LOW);
    digitalWrite(LED_PIN, LOW);
    delay(12);
  }
  // then 180 → 90
  for (int a = 180; a >= 90; a--) {
    filler.write(a);
    digitalWrite(BEEPER_PIN, HIGH);
    digitalWrite(LED_PIN, HIGH);
    delay(12);
    digitalWrite(BEEPER_PIN, LOW);
    digitalWrite(LED_PIN, LOW);
    delay(12);
  }
  currentAngle = 90;
}

// ============ Direction state handlers ============
void startDirection(const char* dir) {
  if (strcmp(dir, "forward") == 0)       forwardActive = true;
  else if (strcmp(dir, "backward") == 0) backwardActive = true;
  else if (strcmp(dir, "left") == 0)     leftActive = true;
  else if (strcmp(dir, "right") == 0)    rightActive = true;
  // apply immediately
  startMotion();
}

void stopDirection(const char* dir) {
  if (strcmp(dir, "forward") == 0)       forwardActive = false;
  else if (strcmp(dir, "backward") == 0) backwardActive = false;
  else if (strcmp(dir, "left") == 0)     leftActive = false;
  else if (strcmp(dir, "right") == 0)    rightActive = false;
  // if no direction active, ensure motors stop
  if (!forwardActive && !backwardActive && !leftActive && !rightActive) {
    stopMotors();
  } else {
    // apply remaining active states
    startMotion();
  }
}

// startMotion() interprets flags and sets motor outputs accordingly.
// Non-blocking: just sets pins and PWM.
void startMotion() {
  // Priority: if left/right active, perform turning behavior.
  if (leftActive) {
    // spin left: motor A backward, motor B forward
    digitalWrite(in1, HIGH);
    digitalWrite(in2, LOW);
    digitalWrite(in3, HIGH);
    digitalWrite(in4, LOW);
    ledcWrite(enA, currentDuty);
    ledcWrite(enB, currentDuty);
    return;
  }

  if (rightActive) {
    // spin right: motor A forward, motor B backward
    digitalWrite(in1, LOW);
    digitalWrite(in2, HIGH);
    digitalWrite(in3, LOW);
    digitalWrite(in4, HIGH);
    ledcWrite(enA, currentDuty);
    ledcWrite(enB, currentDuty);
    return;
  }

  // forward / backward
  if (forwardActive) {
    digitalWrite(in1, LOW);
    digitalWrite(in2, HIGH);   // Motor A forward (as your wiring currently expects)
    digitalWrite(in3, HIGH);
    digitalWrite(in4, LOW);    // Motor B forward
    ledcWrite(enA, currentDuty);
    ledcWrite(enB, currentDuty);
    return;
  }

  if (backwardActive) {
    digitalWrite(in1, HIGH);
    digitalWrite(in2, LOW);    // Motor A backward
    digitalWrite(in3, LOW);
    digitalWrite(in4, HIGH);   // Motor B backward
    ledcWrite(enA, currentDuty);
    ledcWrite(enB, currentDuty);
    return;
  }

  // no direction active -> ensure stop
  stopMotors();
}

// ============ Motor helpers ============
void stopMotors() {
  // disable PWM on EN pins
  ledcWrite(enA, 0);
  ledcWrite(enB, 0);

  // set direction pins low (coast)
  digitalWrite(in1, LOW);
  digitalWrite(in2, LOW);
  digitalWrite(in3, LOW);
  digitalWrite(in4, LOW);
}

// ============ Servo sweep (blocking small routine) ============
void sweepTo(int targetAngle) {
  if (targetAngle < 0) targetAngle = 0;
  if (targetAngle > 180) targetAngle = 180;

  // smooth move from currentAngle to targetAngle
  if (targetAngle == currentAngle) return;
  if (targetAngle > currentAngle) {
    for (int a = currentAngle; a <= targetAngle; ++a) {
      filler.write(a);
      delay(12);
    }
  } else {
    for (int a = currentAngle; a >= targetAngle; --a) {
      filler.write(a);
      delay(12);
    }
  }
  currentAngle = targetAngle;
}

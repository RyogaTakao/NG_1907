#include <M5Stack.h>
#include <WiFi.h>
#include <WiFiClient.h>

//各種設定
//ネットワーク設定
//セキュリティもクソもないです。
#define SSID "NG1907"
#define PASSWORD "Shikishima"
#define SRV_IP_ADDR "192.168.137.42"
#define SRV_PORT 12345
#define CONNECTION_WAIT 1000

//シリアル通信設定
#define BAUD_RATE 115200

//LCD設定
#define LCD_WIDTH 320
#define LCD_HEIGHT 240
#define DOTS_DIV 30
#define GREY 0x7BEF
#define REDRAW 20

//GPIO設定
#define PIN_INPUT 36
#define THRESHOLD 550   // Adjust this number to avoid noise when idle

//みんな大好きグローバル変数
//接頭辞 glb_ をつけてください。
WiFiClient glb_wifi_client;

/*
  M5Stackの各種セットアップを行います。

  @param なし [なし]: この関数に引数はありません。
  @return なし [なし]: この関数は戻り値がありません。
*/
void setup() {
  M5.begin();
  //dacWrite(25, 0); // Speaker OFF

  Serial.begin(BAUD_RATE);

  delay(500);

  pinMode(PIN_INPUT, INPUT);

  //connectAP();
  //connectTCP();

  Serial.printf("All system ready.\n");
}

/*
  WiFiに接続します。

  @param なし [なし]: この関数に引数はありません。
  @return N/A [bool]: 接続が成功したか否か。
*/
bool connectAP(void) {
  //設定
  unsigned int patience = 30;

  Serial.printf("Trying to connect to AP");

  //接続
  WiFi.begin(SSID, PASSWORD);
  while (patience--) {
    if (WiFi.status() == WL_CONNECTED) {
      Serial.printf("Connected!\n");
      return true;
    } else {
      Serial.printf(".");
      delay(CONNECTION_WAIT);
    }
  }

  Serial.printf("Connection timed out.\n");
  return false;
}

/*
  TCP接続を確立します。

  @param なし [なし]: この関数に引数はありません。
  @return N/A [bool]: 接続が成功したか否か。
*/
bool connectTCP(void){
  //設定
  unsigned int patience = 30;

  Serial.printf("Trying to connect to server");
  while (patience--) {
    if (glb_wifi_client.connect(SRV_IP_ADDR, SRV_PORT)) {
      Serial.printf("TCP connection established.\n");
      return true;
    } else {
      Serial.printf(".");
      delay(CONNECTION_WAIT);
    }
  }

  Serial.printf("Connection timed out.\n");
  return false;
}

void loop() {
  uint16_t heart = analogRead(PIN_INPUT);
  glb_wifi_client.printf("%d\n", heart);
  M5.Lcd.setCursor(1, 1);
  M5.Lcd.setTextSize(3);
  M5.Lcd.printf("Raw Input: %d", heart);
  delay(10);
}

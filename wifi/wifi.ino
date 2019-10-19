#include <M5Stack.h>
#include <WiFi.h>
#include <WiFiClient.h>

//各種設定
//セキュリティもクソもないです。
#define SSID "NG1907"
#define PASSWORD "Shikishima"
#define SRV_IP_ADDR "192.168.137.42"
#define SRV_PORT 12345
#define CONNECTION_WAIT 1000

#define BAUD_RATE 115200

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

  Serial.begin(BAUD_RATE);
  delay(500);
  Serial.printf("\nM5 ready!\n");

  connectAP();
  connectTCP();
}

/*
  WiFiに接続します。

  @param なし [なし]: この関数に引数はありません。
  @return N/A [bool]: 接続が成功したか否か。
*/
bool connectAP(void) {
  //設定
  unsigned int patience = 50;

  Serial.printf("Trying to connect to AP...\n");

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
  unsigned int patience = 50;

  Serial.printf("Trying to connect to server...\n");
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
  static unsigned int count = 0;
  glb_wifi_client.printf("%d\n", count++);
  delay(1000);
}
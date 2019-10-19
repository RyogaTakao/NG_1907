#include <M5Stack.h>
#include <WiFi.h>
#include <ESPmDNS.h>
#include <WiFiClient.h>
#include <Preferences.h>

/*
  M5Stackの各種セットアップを行います。

  @param なし [なし]: この関数に引数はありません。
  @return なし [なし]: この関数は戻り値がありません。
*/
void setup() {
  M5.begin();

  Serial.begin(115200);
  delay(500);
  Serial.printf("\nM5 ready!\n");

  connect();
  post();
}

/*
  WiFiに接続します。

  @param なし [なし]: この関数に引数はありません。
  @return N/A [bool]: 接続が成功したか否か。
*/
bool connect() {
  //設定
  const char ssid[] = "NG1907";
  const char password[] = "Shikishima";
  unsigned int patience = 50;

  //接続
  WiFi.begin(ssid, password);
  while (patience--) {
    if (WiFi.status() == WL_CONNECTED) {
      Serial.printf("Connected!\n");
      return true;
    } else {
      Serial.printf(".");
      delay(500);
    }
  }

  Serial.printf("Connection timed out.\n");
  return false;
}

/*
  
*/
void post() {

}

void loop() {
}
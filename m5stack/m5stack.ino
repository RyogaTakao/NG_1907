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

//GPIO設定
#define PIN_INPUT 36

//波形データ用リングバッファの大きさです。
#define WAVE_BUFFER 1024

//測定用の定数
#define PEAK_THRESHOLD 0.99 //リングバッファの最大値×これ　より大きい信号を新たなピークとします。
#define MIN_PEAK_DELTA 300000 //これより短い周期のピークを破棄します。

//みんな大好きグローバル変数
//接頭辞 glb_ をつけてください。
WiFiClient glb_wifi_client;

/*
  M5Stackの各種セットアップを行います。

  @param なし [なし]: この関数に引数はありません。
  @return なし [なし]: この関数は戻り値がありません。
*/
void setup() {
  //初期化
  M5.begin();

  //スピーカーがうるさいので
  //M5.Speaker.beep();
  dacWrite(25, 0); 

  //シリアル通信
  Serial.begin(BAUD_RATE);
  delay(500);

  //LCD
  M5.Lcd.setTextSize(3);

  //心拍計
  pinMode(PIN_INPUT, INPUT);

  //Wi-Fi
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

void loop(){
  unsigned int level = analogRead(PIN_INPUT);
  static unsigned int wave[WAVE_BUFFER] = {};
  static unsigned int index = 0;
  static unsigned long last_peak = 0;
  static float bpm = 65;
  double correlation[WAVE_BUFFER] = {};

  M5.Lcd.setCursor(1, 1);
  M5.Lcd.printf("Input: %4d mV\n", level);

  //リングバッファ的な
  if (index < WAVE_BUFFER) {
    wave[index++] = level;
  } else {
    index = 0;
  }
  
  //乗るしかない、このビッグウェーブに
  if (level > wave_max(wave) * PEAK_THRESHOLD) {
    unsigned long new_peak = micros();
    unsigned int delta = new_peak - last_peak;

    //頂上を2回とってバグるの防止
    if (delta > MIN_PEAK_DELTA) {
      //マイクロ秒→BPM  
      bpm = 1000000.0 / delta * 60;
      last_peak = new_peak;
    }
  }

  M5.Lcd.printf("B P M: %3.1f\n", bpm);

  Serial.printf("%d\n", level);
}

unsigned int wave_max(unsigned int *arr){
  unsigned int temp = 0;

  for (int i=0; i < WAVE_BUFFER; i++) {
    if (arr[i] > temp) {
      temp = arr[i];
    }
  }

  return temp;
}

/*
double corr(unsigned int *arr, int m) {
  double ret = 0;

  for (int i=0; i < WAVE_BUFFER; i++) {
    int j = i - m;

    if (j < 0) {
      //rotation
      j += WAVE_BUFFER;
    }

    ret += arr[i] * arr[j];
  }

  return ret / WAVE_BUFFER;
}
*/
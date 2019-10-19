#include <M5Stack.h>
#include <WiFi.h>
#include <WiFiClient.h>
#include "arduinoFFT.h"

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

//FFT設定
//FFT_SAMPLES は 2^n でなければなりません。
#define FFT_SAMPLES 16
#define FFT_SAMPLING_FREQUENCY 4

arduinoFFT FFT = arduinoFFT();

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
  dacWrite(25, 0); 

  //シリアル通信
  Serial.begin(BAUD_RATE);
  delay(500);

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

void loop() {
  //1サンプルの間隔
  const unsigned int sampling_period_us = round(1000000*(1.0/FFT_SAMPLING_FREQUENCY));

  //波形データ格納用
  double real[FFT_SAMPLES], imaginary[FFT_SAMPLES];

  //サンプリング
  for (unsigned int i=0; i < FFT_SAMPLES; i++) {
    unsigned long microseconds = micros();

    real[i] = analogRead(PIN_INPUT);
    imaginary[i] = 0;

    while(micros() < (microseconds + sampling_period_us));
  }

  //FFT
  FFT.Windowing(real, FFT_SAMPLES, FFT_WIN_TYP_HAMMING, FFT_FORWARD);
  FFT.Compute(real, imaginary, FFT_SAMPLES, FFT_FORWARD);
  FFT.ComplexToMagnitude(real, imaginary, FFT_SAMPLES);

  //最もエネルギーの大きい周波数を取り出す(Hz)
  double peak = FFT.MajorPeak(real, FFT_SAMPLES, FFT_SAMPLING_FREQUENCY);

  //BPMに変換
  unsigned int bpm = peak * 60;

  //画面
  M5.Lcd.setCursor(1, 1);
  M5.Lcd.setTextSize(3);
  M5.Lcd.printf("%3d BPM", bpm);

  //送信
  glb_wifi_client.printf("%d\n", bpm);
}

#include <M5Stack.h>
#include <WiFi.h>

//  # 各種設定
//  ## ネットワーク設定
const char *SSID = "NG1907";
const char *PSK = "Shikishima";
const char *SRV_IP = "192.168.137.42";
uint16_t SRV_PORT = 12345;
uint16_t CLIENT_PORT = 12345;
uint32_t CONNECTION_WAIT = 1000;

//  ## シリアル通信設定
#define BAUD_RATE 115200

//  ## GPIO設定
#define PIN_INPUT 36

//  ## 波形データ
#define WAVE_BUFFER 32

//  ## 測定用定数
#define PEAK_THRESHOLD 0.99   //リングバッファの最大値×これ　より大きい信号を新たなピークとします。
#define MIN_PEAK_DELTA 300000 //これより短い周期のピークを破棄します。

//  ## 色
const uint16_t FORECOLOR = M5.Lcd.color565(252,120,177);

//　## ユーザー
#define USER_ID_LENGTH 128
char user_id[USER_ID_LENGTH] = {};
char twitter_id[USER_ID_LENGTH] = {};

bool btnChangeFlg = false;
uint8_t displayMode = 0; //  0: BPM  1: QR

WiFiClient glb_wifi_client;
WiFiServer glb_wifi_server(CLIENT_PORT);

/*
  M5Stackの各種セットアップを行います。

  @param なし [なし]: この関数に引数はありません。
  @return なし [なし]: この関数は戻り値がありません。
*/
void setup()
{
    //初期化
    M5.begin();
    Serial.begin(BAUD_RATE);
    
    //スピーカーがうるさいので
    dacWrite(25, 0);

    //  画像描画
    M5.Lcd.drawJpgFile(SD, "/EMOVE.jpg");

    //  心拍計
    pinMode(PIN_INPUT, INPUT);
    analogReadResolution(12);
    analogSetWidth(12);
    analogSetCycles(8);
    analogSetSamples(8);
    analogSetClockDiv(1);
    analogSetAttenuation(ADC_11db);
    adcAttachPin(PIN_INPUT);

    //  WiFi
    connectAP();
    Serial.println(WiFi.localIP());
    glb_wifi_server.begin();

    // ユーザーID
    File userid_file = SD.open("/id.txt", FILE_READ);
    if (userid_file) {
        int c = 0;
        while (userid_file.available()) {
            if (c++ >= USER_ID_LENGTH) break;
            user_id[c++] = userid_file.read();
        }
    }
    userid_file.close();

    M5.Lcd.fillScreen(TFT_WHITE);

    Serial.printf("All system ready.\n");
}

/*
  WiFiに接続します。

  @param なし [なし]: この関数に引数はありません。
  @return N/A [bool]: 接続が成功したか否か。
*/
bool connectAP(void)
{
    //  設定
    unsigned int patience = 30;

    Serial.printf("Trying to connect to AP");

    //  接続
    WiFi.begin(SSID, PSK);
    while (patience--)
    {
        if (WiFi.status() == WL_CONNECTED)
        {
            Serial.printf("Connected!\n");
            return true;
        }
        else
        {
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
bool connectTCP(void)
{
    //設定
    unsigned int patience = 30;

    Serial.printf("Trying to connect to server");
    while (patience--)
    {
        if (glb_wifi_client.connect(SRV_IP, SRV_PORT))
        {
            Serial.printf("TCP connection established.\n");
            return true;
        }
        else
        {
            Serial.printf(".");
            delay(CONNECTION_WAIT);
        }
    }

    Serial.printf("Connection timed out.\n");
    return false;
}

/*
    メインループです。

    @param なし [なし]: この関数に引数はありません。
    @return なし [なし]: この関数は戻り値がありません。
*/
void loop()
{
    unsigned int level = analogRead(PIN_INPUT);
    static unsigned int wave[WAVE_BUFFER] = {};
    static unsigned int index = 0;
    static unsigned long last_peak = 0;
    static float bpm = 0;
    static float bpm_history[10] = {};
    static unsigned int bpm_index = 0;
    static unsigned int count = 0;

    //リングバッファ的な
    if (++index >= WAVE_BUFFER)
    {
        index = 0;
    }
    wave[index] = level;

    //大きい波
    const unsigned int wall = wave_max(wave) * PEAK_THRESHOLD;
    if (wave[index] > wall)
    {
        unsigned long new_peak = micros();
        unsigned long delta = new_peak - last_peak;

        //頂上を2回とってバグるの防止
        if (delta > MIN_PEAK_DELTA)
        {
            //選ばれしデータ
            if (++bpm_index >= 10)
            {
                bpm_index = 0;
            }

            last_peak = new_peak;

            //マイクロ秒→BPM
            bpm_history[bpm_index] = 1000000.0 / delta * 60;
        }
    }

    //メジアン
    for (int i = 0; i < 10 - 1; i++)
    {
        int j = i;

        for (int k = i; k < 10; k++)
        {
            if (bpm_history[k] < bpm_history[j])
            {
                j = k;
            }
        }

        if (i < j)
        {
            double v = bpm_history[i];
            bpm_history[i] = bpm_history[j];
            bpm_history[j] = v;
        }
    }

    // Wi-Fi 受信
    WiFiClient client = glb_wifi_server.available();
    if (client) {
        int c = 0;
        String concat = "";
        while (client.connected()) {
            if (client.available()) {
                char ch = client.read();
                concat += ch;

                if (c++ < USER_ID_LENGTH) {
                    twitter_id[c] = ch;
                }
            }
        }
        Serial.printf(concat.c_str());
        client.stop();
    }

    //  ボタン検出
    M5.update();
    if (M5.BtnA.isPressed())
    {
        displayMode = 0;
        btnChangeFlg = true;
    }
    else if (M5.BtnB.isPressed())
    {
        displayMode = 1;
        btnChangeFlg = true;
    }
    else if (M5.BtnC.isPressed())
    {
        displayMode = 2;
        btnChangeFlg = true;
    }

    //  ボタンによる画面切り替え
    if (btnChangeFlg)
    {
        if (displayMode == 0)
        {
            M5.Lcd.fillScreen(TFT_WHITE);
        }
        else if (displayMode == 1)
        {
                M5.Lcd.fillScreen(TFT_WHITE);
                M5.Lcd.qrcode(twitter_id);
        }
        else if (displayMode == 2)
        {
                M5.Lcd.drawJpgFile(SD, "/EMOVE.jpg");
        }
        btnChangeFlg = false;
    }

    if (displayMode == 0 && bpm_history[5] != bpm)
    {
        bpm = bpm_history[5];

        M5.Lcd.fillEllipse(160, 120, 90, 90, FORECOLOR);
        M5.Lcd.setTextColor(TFT_WHITE, FORECOLOR);
        M5.Lcd.setCursor(100, 90);
        M5.Lcd.setTextSize(8);
        M5.Lcd.printf("%03.0f", bpm);

        connectTCP();
        glb_wifi_client.printf("{\"userID\": \"%s\", \"BPM\": \"%.0f\"}\n", user_id, bpm);
        //Serial.printf("{\"userID\": \"%s\", \"BPM\": \"%.0f\"}\n", user_id, bpm); //debug
    }

   Serial.printf("%d\n", wave[index]); //debug
}

/*
    波形データ中の最大値を返します。

    @param *arr (unsigned int): 波形データ
    @return temp (unsigned int): 波形データの最大値
*/
unsigned int wave_max(unsigned int *arr)
{
    unsigned int temp = 0;

    for (int i = 0; i < WAVE_BUFFER; i++)
    {
        if (arr[i] > temp)
        {
            temp = arr[i];
        }
    }

    return temp;
}

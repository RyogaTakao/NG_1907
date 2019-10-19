#include <M5Stack.h>
#include <WiFi.h>
#include <arduinoFFT.h>

//  # 各種設定
//  ## ネットワーク設定
const char *SSID = "NG1907";
const char *PSK = "Shikishima";
const char *SRV_IP = "192.168.137.42";
uint16_t SRV_PORT = 12345;
uint32_t CONNECTION_WAIT = 1000;

//  ## シリアル通信設定
#define BAUD_RATE 115200

//  ## GPIO設定
#define PIN_INPUT 36

//  ## FFT設定
//  ## FFT_SAMPLES must be 2^n
#define FFT_SAMPLES 16
#define FFT_SAMPLING_FREQUENCY 4.0
double vReal[FFT_SAMPLES];
double vImag[FFT_SAMPLES];
unsigned long newTime, oldTime;

bool btnChangeFlg = false;
uint8_t displayMode = 0; //  0: BPM  1: QR
bool displayDraw = false;

WiFiClient glb_wifi_client;
arduinoFFT glb_fft = arduinoFFT();

void setup()
{
    Serial.begin(BAUD_RATE);
    M5.begin();
    dacWrite(25, 0);

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
    connectTCP();

    Serial.printf("All system ready.\n");
    newTime = millis();
}

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

void loop()
{
    uint64_t sum = 0;
    for (int i = 0; i < FFT_SAMPLES; i++)
    {
        adcStart(PIN_INPUT);
        vReal[i] = adcEnd(PIN_INPUT);
        vImag[i] = 0;
        sum += (uint64_t)vReal[i];
    }
    uint16_t ave = (uint16_t)(sum / FFT_SAMPLES);
    for (int i = 0; i < FFT_SAMPLES; i++)
    {
        if (vReal[i] > ave){
            vReal[i] -= ave;
        }
        else{
            vReal[i] = 0;
        }
    }
    glb_fft.Windowing(vReal, FFT_SAMPLES, FFT_WIN_TYP_HAMMING, FFT_FORWARD);
    glb_fft.Compute(vReal, vImag, FFT_SAMPLES, FFT_FORWARD);
    glb_fft.ComplexToMagnitude(vReal, vImag, FFT_SAMPLES);
    double peak = glb_fft.MajorPeak(vReal, FFT_SAMPLES, FFT_SAMPLING_FREQUENCY);
    unsigned int bpm = (unsigned int)(peak * 60.0);

    oldTime = newTime;
    newTime = millis();

    unsigned long dt = oldTime - newTime;

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

    //  ボタンによる画面切り替え
    if (btnChangeFlg == true)
    {
        if (displayMode == 0)
        {
            M5.Lcd.fillScreen(TFT_BLACK);
            displayDraw = false;
        }
        else
        {
            if (displayDraw == false)
            {
                M5.Lcd.fillScreen(TFT_BLACK);
                M5.Lcd.qrcode("http://www.m5stack.com");
                displayDraw = true;
            }
        }
        btnChangeFlg = false;
    }

    if (displayMode == 0)
    {
        M5.Lcd.setCursor(1, 3);
        M5.Lcd.setTextSize(3);
        M5.Lcd.printf("%3d BPM\nAVE %d", bpm, ave);
    }

    //  通信エラー対策
    if (glb_wifi_client.connected() == 0){
        glb_wifi_client.stop();
        connectTCP();
    }
    glb_wifi_client.printf("%d\n", bpm);
}

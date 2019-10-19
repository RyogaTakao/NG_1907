import socket
import emove_json
import Main

def main():
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.bind(("192.168.137.42", 12345)) #ホストとポートは隠します
    soc.listen(1)
    soc, addr = soc.accept()
    while True:
        data = soc.recv(1024) #1024バイトづつ分割して受信する
        if not data:
            break
        #print(data)
        pulse_data = int(data.decode())
        print('HeartBeat: %d[bpm]'%pulse_data)
        emove_json.send_bpm(Main.userID, Main.musicID, pulse_data)
        emove_json.send_json(Main.JSON_FILE_PATH, Main.SEND_URL)

if __name__ == '__main__':
    main()
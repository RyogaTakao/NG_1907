import socket
import emove_json
import Main
import json

def receive_bpm():
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    soc.bind(("192.168.137.42", 12345)) #ホストとポートは隠します
    soc.listen(1)
#    soc, addr = soc.accept()
    while True:
        new_sock, (remote_host, remote_remport) = soc.accept()
        print('[FD:{}]Accept:{}:{}'.format(new_sock.fileno(), remote_host, remote_remport))
        data = new_sock.recv(1024) #1024バイトづつ分割して受信する
        if not data:
            continue
        data = data.decode()
        print(data, end='')
        try:
            jsonDict = json.loads(data)
            with open(Main.JSON_FILE_PATH) as f:
                savedDict = json.load(f)
                emove_json.send_bpm(jsonDict['userID'], savedDict[jsonDict['userID']]['twitterID'], jsonDict['BPM'], savedDict[jsonDict['userID']]['name'], savedDict[jsonDict['userID']]['age'], savedDict[jsonDict['userID']]['sex'])
        except Exception:
            print('型が違います')
        new_sock.close()

def receive_account():
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    soc.bind(("192.168.137.42", 23456)) #ホストとポートは隠します
    soc.listen(1)
    #new_sock, (remote_host, remote_remport) = soc.accept()
    #print('[FD:{}]Accept:{}:{}'.format(new_sock.fileno(), remote_host, remote_remport))
    with open(Main.JSON_FILE_PATH) as f:
        while True:
            new_sock, (remote_host, remote_remport) = soc.accept()
            print('[FD:{}]Accept:{}:{}'.format(new_sock.fileno(), remote_host, remote_remport))
            data = new_sock.recv(1024) #1024バイトづつ分割して受信する
            if not data:
                continue
            print(data)
            data = data.decode()
            print(data, end='')
            try:
                receivedDict = json.loads(data)
                fileDict = json.load(f)
                fileDict[receivedDict['userID']] = {"name": receivedDict['name'],"twitterID": "@shikishijun", "age": receivedDict['age'], "sex": receivedDict['sex']}
            except Exception:
                print('型が違います')
            new_sock.close()

if __name__ == '__main__':
    #receive_bpm()
    receive_account()
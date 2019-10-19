import requests
import json

URL = ''

def send_bpm(userID, musicID, BPM):
    #POSTパラメータは二つ目の引数に辞書で指定する
    response = requests.post(
        URL,
        json.dumps({'userID': userID, 'musicID': musicID, 'BPM': BPM}),
        headers={'Content-Type': 'application/json'})    

if __name__=='__main__':
    send_bpm('5555', '144', '20')
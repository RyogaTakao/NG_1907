import json
import requests

JSON_FILE_PATH = '/home/pi/EMOVE/test_bpm.json'
SEND_URL = 'https://jphacks_noblesseoblige07.serveo.net/bpm'

def send_bpm(userID, musicID, BPM):
    #POSTパラメータは二つ目の引数に辞書で指定する
    response = requests.post(
        SEND_URL,
        json.dumps({'userID': userID, 'musicID': musicID, 'BPM': BPM}),
        headers={'Content-Type': 'application/json'})    

def save_music_list_json():
    dic = {}
    musicID = '4567'
    name = 'no1'
    genre = 'Pop'
    part = {
        "Name": name,
        "Genre": genre
    }
    dic[musicID] = part
    a = open(JSON_FILE_PATH, 'w')
    json.dump(dic, a)

def send_json(path, url):
    file = {'upload_file': open(path, 'rb')}
    headers = {'content-type': 'application/json'}
    res = requests.post(url, files=file, headers=headers)

def main():
    userID = '3125'
    musicID = '7654'
    BPM = 70
    #save_music_list_json()
    send_bpm(userID, musicID, BPM)

if __name__ == "__main__":
    main()
import json
import requests

JSON_FILE_PATH = '/home/pi/EMOVE/test_bpm.json'
SEND_URL = ''

def save_bpm_json(userID, musicID, BPM):
    dic = {
        "userID": userID,
        "musicID": musicID,
        "BPM": BPM
    }
    a = open(JSON_FILE_PATH, 'w')
    json.dump(dic, a)

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
    userID = '3120'
    musicID = '7654'
    BPM = 65
    #save_music_list_json()
    save_bpm_json(userID, musicID, BPM)
    send_json(JSON_FILE_PATH, SEND_URL)

if __name__ == "__main__":
    main()

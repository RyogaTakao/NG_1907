import json
import requests

JSON_FILE_PATH = '/home/pi/EMOVE/test_bpm.json'
SEND_URL = 'https://jphacks_noblesseoblige07.serveo.net/bpm'

def send_bpm(userID, twitterID, BPM, name, age, sex):
    #POSTパラメータは二つ目の引数に辞書で指定する
    dict = json.dumps({
        'userID': userID,
        'twitterID': twitterID,
        'BPM': BPM,
        'name': name,
        'age': age,
        'sex': sex})
    print(dict)
    response = requests.post(
        SEND_URL,
        dict,
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
    BPM = 70
    twitterID = '@shikishijun'
    name = 'shikishima'
    age = 22
    sex = 'male'
    send_bpm(userID, twitterID, BPM, name, age, sex)

if __name__ == "__main__":
    main()
# coding: UTF-8

from flask import Flask, request
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import pytz
import random
import google
import socket
import math
from datetime import datetime
import time


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

cred =credentials.Certificate('<firebase_key>')
app_firebase = firebase_admin.initialize_app(cred)
db = firestore.client()
num = 0
user_bpm = []
bpm_time = []


# data_user = {}  # /userで登録

# timestampをunixtimeに変換
def timeChanger(textTime):
    return textTime.timestamp()

textStartTime = timeChanger(datetime.now(pytz.timezone('Asia/Tokyo')))

# 経過時間を演算
def ElapsedTime(nowTime):
    return math.floor(timeChanger(nowTime)) - textStartTime

# 時刻ごとの盛り上がり度の登録時の演算　（修正あり）
# 盛り上がり度 = 現在時刻でのbpmの平均　と考える
def GetExcitementForTime(BPM):  # 引数は現在の時刻(開始時刻からの経過時間)
    bpmSum = 0
    
    # UserIDごとに[time, bpm]の形式で保存している二次元配列　(修正)
    listDataOfMusicData = BPM

    # 時刻ごとのbpmの平均
    for data in listDataOfMusicData:
        bpmSum += data[1]
    bpmAverage = bpmSum / len(listDataOfMusicData)


    return bpmAverage

# 共分散
def GetCovariance(listData):
    averageX = 0
    averageY = 0
    for data in listData:
        averageX += data[0]
        averageY += data[1]

    averageX = averageX / len(listData)
    averageY = averageY / len(listData)

    covariance = 0

    for data in listData:
       covariance += (data[0] - averageX) * (data[1] - averageY)

    return covariance / len(listData) 

# 分散
def GetDispersion(listData):
    averageX = 0
    for data in listData:
        averageX += data[0]

    averageX = averageX / len(listData)

    dispersion = 0
    for data in listData:
        dispersion += (data[0] - averageX) * (data[0] - averageX)
    
    return dispersion / len(listData)

# 最小二乗法による回帰直線の傾きを演算　（修正あり）
def LeastSquareMethod(leng):

    # excitementデータベースから取得した盛り上がり度データ(新しい順)[time, bpm]
    excitementData = leng
    # excitement.append(excitementData)

    return GetCovariance(excitementData[:num]) / GetDispersion(excitementData[:num])

# 乱数
def RandomNumber(num):
    return random.randrange(num)

# 同じ系統の曲を抽出（論理積）
def musicSiftAnd(data, bpm, genre):
    musicData = data
    resultData = []
    for d in musicData:
        if d[1] == bpm and d[2] == genre:
            resultData.append(d)
    return resultData

# 同じ系統の曲を抽出（論理和）
def musicSiftOr(data, bpm, genre):
    musicData = data
    resultData = []
    for d in musicData:
        if d[1] == bpm or d[2] == genre:
            resultData.append(d)
    return resultData

# 選曲関数　(修正あり)
def SelectMusic(nowMusicID, data):    # 引数は現在の流れている曲のID
    # 引数のnowMusicIDから現在の曲のbpmを取得する
    musicData = data
    nowMusicBpmType = 0
    nowMusicGenre = ""
    count = 0
    for data in musicData:
        if data[0] == nowMusicID:
            nowMusicBpmType = data[1]
            nowMusicGenre = data[2]
            musicData.pop(count)
        count += 1


    # 最近5回分のデータの傾向を演算
    inclination = LeastSquareMethod(5)

    # 次の曲のbpmを決定
    if nowMusicBpmType == 3:
        if inclination < 0:
            nowMusicBpmType -= 2
    elif nowMusicBpmType == -1:
        if inclination > 0:
            nowMusicBpmType += 1  
    else:
        if inclination > 0.5:
            nowMusicBpmType += 1
        elif inclination < 0.5:
            nowMusicBpmType -= 1 
    

    # musicデータベースからmusicBpmTypeとジャンルが一致するmusicDataのlist
    musicIdListOfMusicBpmType = musicSiftAnd(musicData ,nowMusicBpmType, nowMusicGenre)
    if len(musicIdListOfMusicBpmType) == 0:
        musicIdListOfMusicBpmType = musicSiftOr(musicData ,nowMusicBpmType, nowMusicGenre)
    return musicIdListOfMusicBpmType[RandomNumber(len(musicIdListOfMusicBpmType))][0]

# データサイズ調整
def Adjustment(listA, listB):
    small = listA[0][0] - listB[0][0]
    big = listA[len(listA) - 1][0] - listB[len(listB) - 1][0]

    if small < 0: listA = listA[abs(small):]
    else: listB = listB[abs(small):]

    if big < 0: listB = listB[:len(listA)]
    else: listA = listA[:len(listB)]

    return listA, listB

# import math

# 補間値
def InterpolatedValue(dataA, dataB):
    return math.floor((dataB[1] - dataA[1]) / (dataB[0] - dataA[0]))

# データの穴埋め
def HoleFilling(listData):
    # 本来あるべき長さがあるか
    resultData = []
    print(listData[0][0])
    length = listData[len(listData) - 1][0] - listData[0][0]
    startLength = len(listData)
    if startLength < length:
        ID = listData[0][0]
        count = 0
        while ID < listData[len(listData) - 1][0]:
            if listData[count][0] == ID:
                resultData.append(listData[count])
                count += 1
            else:
                resultData.append([ID, listData[count + ID - listData[count][0]][1] + InterpolatedValue(listData[count], listData[count + 1])])

            ID += 1
  
    return resultData
      
# マッチング用リスト追加関数
def AscendingQuickSort(listData):

    if len(listData) < 2: 
        return listData
    head = listData[0][1]
    left = []
    middle = []
    right = []

    for data in listData:
        if data[1] < head: left.append(data)
        elif data[1] == head: middle.append(data)
        else: right.append(data)
    
    return AscendingQuickSort(left) + middle + AscendingQuickSort(right)

def sumData(listData):
    sumData = 0
    for data in listData:
        sumData += data[1]
    return sumData

# 基準値(小)を抽出
def GetStandardMin(listData, i):
    listSort = AscendingQuickSort(listData)
    minList = listSort[:i]
    return sum(minList) / len(minList)

### マッチング用関数

# マッチング用 データの正規化
def Normalization(listData):
    i = 0
    standard = GetStandardMin(listData, 5)
    normalizationList = []
    while i < len(listData):
        listData[i][1] = listData[i][1] - standard
        normalizationList.append(listData[i])
        i += 1
    
    return normalizationList

# マッチング用 値の差を抽出する関数
def HumanMatchingCheck(listA, listB):
    listA, listB = Adjustment(listA, listB)
    HoleFilling(listA)
    HoleFilling(listB)
    normalizationListA = Normalization(listA)
    normalizationListB = Normalization(listB)
    if len(normalizationListA) > len(normalizationListB):
        length = len(normalizationListB)
    else:
        length = len(normalizationListA)

    i = 0
    while i < length:
        result = abs(sum(normalizationListA) - sum(normalizationListB))
        i += 1

    return result

# マッチング用リスト追加関数
def MatchingListAdd(listData, data):
    if len(listData) < 1: 
        listData.append(data)
        return listData
    elif len(listData) < 5:
        i = 0
        while i < len(listData):
            if listData[i][1] > data[1]:
                listData.insert(i, data)
                return listData
            i += 1
        listData.append(data)
        return listData
    
    else:
        i = 0
        while i < len(listData):
            if listData[i][1] > data[1]:
                 listData.insert(i, data)
                 listData.pop(5)
                 return listData
            i += 1

    return listData

# マッチング度が高い人上位5人のIDを返す関数
def Humanmatching(idA, listA): # 変更時listBを引数から削除する idAは使用者のID
    # 宣言
    # i = 0
    # マッチング検査するデータ数
    # length = 10
    # idと心拍数の差を保存する配列
    matchingList = []

    # テスト用
    # idc = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    # di = [5, 4, 4, 8, 3, 1, 5, 0, 0, 1]

    ref = db.collection('bpm')
    docs = ref.stream()
    for doc in docs:
    # while i < length:
        data = doc.to_dict()
        # listB = listB
        idB = doc.id

        if idA == idB:
            continue

        # 心拍数の差を計算
        difference = HumanMatchingCheck(listA, data['BPM'])
        
        # 差が小さいIDを配列に格納
        matchingList = MatchingListAdd(matchingList, [idB, difference])
        # i += 1
    # 配列の上位5人を返す
    return matchingList[:5]


# ユーザ情報の登録
@app.route('/user', methods=['POST'])
# Firebaseへのデータ登録
def post_user_json():
    global num
    json_user = request.get_json()  # POSTされたJSONを取得
    age = json_user['age']
    sex = json_user['sex']
    twitterID = json_user['twitterID']

    userID = str(random.randint(0, 10000))

    new_ref = db.collection('users').document(str(userID))
    new_data = {
        'age': str(age),
        'sex': str(sex),
        'twitterID': str(twitterID)
    }
    new_ref.set(new_data)
    
    num += 1

# BPMの登録
@app.route('/bpm', methods=['POST'])

# Firebaseへのデータ登録
def post_firebase_json():
    now_datetime = datetime.now(pytz.timezone('Asia/Tokyo'))
    dif_datetime = ElapsedTime(timeChanger(now_datetime))
    dif_result = dif_datetime % 6
    json_data = request.get_json()  # POSTされたJSONを取得
    userID = json_data['userID']
    twitterID = json_data['twitterID']
    BPM = json_data['BPM']

    ref = db.collection('bpm')
    docs = ref.stream()
    judge = True
    for doc in docs:
        data = doc.to_dict()
        if doc.id == str(userID):
            global user_bpm
            if type(data['BPM']) is int:
                bpm = []
                bpm.append(data['BPM'])
                bpm.append(int(BPM))
                judge = False
                user_bpm = bpm
                break
            
            user_bpm = data['BPM']
            user_bpm.append(int(BPM))
            judge = False
            break
    
    if judge == True:
        user_bpm = int(BPM)

    docs = ref.stream()
    judge_time = True
    for doc in docs:
        data = doc.to_dict()
        if doc.id == str(userID):
            global bpm_time
            tmp_data = data['bpm_time']
            if type(tmp_data) is google.api_core.datetime_helpers.DatetimeWithNanoseconds:
                tmp = []
                tmp.append(tmp_data)
                tmp.append(datetime.now(pytz.timezone('Asia/Tokyo')))
                bpm_time = tmp
                judge_time = False
                break

            bpm_time = tmp_data
            bpm_time.append(datetime.now(pytz.timezone('Asia/Tokyo')))
            judge_time = False
            break
    
    if judge_time == True:
        bpm_time = datetime.now(pytz.timezone('Asia/Tokyo'))

    new_ref = db.collection('bpm').document(str(userID))
    
    new_ref.set({
        'BPM': user_bpm,
        'twitterID': twitterID,
        'bpm_time': bpm_time
    })

    result = Humanmatching(str(userID), user_bpm)
    result_human = []
    result_return = ''
    
    for i in result:
        result_human.append(i[0])

    docs = ref.stream()
    judge = True
    for doc in docs:
        data = doc.to_dict()
        for j in result_human:
            if str(j) == str(doc.id):
                result_return += str(data['twitterID']) + ', '

    if dif_result == 0:
        bpm_all = []
        docs = ref.stream()
        for doc in docs:
            data = doc.to_dict()
            BPM_data = data['BPM']
            bpm_all.append(BPM_data[len(BPM_data)-1])

        excite = GetExcitementForTime(bpm_all)

        new_ref = db.collection('excitement').document(now_datetime)
        new_ref.set({
            'excite': user_bpm,
            'time': now_datetime
        })
        
        db.collection("excitement").orderBy("time", "desc")

        ref_ex = db.collection("excitement")
        docs = ref_ex.stream()
        data_leng = []
        for doc in docs:
            data = doc.to_dict()
            ex_data = data['excitement']
            time_data = data['bpm_time']
            data_leng.appned([ex_data, time_data])
        LeastSquareMethod(data_leng)

        db.collection("choice_music").orderBy("time", "desc")
        ref_old = db.collection("choice_music")
        docs = ref_ex.stream()
        data = docs[0].to_dict()
        musicID_old = data['musicID']
        
        ref_ex = db.collection("music")
        docs = ref_ex.stream()
        data_leng = []
        for doc in docs:
            data = doc.to_dict()
            musicID = data['musicID']
            BPM = data['BPM']
            genre = data['genre']
            data_leng.append([musicID, BPM, genre])
        
        SelectMusic(musicID_old, data_leng)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # サーバを指定
        s.connect(('192.168.137.116', 12345))
        # サーバにメッセージを送る
        s.sendall(result_return)
    

if __name__ == '__main__':
    app.run(host='localhost', port=5000, threaded=True)
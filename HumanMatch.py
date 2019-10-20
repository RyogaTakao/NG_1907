test1 = []
i = 89
count = 0
while count < 50:
    if count > 10 and count < 20:
        i += 1 

    if count >= 20 and count < 35:
        i -= 1

    if count >= 45:
        i += 2

    if count != 22 and count != 30 and count != 31 and count != 32 and count != 49:test1.append([count, i])
    count += 1

print(test1)
print("\n")

test2 = []
i = 90
count = 5
while count < 20:
    if count > 8 and count < 22:
        i += 1 

    if count >= 25 and count < 35:
        i -= 1

    if count >= 40:
        i += 1

    test2.append([count, i])
    count += 1

# print(test2)
# print("\n")

# データサイズ調整
def Adjustment(listA, listB):
    small = listA[0][0] - listB[0][0]
    big = listA[len(listA) - 1][0] - listB[len(listB) - 1][0]

    if small < 0: listA = listA[abs(small):]
    else: listB = listB[abs(small):]

    if big < 0: listB = listB[:len(listA)]
    else: listA = listA[:len(listB)]

    return listA, listB

import math

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

print("HoleFilling")
print(HoleFilling(test1))                


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
    # print(listSort)
    minList = listSort[:i]
    return sumData(minList) / len(minList)

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
    print(listA)
    print(listB)
    normalizationListA = Normalization(listA)
    normalizationListB = Normalization(listB)
    if len(normalizationListA) > len(normalizationListB):
        length = len(normalizationListB)
    else:
        length = len(normalizationListA)

    i = 0
    while i < length:
        result = abs(sumData(normalizationListA) - sumData(normalizationListB))
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
def Humanmatching(idA, listA, listB): # 変更時listBを引数から削除する idAは使用者のID
    # 宣言
    i = 0
    # マッチング検査するデータ数
    length = 10
    # idと心拍数の差を保存する配列
    matchingList = []

    # # テスト用
    # idc = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    # di = [5, 4, 4, 8, 3, 1, 5, 0, 0, 1]

    while i < length:
        # listB = listB
        idB = 100

        # 心拍数の差を計算
        difference = HumanMatchingCheck(listA, listB)

        # # テスト用
        # difference = di[i]
        # idB = idc[i]
        
        # 差が小さいIDを配列に格納
        matchingList = MatchingListAdd(matchingList, [idB, difference])
        i += 1
    # 配列の上位5人を返す
    return matchingList[:5]

# print(GetExcitementPoint(test2))
# print("\n")

# print(HumanMatchingCheck(test1, test2))
# print("\n")

# print(Humanmatching(200, test1, test2))


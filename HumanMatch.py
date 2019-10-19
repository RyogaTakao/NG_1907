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

    test1.append(i)
    count += 1

print(test1)
print("\n")

test2 = []
i = 90
count = 0
while count < 50:
    if count > 8 and count < 22:
        i += 1 

    if count >= 25 and count < 35:
        i -= 1

    if count >= 40:
        i += 1

    test2.append(i)
    count += 1

print(test2)
print("\n")




# 基準値(小)を抽出
def GetStandardMin(listData, i):
    listSort = sorted(listData)
    minList = listSort[:i]
    return sum(minList) / len(minList)

### マッチング用関数 

# マッチング用 データの正規化
def Normalization(listData):
    i = 0
    standard = GetStandardMin(listData, 5)
    normalizationList = []
    while i < len(listData):
        normalizationList.append(listData[i] - standard)
        i += 1
    
    return normalizationList

# マッチング用 値の差を抽出する関数
def HumanMatchingCheck(listA, listB):
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
def Humanmatching(idA, listA, listB): # 変更時listBを引数から削除する idAは使用者のID
    # 宣言
    i = 0
    # マッチング検査するデータ数
    length = 10
    # idと心拍数の差を保存する配列
    matchingList = []

    # テスト用
    # idc = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    # di = [5, 4, 4, 8, 3, 1, 5, 0, 0, 1]

    while i < length:
        listB = listB
        idB = 100
        # 心拍数の差を計算
        difference = HumanMatchingCheck(listA, listB)

        # テスト用
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

# print(Humanmatching(test1, test2))
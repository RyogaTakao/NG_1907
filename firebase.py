import firebase_admin
from firebase_admin import credentials, firestore

cred =credentials.Certificate()
app = firebase_admin.initialize_app(cred)

db = firestore.client()

array = [[]]
array[0].append(1)
array[0].append(2)
array[0].append(3)
# firebaseに新規データを格納
new_ref = db.collection('bpm').document('0')
new_data = {
    'BPM': array[0],
    'musicID': 1
}
new_ref.set(new_data)
new_ref.update({'music': 1111})

# firebaseからデータ取り出し
ref = db.collection('bpm')
docs = ref.get()
for doc in docs:
    data = doc.to_dict()
    if doc.id == '0':
        print('BPM : {}'.format(data['BPM']))
        print('dif : {}'.format(data['music']))
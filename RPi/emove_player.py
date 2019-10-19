# import
import subprocess
import os
import sys
import time
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


# firebase
cred = credentials.Certificate("./serviceAccountKey.json")
firebase_admin.initialize_app(cred)


# define
OUTRO_TIME = 1
MUSIC_PATH = "/jphacks/music/"

def sound_play(path):
	os.system("mpg321 " + path + " &")

def sound_stop():
	os.system("killall mpg321")

# main
def main():
	next_m_path = "undecided"
	next_m_time = 0

	db = firestore.client()
	docs_c = db.collection('choice_music').get()

	for doc_c in docs_c:
		data_c = doc_c.to_dict()
		print(format(data_c['musicID']))
		# 楽曲情報の更新
		# prev_m_path=next_m_path
		# prev_m_time=next_m_path

		# 楽曲情報の取得
		docs_m = db.collection('music').get()
		for doc_m in docs_m:
			data_m = doc_m.to_dict()
			if format(data_c['musicID']) == format(data_m['musicID']):
				next_m_path=format(data_m['path'])
				next_m_time=format(data_m['time'])

		print(next_m_path)
		print(next_m_time)

		# 楽曲の再生
		sound_play(MUSIC_PATH+next_m_path)

		# 楽曲の再生中待機
		time.sleep(int(next_m_time)-OUTRO_TIME)


if __name__ == "__main__":
	main()

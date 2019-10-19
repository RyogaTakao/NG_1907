import emove_socket
import emove_json

JSON_FILE_PATH = '/home/pi/EMOVE/test_bpm.json'
SEND_URL = 'https://jphacks_noblesseoblige.serveo.net/bpm'

userID = '3120'
musicID = '7654'

def main():
    emove_socket.main()

if __name__ == "__main__":
    main()